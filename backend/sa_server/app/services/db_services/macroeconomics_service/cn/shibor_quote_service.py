import datetime
import pandas as pd
from typing import List, Optional, Union
from app.external.tushare_api.macroeconomics_api import get_shibor_quote
from app.data.db_modules.macroeconomics_modules.cn.shibor_quote import ShiborQuoteData


class ShiborQuoteService:
    """SHIBOR报价数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_shibor_quote_data(self, date: Optional[str] = None, 
                                      start_date: Optional[str] = None, 
                                      end_date: Optional[str] = None, 
                                      bank: Optional[str] = None,
                                      batch_size: int = 1000) -> int:
        """
        从Tushare获取SHIBOR报价数据并高效导入数据库
        
        参数:
            date: 可选，指定日期，格式为YYYYMMDD
            start_date: 可选，开始日期，格式为YYYYMMDD
            end_date: 可选，结束日期，格式为YYYYMMDD
            bank: 可选，银行名称（中文名称，例如 农业银行）
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_shibor_quote(date=date, start_date=start_date, 
                                    end_date=end_date, bank=bank)
        
        if df_result is None or df_result.empty:
            print(f"未找到SHIBOR报价数据: date={date}, start_date={start_date}, end_date={end_date}, bank={bank}")
            return 0
        
        # 标准化列名（从API返回的列名转换为数据库列名）
        column_mapping = {
            'date': 'date',
            'bank': 'bank',
            'on_b': 'on_b',
            'on_a': 'on_a',
            '1w_b': 'w1_b',
            '1w_a': 'w1_a',
            '2w_b': 'w2_b',
            '2w_a': 'w2_a',
            '1m_b': 'm1_b',
            '1m_a': 'm1_a',
            '3m_b': 'm3_b',
            '3m_a': 'm3_a',
            '6m_b': 'm6_b',
            '6m_a': 'm6_a',
            '9m_b': 'm9_b',
            '9m_a': 'm9_a',
            '1y_b': 'y1_b',
            '1y_a': 'y1_a'
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
                # 将批次数据转换为ShiborQuoteData对象
                quote_data_list = []
                for record in batch:
                    try:
                        quote_data = ShiborQuoteData(**record)
                        quote_data_list.append(quote_data)
                    except Exception as e:
                        date_str = record.get('date', '未知')
                        bank_name = record.get('bank', '未知')
                        print(f"创建ShiborQuoteData对象失败 日期:{date_str}, 银行:{bank_name}: {str(e)}")
                
                # 使用COPY命令批量导入
                if quote_data_list:
                    inserted = await self.batch_upsert_quotes(quote_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_quotes(self, quote_list: List[ShiborQuoteData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            quote_list: 要插入或更新的SHIBOR报价数据列表
            
        返回:
            处理的记录数
        """
        if not quote_list:
            return 0
        
        # 获取字段列表
        columns = list(quote_list[0].model_dump().keys())
        
        # 准备数据
        records = []
        for quote in quote_list:
            quote_dict = quote.model_dump()
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = quote_dict[col]
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
                    await conn.execute('CREATE TEMP TABLE temp_shibor_quote (LIKE shibor_quote) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_shibor_quote', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（除了主键外的所有字段）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ('date', 'bank')]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO shibor_quote 
                        SELECT * FROM temp_shibor_quote
                        ON CONFLICT (date, bank) DO UPDATE SET {update_clause}
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


# 快捷函数，用于导入特定日期的SHIBOR报价数据
async def import_shibor_quote_by_date(db, date: Union[str, datetime.date]) -> int:
    """
    导入特定日期的SHIBOR报价数据
    
    参数:
        db: 数据库连接对象
        date: 日期，可以是字符串格式YYYYMMDD或datetime.date对象
        
    返回:
        导入的记录数
    """
    # 将datetime.date对象转换为YYYYMMDD格式字符串
    if isinstance(date, datetime.date):
        date_str = date.strftime('%Y%m%d')
    else:
        date_str = date
    
    service = ShiborQuoteService(db)
    count = await service.import_shibor_quote_data(date=date_str)
    print(f"成功导入 {count} 条 {date_str} 日期的SHIBOR报价记录")
    return count


# 快捷函数，用于导入日期范围内的SHIBOR报价数据
async def import_shibor_quote_by_date_range(db, start_date: Union[str, datetime.date], 
                                          end_date: Union[str, datetime.date]) -> int:
    """
    导入日期范围内的SHIBOR报价数据
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期，可以是字符串格式YYYYMMDD或datetime.date对象
        end_date: 结束日期，可以是字符串格式YYYYMMDD或datetime.date对象
        
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
    
    service = ShiborQuoteService(db)
    count = await service.import_shibor_quote_data(start_date=start_date_str, end_date=end_date_str)
    print(f"成功导入 {count} 条 {start_date_str} 至 {end_date_str} 日期范围内的SHIBOR报价记录")
    return count


# 快捷函数，用于导入特定银行的SHIBOR报价数据
async def import_shibor_quote_by_bank(db, bank: str, start_date: Optional[Union[str, datetime.date]] = None, 
                                    end_date: Optional[Union[str, datetime.date]] = None) -> int:
    """
    导入特定银行的SHIBOR报价数据
    
    参数:
        db: 数据库连接对象
        bank: 银行名称（中文名称，例如 农业银行）
        start_date: 可选，开始日期，可以是字符串格式YYYYMMDD或datetime.date对象
        end_date: 可选，结束日期，可以是字符串格式YYYYMMDD或datetime.date对象
        
    返回:
        导入的记录数
    """
    # 将datetime.date对象转换为YYYYMMDD格式字符串
    start_date_str = None
    if start_date:
        if isinstance(start_date, datetime.date):
            start_date_str = start_date.strftime('%Y%m%d')
        else:
            start_date_str = start_date
    
    end_date_str = None
    if end_date:
        if isinstance(end_date, datetime.date):
            end_date_str = end_date.strftime('%Y%m%d')
        else:
            end_date_str = end_date
    
    service = ShiborQuoteService(db)
    count = await service.import_shibor_quote_data(bank=bank, start_date=start_date_str, end_date=end_date_str)
    
    date_info = ""
    if start_date_str and end_date_str:
        date_info = f"日期范围 {start_date_str} 至 {end_date_str} 内"
    elif start_date_str:
        date_info = f"从 {start_date_str} 开始"
    elif end_date_str:
        date_info = f"截至 {end_date_str}"
    
    print(f"成功导入 {count} 条{bank}{date_info}的SHIBOR报价记录")
    return count


# 快捷函数，导入最新一天的SHIBOR报价数据
async def import_latest_shibor_quote(db) -> int:
    """
    导入最新一天的SHIBOR报价数据
    
    参数:
        db: 数据库连接对象
        
    返回:
        导入的记录数
    """
    # 获取当前日期的YYYYMMDD格式字符串
    today = datetime.date.today()
    date_str = today.strftime('%Y%m%d')
    
    service = ShiborQuoteService(db)
    count = await service.import_shibor_quote_data(date=date_str)
    
    if count > 0:
        print(f"成功导入 {count} 条 {date_str} 日期的最新SHIBOR报价记录")
    else:
        # 如果当天没有数据，尝试获取前一天的数据
        yesterday = today - datetime.timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y%m%d')
        count = await service.import_shibor_quote_data(date=yesterday_str)
        print(f"当天无数据，成功导入 {count} 条 {yesterday_str} 日期的SHIBOR报价记录")
    
    return count


# 快捷函数，导入最近N天的SHIBOR报价数据
async def import_recent_shibor_quote(db, days: int = 30) -> int:
    """
    导入最近N天的SHIBOR报价数据
    
    参数:
        db: 数据库连接对象
        days: 天数，默认30天
        
    返回:
        导入的记录数
    """
    # 计算开始日期和结束日期
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days-1)  # 减一是因为包含当天
    
    # 格式化为YYYYMMDD格式字符串
    start_date_str = start_date.strftime('%Y%m%d')
    end_date_str = end_date.strftime('%Y%m%d')
    
    service = ShiborQuoteService(db)
    count = await service.import_shibor_quote_data(start_date=start_date_str, end_date=end_date_str)
    print(f"成功导入 {count} 条最近 {days} 天的SHIBOR报价记录")
    return count


# 快捷函数，导入所有历史SHIBOR报价数据
async def import_all_historical_shibor_quote(db, batch_size: int = 1000) -> int:
    """
    导入所有历史SHIBOR报价数据，注意这可能花费较长时间
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = ShiborQuoteService(db)
    # 不指定日期参数，将获取所有历史数据
    count = await service.import_shibor_quote_data(batch_size=batch_size)
    print(f"成功导入 {count} 条历史SHIBOR报价记录")
    return count