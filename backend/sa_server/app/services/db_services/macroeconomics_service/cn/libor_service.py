import datetime
import pandas as pd
from typing import List, Optional, Union
from app.external.tushare_api.macroeconomics_api import get_libor
from app.data.db_modules.macroeconomics_modules.cn.libor import LiborData


class LiborService:
    """LIBOR数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_libor_data(self, date: Optional[str] = None, 
                              start_date: Optional[str] = None, 
                              end_date: Optional[str] = None, 
                              curr_type: Optional[str] = None,
                              batch_size: int = 1000) -> int:
        """
        从Tushare获取LIBOR数据并高效导入数据库
        
        参数:
            date: 可选，指定日期，格式为YYYYMMDD
            start_date: 可选，开始日期，格式为YYYYMMDD
            end_date: 可选，结束日期，格式为YYYYMMDD
            curr_type: 可选，货币类型 (USD美元 EUR欧元 JPY日元 GBP英镑 CHF瑞郎，默认是USD)
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_libor(date=date, start_date=start_date, 
                             end_date=end_date, curr_type=curr_type)
        
        if df_result is None or df_result.empty:
            print(f"未找到LIBOR数据: date={date}, start_date={start_date}, end_date={end_date}, curr_type={curr_type}")
            return 0
        
        # 标准化列名（从API返回的列名转换为数据库列名）
        column_mapping = {
            'date': 'date',
            'curr_type': 'curr_type',
            'on': 'on_rate',
            '1w': 'w1_rate',
            '1m': 'm1_rate',
            '2m': 'm2_rate',
            '3m': 'm3_rate',
            '6m': 'm6_rate',
            '12m': 'm12_rate'
        }
        
        # 重命名列
        df_renamed = df_result.rename(columns=column_mapping)
        
        # 转换为列表并处理可能的NaN值
        records = df_renamed.replace({pd.NA: None}).to_dict('records')
        
        # 分批处理
        batches = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为LiborData对象
                libor_data_list = []
                for record in batch:
                    try:
                        libor_data = LiborData(**record)
                        libor_data_list.append(libor_data)
                    except Exception as e:
                        date_str = record.get('date', '未知')
                        currency = record.get('curr_type', '未知')
                        print(f"创建LiborData对象失败 日期:{date_str}, 货币:{currency}: {str(e)}")
                
                # 使用COPY命令批量导入
                if libor_data_list:
                    inserted = await self.batch_upsert_libor(libor_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_libor(self, libor_list: List[LiborData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            libor_list: 要插入或更新的LIBOR数据列表
            
        返回:
            处理的记录数
        """
        if not libor_list:
            return 0
        
        # 获取字段列表
        columns = list(libor_list[0].model_dump().keys())
        
        # 准备数据
        records = []
        for libor in libor_list:
            libor_dict = libor.model_dump()
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = libor_dict[col]
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
                    await conn.execute('CREATE TEMP TABLE temp_libor (LIKE libor) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_libor', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（除了主键外的所有字段）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ('date', 'curr_type')]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO libor 
                        SELECT * FROM temp_libor
                        ON CONFLICT (date, curr_type) DO UPDATE SET {update_clause}
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


# 快捷函数，用于导入特定日期的LIBOR数据
async def import_libor_by_date(db, date: Union[str, datetime.date], 
                              curr_type: Optional[str] = None) -> int:
    """
    导入特定日期的LIBOR数据
    
    参数:
        db: 数据库连接对象
        date: 日期，可以是字符串格式YYYYMMDD或datetime.date对象
        curr_type: 可选，货币类型 (USD美元 EUR欧元 JPY日元 GBP英镑 CHF瑞郎)
        
    返回:
        导入的记录数
    """
    # 将datetime.date对象转换为YYYYMMDD格式字符串
    if isinstance(date, datetime.date):
        date_str = date.strftime('%Y%m%d')
    else:
        date_str = date
    
    service = LiborService(db)
    count = await service.import_libor_data(date=date_str, curr_type=curr_type)
    
    currency_info = f"，货币类型: {curr_type}" if curr_type else ""
    print(f"成功导入 {count} 条 {date_str} 日期的LIBOR记录{currency_info}")
    return count


# 快捷函数，用于导入日期范围内的LIBOR数据
async def import_libor_by_date_range(db, start_date: Union[str, datetime.date], 
                                   end_date: Union[str, datetime.date],
                                   curr_type: Optional[str] = None) -> int:
    """
    导入日期范围内的LIBOR数据
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期，可以是字符串格式YYYYMMDD或datetime.date对象
        end_date: 结束日期，可以是字符串格式YYYYMMDD或datetime.date对象
        curr_type: 可选，货币类型 (USD美元 EUR欧元 JPY日元 GBP英镑 CHF瑞郎)
        
    返回:
        导入的记录数
    """
    # 将datetime.date对象转换为YYYYMMDD格式字符串
    if isinstance(start_date, datetime.date):
        start_date_str = start_date.strftime('%Y%m%d')
    else:
        start_date_str = start_date
    
    if isinstance(end_date, datetime.date):
        end_date_str = end_date.strftime('%Y%m%d')
    else:
        end_date_str = end_date
    
    service = LiborService(db)
    count = await service.import_libor_data(start_date=start_date_str, end_date=end_date_str, curr_type=curr_type)
    
    currency_info = f"，货币类型: {curr_type}" if curr_type else ""
    print(f"成功导入 {count} 条 {start_date_str} 至 {end_date_str} 日期范围内的LIBOR记录{currency_info}")
    return count


# 快捷函数，用于导入特定货币类型的所有LIBOR数据
async def import_libor_by_currency(db, curr_type: str) -> int:
    """
    导入特定货币类型的所有LIBOR数据
    
    参数:
        db: 数据库连接对象
        curr_type: 货币类型 (USD美元 EUR欧元 JPY日元 GBP英镑 CHF瑞郎)
        
    返回:
        导入的记录数
    """
    service = LiborService(db)
    count = await service.import_libor_data(curr_type=curr_type)
    print(f"成功导入 {count} 条 {curr_type} 货币类型的LIBOR记录")
    return count


# 快捷函数，导入最新一天的LIBOR数据
async def import_latest_libor(db, curr_type: Optional[str] = None) -> int:
    """
    导入最新一天的LIBOR数据
    
    参数:
        db: 数据库连接对象
        curr_type: 可选，货币类型 (USD美元 EUR欧元 JPY日元 GBP英镑 CHF瑞郎)
        
    返回:
        导入的记录数
    """
    # 获取当前日期的YYYYMMDD格式字符串
    today = datetime.date.today()
    date_str = today.strftime('%Y%m%d')
    
    service = LiborService(db)
    count = await service.import_libor_data(date=date_str, curr_type=curr_type)
    
    currency_info = f"，货币类型: {curr_type}" if curr_type else ""
    
    if count > 0:
        print(f"成功导入 {count} 条 {date_str} 日期的最新LIBOR记录{currency_info}")
    else:
        # 如果当天没有数据，尝试获取前一天的数据
        yesterday = today - datetime.timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y%m%d')
        count = await service.import_libor_data(date=yesterday_str, curr_type=curr_type)
        print(f"当天无数据，成功导入 {count} 条 {yesterday_str} 日期的LIBOR记录{currency_info}")
    
    return count


# 快捷函数，导入最近N天的LIBOR数据
async def import_recent_libor(db, days: int = 30, curr_type: Optional[str] = None) -> int:
    """
    导入最近N天的LIBOR数据
    
    参数:
        db: 数据库连接对象
        days: 天数，默认30天
        curr_type: 可选，货币类型 (USD美元 EUR欧元 JPY日元 GBP英镑 CHF瑞郎)
        
    返回:
        导入的记录数
    """
    # 计算开始日期和结束日期
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days-1)  # 减一是因为包含当天
    
    # 格式化为YYYYMMDD格式字符串
    start_date_str = start_date.strftime('%Y%m%d')
    end_date_str = end_date.strftime('%Y%m%d')
    
    service = LiborService(db)
    count = await service.import_libor_data(start_date=start_date_str, end_date=end_date_str, curr_type=curr_type)
    
    currency_info = f"，货币类型: {curr_type}" if curr_type else ""
    print(f"成功导入 {count} 条最近 {days} 天的LIBOR记录{currency_info}")
    return count


# 快捷函数，导入所有历史LIBOR数据
async def import_all_historical_libor(db, batch_size: int = 1000) -> int:
    """
    导入所有历史LIBOR数据，注意这可能花费较长时间
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = LiborService(db)
    # 不指定日期参数，将获取所有历史数据
    count = await service.import_libor_data(batch_size=batch_size)
    print(f"成功导入 {count} 条历史LIBOR记录")
    return count


# 快捷函数，导入所有货币类型的LIBOR数据
async def import_all_currencies_libor(db) -> dict:
    """
    分别导入所有货币类型(USD, EUR, JPY, GBP, CHF)的LIBOR数据
    
    参数:
        db: 数据库连接对象
        
    返回:
        dict: 各货币类型导入的记录数统计
    """
    currencies = ['USD', 'EUR', 'JPY', 'GBP', 'CHF']
    result = {}
    
    for curr in currencies:
        count = await import_libor_by_currency(db, curr)
        result[curr] = count
    
    total = sum(result.values())
    print(f"成功导入所有货币类型的LIBOR数据，总计 {total} 条记录")
    return result