import datetime
import pandas as pd
from typing import List, Optional, Union, Set
from app.external.tushare_api.macroeconomics_api import get_us_tbr
from app.data.db_modules.macroeconomics_modules.us.us_tbr import UsTbrData


class UsTbrService:
    """美国国库券利率数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_us_tbr_data(self, date: Optional[str] = None, 
                              start_date: Optional[str] = None, 
                              end_date: Optional[str] = None,
                              fields: Optional[str] = None,
                              batch_size: int = 1000) -> int:
        """
        从Tushare获取美国国库券利率数据并高效导入数据库
        
        参数:
            date: 可选，指定日期，格式为YYYYMMDD
            start_date: 可选，开始日期，格式为YYYYMMDD
            end_date: 可选，结束日期，格式为YYYYMMDD
            fields: 可选，指定字段(e.g. fields='w4_bd,w52_ce')
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_us_tbr(date=date, start_date=start_date, end_date=end_date, fields=fields)
        
        if df_result is None or df_result.empty:
            print(f"未找到美国国库券利率数据: date={date}, start_date={start_date}, end_date={end_date}, fields={fields}")
            return 0
        
        # 确保date列存在
        if 'date' not in df_result.columns:
            print("获取的数据中缺少date列")
            return 0
        
        # 标准化列名（确保所有可能的列都存在）
        expected_columns = {
            'date', 'w4_bd', 'w4_ce', 'w8_bd', 'w8_ce', 'w13_bd', 'w13_ce', 
            'w17_bd', 'w17_ce', 'w26_bd', 'w26_ce', 'w52_bd', 'w52_ce'
        }
        
        # 确保所有期望的列都存在（使用None填充缺失的列）
        for col in expected_columns:
            if col not in df_result.columns:
                df_result[col] = None
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 分批处理
        batches = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为UsTbrData对象
                tbr_data_list = []
                for record in batch:
                    try:
                        tbr_data = UsTbrData(**record)
                        tbr_data_list.append(tbr_data)
                    except Exception as e:
                        date_str = record.get('date', '未知')
                        print(f"创建UsTbrData对象失败 日期:{date_str}: {str(e)}")
                
                # 使用COPY命令批量导入
                if tbr_data_list:
                    inserted = await self.batch_upsert_us_tbr(tbr_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_us_tbr(self, tbr_list: List[UsTbrData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            tbr_list: 要插入或更新的美国国库券利率数据列表
            
        返回:
            处理的记录数
        """
        if not tbr_list:
            return 0
        
        # 获取字段列表
        columns = list(tbr_list[0].model_dump().keys())
        
        # 准备数据
        records = []
        for tbr in tbr_list:
            tbr_dict = tbr.model_dump()
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = tbr_dict[col]
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
                    await conn.execute('CREATE TEMP TABLE temp_us_tbr (LIKE us_tbr) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_us_tbr', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（除了主键外的所有字段）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col != 'date']
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO us_tbr 
                        SELECT * FROM temp_us_tbr
                        ON CONFLICT (date) DO UPDATE SET {update_clause}
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


# 快捷函数，用于导入特定日期的美国国库券利率数据
async def import_us_tbr_by_date(db, date: Union[str, datetime.date], fields: Optional[str] = None) -> int:
    """
    导入特定日期的美国国库券利率数据
    
    参数:
        db: 数据库连接对象
        date: 日期，可以是字符串格式YYYYMMDD或datetime.date对象
        fields: 可选，指定字段(e.g. fields='w4_bd,w52_ce')
        
    返回:
        导入的记录数
    """
    # 将datetime.date对象转换为YYYYMMDD格式字符串
    if isinstance(date, datetime.date):
        date_str = date.strftime('%Y%m%d')
    else:
        date_str = date
    
    service = UsTbrService(db)
    count = await service.import_us_tbr_data(date=date_str, fields=fields)
    
    fields_info = f"，字段: {fields}" if fields else ""
    print(f"成功导入 {count} 条 {date_str} 日期的美国国库券利率记录{fields_info}")
    return count


# 快捷函数，用于导入日期范围内的美国国库券利率数据
async def import_us_tbr_by_date_range(db, start_date: Union[str, datetime.date], 
                                    end_date: Union[str, datetime.date],
                                    fields: Optional[str] = None) -> int:
    """
    导入日期范围内的美国国库券利率数据
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期，可以是字符串格式YYYYMMDD或datetime.date对象
        end_date: 结束日期，可以是字符串格式YYYYMMDD或datetime.date对象
        fields: 可选，指定字段(e.g. fields='w4_bd,w52_ce')
        
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
    
    service = UsTbrService(db)
    count = await service.import_us_tbr_data(start_date=start_date_str, end_date=end_date_str, fields=fields)
    
    fields_info = f"，字段: {fields}" if fields else ""
    print(f"成功导入 {count} 条 {start_date_str} 至 {end_date_str} 日期范围内的美国国库券利率记录{fields_info}")
    return count


# 快捷函数，导入最新一天的美国国库券利率数据
async def import_latest_us_tbr(db, fields: Optional[str] = None) -> int:
    """
    导入最新一天的美国国库券利率数据
    
    参数:
        db: 数据库连接对象
        fields: 可选，指定字段(e.g. fields='w4_bd,w52_ce')
        
    返回:
        导入的记录数
    """
    # 获取当前日期的YYYYMMDD格式字符串
    today = datetime.date.today()
    date_str = today.strftime('%Y%m%d')
    
    service = UsTbrService(db)
    count = await service.import_us_tbr_data(date=date_str, fields=fields)
    
    fields_info = f"，字段: {fields}" if fields else ""
    
    if count > 0:
        print(f"成功导入 {count} 条 {date_str} 日期的最新美国国库券利率记录{fields_info}")
    else:
        # 如果当天没有数据，尝试获取前一天的数据
        yesterday = today - datetime.timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y%m%d')
        count = await service.import_us_tbr_data(date=yesterday_str, fields=fields)
        print(f"当天无数据，成功导入 {count} 条 {yesterday_str} 日期的美国国库券利率记录{fields_info}")
    
    return count


# 快捷函数，导入最近N天的美国国库券利率数据
async def import_recent_us_tbr(db, days: int = 30, fields: Optional[str] = None) -> int:
    """
    导入最近N天的美国国库券利率数据
    
    参数:
        db: 数据库连接对象
        days: 天数，默认30天
        fields: 可选，指定字段(e.g. fields='w4_bd,w52_ce')
        
    返回:
        导入的记录数
    """
    # 计算开始日期和结束日期
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days-1)  # 减一是因为包含当天
    
    # 格式化为YYYYMMDD格式字符串
    start_date_str = start_date.strftime('%Y%m%d')
    end_date_str = end_date.strftime('%Y%m%d')
    
    service = UsTbrService(db)
    count = await service.import_us_tbr_data(start_date=start_date_str, end_date=end_date_str, fields=fields)
    
    fields_info = f"，字段: {fields}" if fields else ""
    print(f"成功导入 {count} 条最近 {days} 天的美国国库券利率记录{fields_info}")
    return count


# 快捷函数，导入所有历史美国国库券利率数据
async def import_all_historical_us_tbr(db, batch_size: int = 1000, fields: Optional[str] = None) -> int:
    """
    导入所有历史美国国库券利率数据，注意这可能花费较长时间
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小
        fields: 可选，指定字段(e.g. fields='w4_bd,w52_ce')
        
    返回:
        导入的记录数
    """
    service = UsTbrService(db)
    # 不指定日期参数，将获取所有历史数据
    count = await service.import_us_tbr_data(fields=fields, batch_size=batch_size)
    
    fields_info = f"，字段: {fields}" if fields else ""
    print(f"成功导入 {count} 条历史美国国库券利率记录{fields_info}")
    return count


# 快捷函数，导入指定年份的美国国库券利率数据
async def import_us_tbr_by_year(db, year: int, fields: Optional[str] = None) -> int:
    """
    导入指定年份的美国国库券利率数据
    
    参数:
        db: 数据库连接对象
        year: 年份
        fields: 可选，指定字段(e.g. fields='w4_bd,w52_ce')
        
    返回:
        导入的记录数
    """
    # 计算年份的开始和结束日期
    start_date = datetime.date(year, 1, 1)
    end_date = datetime.date(year, 12, 31)
    
    # 格式化为YYYYMMDD格式字符串
    start_date_str = start_date.strftime('%Y%m%d')
    end_date_str = end_date.strftime('%Y%m%d')
    
    service = UsTbrService(db)
    count = await service.import_us_tbr_data(start_date=start_date_str, end_date=end_date_str, fields=fields)
    
    fields_info = f"，字段: {fields}" if fields else ""
    print(f"成功导入 {count} 条 {year} 年的美国国库券利率记录{fields_info}")
    return count


# 快捷函数，导入指定月份的美国国库券利率数据
async def import_us_tbr_by_month(db, year: int, month: int, fields: Optional[str] = None) -> int:
    """
    导入指定月份的美国国库券利率数据
    
    参数:
        db: 数据库连接对象
        year: 年份
        month: 月份 (1-12)
        fields: 可选，指定字段(e.g. fields='w4_bd,w52_ce')
        
    返回:
        导入的记录数
    """
    # 计算月份的开始日期
    start_date = datetime.date(year, month, 1)
    
    # 计算月份的结束日期
    if month == 12:
        end_date = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        end_date = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    
    # 格式化为YYYYMMDD格式字符串
    start_date_str = start_date.strftime('%Y%m%d')
    end_date_str = end_date.strftime('%Y%m%d')
    
    service = UsTbrService(db)
    count = await service.import_us_tbr_data(start_date=start_date_str, end_date=end_date_str, fields=fields)
    
    fields_info = f"，字段: {fields}" if fields else ""
    print(f"成功导入 {count} 条 {year}年{month}月 的美国国库券利率记录{fields_info}")
    return count


# 快捷函数，仅导入特定期限的美国国库券利率数据
async def import_us_tbr_by_terms(db, terms: List[str], rate_types: List[str] = ['bd', 'ce'],
                              start_date: Optional[Union[str, datetime.date]] = None,
                              end_date: Optional[Union[str, datetime.date]] = None) -> int:
    """
    仅导入特定期限的美国国库券利率数据
    
    参数:
        db: 数据库连接对象
        terms: 期限列表，例如 ['w4', 'w13', 'w52']
        rate_types: 利率类型列表，默认 ['bd', 'ce']
        start_date: 可选，开始日期
        end_date: 可选，结束日期
        
    返回:
        导入的记录数
    """
    # 验证期限参数
    valid_terms = {'w4', 'w8', 'w13', 'w17', 'w26', 'w52'}
    valid_rate_types = {'bd', 'ce'}
    
    filtered_terms = []
    for term in terms:
        if term in valid_terms:
            filtered_terms.append(term)
    
    filtered_rate_types = []
    for rate_type in rate_types:
        if rate_type in valid_rate_types:
            filtered_rate_types.append(rate_type)
    
    if not filtered_terms or not filtered_rate_types:
        print("没有提供有效的期限参数或利率类型")
        return 0
    
    # 构建字段列表
    field_list = []
    for term in filtered_terms:
        for rate_type in filtered_rate_types:
            field_list.append(f"{term}_{rate_type}")
    
    # 转换为字符串格式
    fields = ','.join(['date'] + field_list)
    
    # 处理日期参数
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
    
    service = UsTbrService(db)
    count = await service.import_us_tbr_data(start_date=start_date_str, end_date=end_date_str, fields=fields)
    
    date_info = ""
    if start_date_str and end_date_str:
        date_info = f" {start_date_str} 至 {end_date_str} 期间"
    elif start_date_str:
        date_info = f" 从 {start_date_str} 开始"
    elif end_date_str:
        date_info = f" 截至 {end_date_str}"
    
    term_info = ', '.join(filtered_terms)
    rate_type_info = ', '.join(filtered_rate_types)
    
    print(f"成功导入 {count} 条{date_info}的美国国库券利率数据，期限: {term_info}，利率类型: {rate_type_info}")
    return count