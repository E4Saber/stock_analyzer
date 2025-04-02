import pandas as pd
from decimal import Decimal
from typing import List, Optional, Dict, Any
from app.external.tushare_api.financial_info_api import get_dividend
from app.data.db_modules.stock_modules.stock_financial.dividend import DividendData
from app.db.crud.stock_crud.stock_financial.dividend_crud import DividendCRUD


class DividendService:
    """分红数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_dividend_data(self, ts_code: Optional[str] = None, 
                                ann_date: Optional[str] = None,
                                ex_date: Optional[str] = None,
                                record_date: Optional[str] = None,
                                imp_ann_date: Optional[str] = None,
                                batch_size: int = 1000) -> int:
        """
        从Tushare获取分红送股数据并高效导入数据库
        
        参数:
            ts_code: 股票代码
            ann_date: 公告日期（YYYYMMDD格式）
            ex_date: 除权除息日（YYYYMMDD格式）
            record_date: 股权登记日（YYYYMMDD格式）
            imp_ann_date: 实施公告日（YYYYMMDD格式）
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_dividend(ts_code=ts_code, ann_date=ann_date, ex_date=ex_date,
                              record_date=record_date, imp_ann_date=imp_ann_date)
        
        if df_result is None or df_result.empty:
            print(f"未找到分红数据: ts_code={ts_code}, ann_date={ann_date}, ex_date={ex_date}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 定义必填字段及默认值
        required_fields = {
            'ts_code': '',
            'end_date': None,
        }
        
        # 处理数据并确保所有必填字段都有值
        valid_records = []
        for record in records:
            # 确保必填字段存在且有值
            for field, default_value in required_fields.items():
                if field not in record or record[field] is None or (isinstance(record[field], str) and record[field] == ''):
                    record[field] = default_value
            
            # 如果缺少关键字段，跳过该记录
            if record['ts_code'] == '' or record['end_date'] is None:
                continue
            
            # 处理日期格式，确保是YYYYMMDD格式
            date_fields = ['end_date', 'ann_date', 'record_date', 'ex_date', 'pay_date', 'div_listdate', 'imp_ann_date', 'base_date']
            for date_field in date_fields:
                if date_field in record and record[date_field] is not None:
                    # 如果是pandas Timestamp对象，转换为YYYYMMDD格式字符串
                    if hasattr(record[date_field], 'strftime'):
                        record[date_field] = record[date_field].strftime('%Y%m%d')
                    # 如果已经是字符串但带有连字符（如"2023-12-31"），转换为YYYYMMDD
                    elif isinstance(record[date_field], str) and '-' in record[date_field]:
                        date_parts = record[date_field].split('-')
                        if len(date_parts) == 3:
                            record[date_field] = ''.join(date_parts)
                
            valid_records.append(record)
        
        # 分批处理
        batches = [valid_records[i:i + batch_size] for i in range(0, len(valid_records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为DividendData对象
                dividend_data_list = []
                for record in batch:
                    try:
                        # 处理数字字段，确保它们是Decimal类型
                        for key, value in record.items():
                            if isinstance(value, (float, int)) and key not in ['id']:
                                record[key] = Decimal(str(value))
                        
                        dividend_data = DividendData(**record)
                        dividend_data_list.append(dividend_data)
                    except Exception as e:
                        print(f"创建DividendData对象失败 {record.get('ts_code', '未知')}, {record.get('end_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if dividend_data_list:
                    inserted = await self.batch_upsert_dividend(dividend_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条分红记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_dividend(self, dividend_list: List[DividendData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            dividend_list: 要插入或更新的分红数据列表
            
        返回:
            处理的记录数
        """
        if not dividend_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = dividend_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 优先选择更新的记录
        # 使用字典来存储记录，如果有重复键，根据日期更新
        unique_records = {}
        
        for dividend in dividend_list:
            # 创建唯一键
            key = (dividend.ts_code, str(dividend.end_date), str(dividend.ann_date))
            
            # 如果键不存在，或者当前记录比已存在的记录更新，则更新
            if key not in unique_records or (dividend.imp_ann_date and (not unique_records[key][0].imp_ann_date or dividend.imp_ann_date > unique_records[key][0].imp_ann_date)):
                unique_records[key] = (dividend, True)
                print(f"保留记录: {dividend.ts_code}, {dividend.end_date}, {dividend.ann_date}")
            else:
                print(f"跳过记录: {dividend.ts_code}, {dividend.end_date}, {dividend.ann_date}, 已存在更新的记录")
        
        # 提取最终的唯一记录列表
        unique_dividend_list = [record[0] for record in unique_records.values()]
        
        # 准备数据
        records = []
        for dividend in unique_dividend_list:
            dividend_dict = dividend.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = dividend_dict[col]
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
                    # 手动创建临时表，明确指定列类型，不包含id列
                    # 首先获取原表的列信息
                    column_types = await self._get_column_type(conn, 'dividend', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_dividend (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_dividend', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'end_date', 'ann_date']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO dividend ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_dividend
                        ON CONFLICT (ts_code, end_date, ann_date) DO UPDATE SET {update_clause}
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

    async def _get_column_type(self, conn, table_name, columns):
        """
        获取表中指定列的数据类型
        
        参数:
            conn: 数据库连接
            table_name: 表名
            columns: 列名列表
            
        返回:
            字典，键为列名，值为数据类型
        """
        column_types = {}
        for column in columns:
            # 查询PostgreSQL系统表获取列的数据类型
            data_type = await conn.fetchval("""
                SELECT pg_catalog.format_type(a.atttypid, a.atttypmod)
                FROM pg_catalog.pg_attribute a
                JOIN pg_catalog.pg_class c ON a.attrelid = c.oid
                JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
                WHERE c.relname = $1
                AND a.attname = $2
                AND a.attnum > 0
                AND NOT a.attisdropped
            """, table_name, column)
            
            if data_type:
                column_types[column] = data_type
            else:
                # 如果找不到类型，使用通用类型
                column_types[column] = 'TEXT'
        
        return column_types


# 快捷函数，用于导入特定股票的分红数据
async def import_stock_dividend(db, ts_code: str, batch_size: int = 1000):
    """
    导入特定股票的分红数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = DividendService(db)
    count = await service.import_dividend_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条股票 {ts_code} 的分红记录")
    return count


# 快捷函数，用于导入特定公告日期的分红数据
async def import_ann_date_dividend(db, ann_date: str, batch_size: int = 1000):
    """
    导入特定公告日期的分红数据
    
    参数:
        db: 数据库连接对象
        ann_date: 公告日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = DividendService(db)
    count = await service.import_dividend_data(ann_date=ann_date, batch_size=batch_size)
    print(f"成功导入 {count} 条公告日期为 {ann_date} 的分红记录")
    return count


# 快捷函数，用于导入特定除权除息日的分红数据
async def import_ex_date_dividend(db, ex_date: str, batch_size: int = 1000):
    """
    导入特定除权除息日的分红数据
    
    参数:
        db: 数据库连接对象
        ex_date: 除权除息日（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = DividendService(db)
    count = await service.import_dividend_data(ex_date=ex_date, batch_size=batch_size)
    print(f"成功导入 {count} 条除权除息日为 {ex_date} 的分红记录")
    return count


# 快捷函数，用于导入特定股权登记日的分红数据
async def import_record_date_dividend(db, record_date: str, batch_size: int = 1000):
    """
    导入特定股权登记日的分红数据
    
    参数:
        db: 数据库连接对象
        record_date: 股权登记日（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = DividendService(db)
    count = await service.import_dividend_data(record_date=record_date, batch_size=batch_size)
    print(f"成功导入 {count} 条股权登记日为 {record_date} 的分红记录")
    return count


# 快捷函数，用于导入特定实施公告日的分红数据
async def import_imp_ann_date_dividend(db, imp_ann_date: str, batch_size: int = 1000):
    """
    导入特定实施公告日的分红数据
    
    参数:
        db: 数据库连接对象
        imp_ann_date: 实施公告日（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = DividendService(db)
    count = await service.import_dividend_data(imp_ann_date=imp_ann_date, batch_size=batch_size)
    print(f"成功导入 {count} 条实施公告日为 {imp_ann_date} 的分红记录")
    return count


# 导入所有分红数据
async def import_all_dividend(db, batch_size: int = 1000):
    """
    导入所有可获取的分红数据
    
    注意: 这可能会请求大量数据，请确保有足够的网络带宽和系统资源。
    根据数据量大小，此操作可能需要较长时间完成。
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小，默认1000条
        
    返回:
        导入的记录总数
    """
    service = DividendService(db)
    
    print("开始导入所有分红数据，此操作可能需要较长时间...")
    count = await service.import_dividend_data(batch_size=batch_size)
    
    print(f"成功导入所有分红数据，共 {count} 条记录")
    return count


# 动态查询分红数据
async def query_dividend_data(db, 
                            filters: Optional[Dict[str, Any]] = None, 
                            order_by: Optional[List[str]] = None,
                            limit: Optional[int] = None,
                            offset: Optional[int] = None):
    """
    动态查询分红数据，支持任意字段过滤和自定义排序
    
    参数:
        db: 数据库连接对象
        filters: 过滤条件字典，支持以下操作符后缀:
                 - __eq: 等于 (默认)
                 - __ne: 不等于
                 - __gt: 大于
                 - __ge: 大于等于
                 - __lt: 小于
                 - __le: 小于等于
                 - __like: LIKE模糊查询
                 - __ilike: ILIKE不区分大小写模糊查询
                 - __in: IN包含查询
                 例如: {'ts_code__like': '600%', 'ex_date__gt': '20230101'}
        order_by: 排序字段列表，字段前加"-"表示降序，例如['-ex_date', 'ts_code']
        limit: 最大返回记录数
        offset: 跳过前面的记录数（用于分页）
        
    返回:
        List[DividendData]: 符合条件的分红数据列表
    
    示例:
        # 查询某股票最近的分红记录，按除权除息日降序排列
        data = await query_dividend_data(
            db,
            filters={'ts_code': '000001.SZ'},
            order_by=['-ex_date']
        )
        
        # 分页查询某时间段内即将除权的股票
        data = await query_dividend_data(
            db,
            filters={
                'ex_date__ge': '20230101',
                'ex_date__le': '20230331'
            },
            order_by=['ex_date', 'ts_code'],
            limit=20,
            offset=0
        )
    """
    crud = DividendCRUD(db)
    results = await crud.get_dividend(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 查询特定公司的分红历史
async def get_company_dividend_history(db, ts_code: str, start_date: str = None, end_date: str = None, limit: int = 20):
    """
    查询特定公司的分红历史记录
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        start_date: 开始日期，格式YYYYMMDD
        end_date: 结束日期，格式YYYYMMDD
        limit: 最大返回记录数
        
    返回:
        List[DividendData]: 该公司的分红历史数据，按分红年度降序排列
    """
    filters = {'ts_code': ts_code}
    
    if start_date:
        filters['end_date__ge'] = start_date
    
    if end_date:
        filters['end_date__le'] = end_date
    
    return await query_dividend_data(
        db,
        filters=filters,
        order_by=['-end_date'],
        limit=limit
    )


# 查询即将除权除息的股票
async def get_upcoming_ex_dividend_stocks(db, days: int = 30, limit: int = 100):
    """
    查询未来指定天数内即将除权除息的股票
    
    参数:
        db: 数据库连接对象
        days: 未来天数
        limit: 最大返回记录数
        
    返回:
        List[DividendData]: 即将除权除息的股票列表，按除权除息日升序排列
    """
    from datetime import datetime, timedelta
    
    today = datetime.today().strftime('%Y%m%d')
    future_date = (datetime.today() + timedelta(days=days)).strftime('%Y%m%d')
    
    return await query_dividend_data(
        db,
        filters={
            'ex_date__ge': today,
            'ex_date__le': future_date
        },
        order_by=['ex_date', 'ts_code'],
        limit=limit
    )


# 统计公司分红频率和比例
async def analyze_company_dividend_pattern(db, ts_code: str, years: int = 5):
    """
    分析公司近几年的分红模式和频率
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        years: 分析的年数
        
    返回:
        Dict: 分红模式分析结果，包括频率、平均比例等
    """
    from datetime import datetime
    
    # 计算起始年份
    current_year = datetime.today().year
    start_year = current_year - years
    
    # 查询该公司近几年的分红记录
    dividend_data = await query_dividend_data(
        db,
        filters={
            'ts_code': ts_code,
            'end_date__ge': f'{start_year}0101'
        },
        order_by=['-end_date']
    )
    
    if not dividend_data:
        return {
            'ts_code': ts_code,
            'dividend_count': 0,
            'years_analyzed': years,
            'pattern': '无分红记录'
        }
    
    # 按年度分组统计
    year_data = {}
    for item in dividend_data:
        if item.end_date:
            year = item.end_date.year
            if year not in year_data:
                year_data[year] = []
            year_data[year].append(item)
    
    # 分析分红频率
    years_with_dividend = len(year_data)
    dividend_frequency = years_with_dividend / min(years, current_year - start_year + 1)
    
    # 分析分红比例
    total_cash_div = 0
    count_cash_div = 0
    
    for year, dividends in year_data.items():
        for dividend in dividends:
            if dividend.cash_div:
                total_cash_div += float(dividend.cash_div)
                count_cash_div += 1
    
    avg_cash_div = total_cash_div / count_cash_div if count_cash_div > 0 else 0
    
    # 分析股票分红情况
    has_stock_dividend = any(
        dividend.stk_div or dividend.stk_bo_rate or dividend.stk_co_rate
        for dividends in year_data.values()
        for dividend in dividends
    )
    
    # 确定分红模式
    if dividend_frequency >= 0.8:
        frequency_pattern = '稳定分红'
    elif dividend_frequency >= 0.5:
        frequency_pattern = '较常分红'
    else:
        frequency_pattern = '偶尔分红'
    
    return {
        'ts_code': ts_code,
        'dividend_count': len(dividend_data),
        'years_with_dividend': years_with_dividend,
        'years_analyzed': years,
        'dividend_frequency': round(dividend_frequency, 2),
        'frequency_pattern': frequency_pattern,
        'avg_cash_div': round(avg_cash_div, 4),
        'has_stock_dividend': has_stock_dividend,
        'yearly_summary': {
            year: {
                'dividend_count': len(dividends),
                'cash_div': sum(float(d.cash_div) if d.cash_div else 0 for d in dividends),
                'has_stock_div': any(d.stk_div or d.stk_bo_rate or d.stk_co_rate for d in dividends)
            }
            for year, dividends in year_data.items()
        }
    }