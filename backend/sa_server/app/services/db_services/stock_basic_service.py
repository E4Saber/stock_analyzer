import pandas as pd
import datetime
from typing import List, Dict, Any, Optional
from app.data.db_modules.stock_basic import StockBasicData
from app.schedule.tasks.tushare.stock_basic_info_task import get_stock_basic


class StockBasicService:
    """股票数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_stock_data(self, ts_code: Optional[str] = None, batch_size: int = 1000) -> int:
        """
        从Tushare获取股票数据并高效导入数据库
        
        参数:
            ts_code: 可选，指定要导入的股票代码，为None时导入所有股票
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_stock_basic(ts_code=ts_code)
        
        if df_result is None or df_result.empty:
            print(f"未找到股票数据: {ts_code}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 定义必填字段及默认值
        required_fields = {
            'ts_code': '',
            'symbol': '',
            'name': '',
            'area': '未知',
            'industry': '未知',
            'cnspell': '',
            'market': '未知',
            'list_date': None,  # 修改为None而不是空字符串
            'act_name': '未知',
            'act_ent_type': '未知'
        }
        
        # 处理数据并确保所有必填字段都有值
        valid_records = []
        for record in records:
            for field, default_value in required_fields.items():
                if field not in record or record[field] is None or (isinstance(record[field], str) and record[field] == ''):
                    record[field] = default_value
            valid_records.append(record)
        
        # 分批处理
        batches = [valid_records[i:i + batch_size] for i in range(0, len(valid_records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为StockBasicData对象
                stock_data_list = []
                for record in batch:
                    try:
                        stock_data = StockBasicData(**record)
                        stock_data_list.append(stock_data)
                    except Exception as e:
                        print(f"创建StockBasicData对象失败 {record.get('ts_code', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if stock_data_list:
                    inserted = await self.batch_upsert_stocks(stock_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_stocks(self, stock_list: List[StockBasicData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            stock_list: 要插入或更新的股票数据列表
            
        返回:
            处理的记录数
        """
        if not stock_list:
            return 0
        
        # 获取字段列表
        columns = list(stock_list[0].model_dump().keys())
        
        # 准备数据
        records = []
        for stock in stock_list:
            stock_dict = stock.model_dump()
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = stock_dict[col]
                # 对于None值，使用PostgreSQL的NULL而不是空字符串
                if val is None:
                    record.append(None)
                # 确保日期对象正确处理
                # elif isinstance(val, (datetime.date, datetime.datetime)):
                #     record.append(val.isoformat())
                else:
                    record.append(val)
            records.append(record)
        
        # 使用COPY命令批量导入数据
        async with self.db.pool.acquire() as conn:
            try:
                # 开始事务
                async with conn.transaction():
                    # 创建临时表，结构与目标表相同
                    await conn.execute('CREATE TEMP TABLE temp_stock_basic (LIKE stock_basic) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_stock_basic', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（除了主键外的所有字段）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col != 'ts_code']
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO stock_basic 
                        SELECT * FROM temp_stock_basic
                        ON CONFLICT (ts_code) DO UPDATE SET {update_clause}
                    ''')
                    
                    # 解析结果获取处理的记录数
                    # 结果格式类似于 "INSERT 0 50"
                    parts = result.split()
                    if len(parts) >= 3:
                        count = int(parts[2])
                    else:
                        count = len(records)  # 如果无法解析，假定全部成功
                    
                    return count
                    
            except Exception as e:
                print(f"批量导入过程中发生错误: {str(e)}")
                raise


# 快捷函数，用于导入所有股票数据
async def import_all_stocks(db, batch_size: int = 1000):
    """
    导入所有股票基础数据
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StockBasicService(db)
    count = await service.import_stock_data(batch_size=batch_size)
    print(f"成功导入 {count} 条股票记录")
    return count


# 快捷函数，用于导入单个股票数据
async def import_single_stock(db, ts_code: str):
    """
    导入单个股票基础数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        
    返回:
        是否成功导入
    """
    service = StockBasicService(db)
    count = await service.import_stock_data(ts_code)
    return count > 0