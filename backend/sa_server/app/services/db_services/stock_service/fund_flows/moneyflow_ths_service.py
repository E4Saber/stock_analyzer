import pandas as pd
from typing import List, Optional
from app.external.tushare_api.fund_flows_api import get_moneyflow_ths
from app.data.db_modules.stock_modules.fund_flows.moneyflow_ths import MoneyflowThsData

class MoneyflowThsService:
    """同花顺股票资金流向数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_moneyflow_ths_data(self, ts_code: Optional[str] = None, 
                                      trade_date: Optional[str] = None,
                                      start_date: Optional[str] = None, 
                                      end_date: Optional[str] = None,
                                      batch_size: int = 1000) -> int:
        """
        从Tushare获取同花顺股票资金流向数据并高效导入数据库
        
        参数:
            ts_code: 可选，指定要导入的股票代码，为None时导入所有股票
            trade_date: 可选，交易日期 YYYYMMDD格式
            start_date: 可选，开始日期 YYYYMMDD格式
            end_date: 可选，结束日期 YYYYMMDD格式
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_moneyflow_ths(ts_code=ts_code, trade_date=trade_date, 
                                        start_date=start_date, end_date=end_date)
        
        if df_result is None or df_result.empty:
            print(f"未找到同花顺资金流向数据: ts_code={ts_code}, trade_date={trade_date}, start_date={start_date}, end_date={end_date}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 分批处理
        batches = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为MoneyflowThsData对象
                moneyflow_data_list = []
                for record in batch:
                    try:
                        moneyflow_data = MoneyflowThsData(**record)
                        moneyflow_data_list.append(moneyflow_data)
                    except Exception as e:
                        print(f"创建MoneyflowThsData对象失败 {record.get('ts_code', '未知')}-{record.get('trade_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if moneyflow_data_list:
                    inserted = await self.batch_upsert_moneyflow_ths(moneyflow_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_moneyflow_ths(self, moneyflow_list: List[MoneyflowThsData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            moneyflow_list: 要插入或更新的同花顺资金流向数据列表
            
        返回:
            处理的记录数
        """
        if not moneyflow_list:
            return 0
        
        # 获取字段列表
        columns = list(moneyflow_list[0].model_dump().keys())
        
        # 准备数据
        records = []
        for moneyflow in moneyflow_list:
            moneyflow_dict = moneyflow.model_dump()
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = moneyflow_dict[col]
                # 对于None值，使用PostgreSQL的NULL而不是空字符串
                if val is None:
                    record.append(None)
                else:
                    record.append(val)
            records.append(record)
        
        # 使用COPY命令批量导入数据
        async with self.db.pool.acquire() as conn:
            try:
                # 开始事务
                async with conn.transaction():
                    # 创建临时表，结构与目标表相同
                    await conn.execute('CREATE TEMP TABLE temp_moneyflow_ths (LIKE moneyflow_ths) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_moneyflow_ths', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（除了复合主键外的所有字段）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ('ts_code', 'trade_date')]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO moneyflow_ths 
                        SELECT * FROM temp_moneyflow_ths
                        ON CONFLICT (ts_code, trade_date) DO UPDATE SET {update_clause}
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


# 快捷函数，用于导入单日所有股票的资金流向数据
async def import_daily_moneyflow_ths(db, trade_date: str, batch_size: int = 1000):
    """
    导入指定交易日所有股票的同花顺资金流向数据
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期，YYYYMMDD格式
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = MoneyflowThsService(db)
    count = await service.import_moneyflow_ths_data(trade_date=trade_date, batch_size=batch_size)
    print(f"成功导入 {count} 条 {trade_date} 日同花顺资金流向记录")
    return count


# 快捷函数，用于导入日期范围内的资金流向数据
async def import_date_range_moneyflow_ths(db, start_date: str, end_date: str, batch_size: int = 1000):
    """
    导入日期范围内的同花顺资金流向数据
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期，YYYYMMDD格式
        end_date: 结束日期，YYYYMMDD格式
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = MoneyflowThsService(db)
    count = await service.import_moneyflow_ths_data(start_date=start_date, end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条 {start_date} 至 {end_date} 期间同花顺资金流向记录")
    return count


# 快捷函数，用于导入单个股票的资金流向数据
async def import_stock_moneyflow_ths(db, ts_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    导入单个股票的同花顺资金流向数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        start_date: 可选，开始日期，YYYYMMDD格式
        end_date: 可选，结束日期，YYYYMMDD格式
        
    返回:
        导入的记录数
    """
    service = MoneyflowThsService(db)
    count = await service.import_moneyflow_ths_data(ts_code=ts_code, start_date=start_date, end_date=end_date)
    date_range = ""
    if start_date and end_date:
        date_range = f" {start_date} 至 {end_date} 期间"
    elif start_date:
        date_range = f" {start_date} 之后"
    elif end_date:
        date_range = f" {end_date} 之前"
    print(f"成功导入 {count} 条{ts_code}{date_range}同花顺资金流向记录")
    return count