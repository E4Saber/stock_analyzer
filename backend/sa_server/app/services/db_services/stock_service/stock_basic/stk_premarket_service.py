import datetime
import pandas as pd
from typing import List, Optional, Union
from app.external.tushare_api.stock_info_api import get_stk_premarket
from app.data.db_modules.stock_modules.stock_basic.stk_premarket import StkPremarketData


class StkPremarketService:
    """股票盘前数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_premarket_data(self, 
                                   trade_date: Optional[Union[str, datetime.date]] = None, 
                                   ts_code: Optional[str] = None,
                                   start_date: Optional[str] = None,
                                   end_date: Optional[str] = None,
                                   batch_size: int = 1000) -> int:
        """
        从Tushare获取股票盘前数据并高效导入数据库
        
        参数:
            trade_date: 可选，指定要导入的交易日期
            ts_code: 可选，指定要导入的股票代码
            start_date: 可选，开始日期，格式YYYYMMDD
            end_date: 可选，结束日期，格式YYYYMMDD
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 至少需要提供一个查询参数
        if not any([trade_date, ts_code, start_date, end_date]):
            print("必须提供至少一个查询参数: trade_date、ts_code、start_date 或 end_date")
            return 0
            
        # 处理日期参数，转换为字符串格式
        trade_date_str = None
        if trade_date:
            if isinstance(trade_date, datetime.date):
                trade_date_str = trade_date.strftime('%Y%m%d')
            elif isinstance(trade_date, str):
                # 如果已经是字符串，验证格式
                if len(trade_date) == 8 and trade_date.isdigit():
                    trade_date_str = trade_date
                else:
                    try:
                        # 尝试 ISO 格式转换
                        date_obj = datetime.date.fromisoformat(trade_date)
                        trade_date_str = date_obj.strftime('%Y%m%d')
                    except ValueError:
                        print(f"无效的日期格式: {trade_date}")
                        return 0
            else:
                print(f"不支持的日期类型: {type(trade_date)}")
                return 0
        
        # 日期范围参数验证
        if start_date and not (len(start_date) == 8 and start_date.isdigit()):
            print(f"无效的开始日期格式: {start_date}，应为YYYYMMDD")
            return 0
            
        if end_date and not (len(end_date) == 8 and end_date.isdigit()):
            print(f"无效的结束日期格式: {end_date}，应为YYYYMMDD")
            return 0
            
        # 从Tushare获取数据
        df_result = get_stk_premarket(
            ts_code=ts_code,
            trade_date=trade_date_str,
            start_date=start_date,
            end_date=end_date
        )
        
        if df_result is None or df_result.empty:
            query_params = []
            if ts_code:
                query_params.append(f"ts_code={ts_code}")
            if trade_date_str:
                query_params.append(f"trade_date={trade_date_str}")
            if start_date:
                query_params.append(f"start_date={start_date}")
            if end_date:
                query_params.append(f"end_date={end_date}")
                
            params_str = ", ".join(query_params) if query_params else "所有条件"
            print(f"未找到盘前数据: {params_str}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 分批处理
        batches = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为StkPremarketData对象
                premarket_data_list = []
                for record in batch:
                    try:
                        premarket_data = StkPremarketData(**record)
                        premarket_data_list.append(premarket_data)
                    except Exception as e:
                        print(f"创建StkPremarketData对象失败 {record.get('ts_code', '未知')}, {record.get('trade_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if premarket_data_list:
                    inserted = await self.batch_upsert_premarket(premarket_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_premarket(self, premarket_list: List[StkPremarketData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            premarket_list: 要插入或更新的盘前数据列表
            
        返回:
            处理的记录数
        """
        if not premarket_list:
            return 0
        
        # 获取字段列表
        columns = list(premarket_list[0].model_dump().keys())
        
        # 准备数据
        records = []
        for premarket in premarket_list:
            premarket_dict = premarket.model_dump()
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = premarket_dict[col]
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
                    await conn.execute('CREATE TEMP TABLE temp_stk_premarket (LIKE stk_premarket) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_stk_premarket', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（除了主键外的所有字段）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ('trade_date', 'ts_code')]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO stk_premarket 
                        SELECT * FROM temp_stk_premarket
                        ON CONFLICT (trade_date, ts_code) DO UPDATE SET {update_clause}
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


# 快捷函数，用于导入指定日期的所有股票盘前数据
async def import_premarket_by_date(db, trade_date: Union[str, datetime.date], batch_size: int = 1000) -> int:
    """
    导入指定日期的所有股票盘前数据
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StkPremarketService(db)
    count = await service.import_premarket_data(trade_date=trade_date, batch_size=batch_size)
    print(f"成功导入 {count} 条 {trade_date} 的盘前数据记录")
    return count


# 快捷函数，用于导入指定股票的所有盘前数据历史
async def import_premarket_by_stock(db, ts_code: str, batch_size: int = 1000) -> int:
    """
    导入指定股票的所有盘前数据历史
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StkPremarketService(db)
    count = await service.import_premarket_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条 {ts_code} 的盘前数据记录")
    return count


# 快捷函数，用于导入指定日期指定股票的盘前数据
async def import_single_premarket(db, trade_date: Union[str, datetime.date], ts_code: str) -> bool:
    """
    导入指定日期指定股票的盘前数据
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期
        ts_code: 股票TS代码
        
    返回:
        是否成功导入
    """
    service = StkPremarketService(db)
    count = await service.import_premarket_data(trade_date=trade_date, ts_code=ts_code)
    return count > 0


# 快捷函数，用于按日期范围导入盘前数据
async def import_premarket_by_date_range(db, start_date: str, end_date: str, batch_size: int = 1000) -> int:
    """
    按日期范围导入盘前数据
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期，格式YYYYMMDD
        end_date: 结束日期，格式YYYYMMDD
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StkPremarketService(db)
    count = await service.import_premarket_data(start_date=start_date, end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条日期范围为 {start_date} 至 {end_date} 的盘前数据记录")
    return count