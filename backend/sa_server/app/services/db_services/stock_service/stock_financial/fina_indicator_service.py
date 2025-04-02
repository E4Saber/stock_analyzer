import pandas as pd
from decimal import Decimal
from typing import List, Optional, Dict, Any
from app.external.tushare_api.financial_info_api import get_fina_indicator
from app.data.db_modules.stock_modules.stock_financial.fina_indicator import FinaIndicatorData
from app.db.crud.stock_crud.stock_financial.fina_indicator_crud import FinaIndicatorCRUD

class FinaIndicatorService:
    """财务指标数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_fina_indicator_data(self, ts_code: Optional[str] = None, 
                                      ann_date: Optional[str] = None,
                                      start_date: Optional[str] = None, 
                                      end_date: Optional[str] = None,
                                      period: Optional[str] = None,
                                      batch_size: int = 1000) -> int:
        """
        从Tushare获取财务指标数据并高效导入数据库
        
        参数:
            ts_code: 股票代码
            ann_date: 公告日期（YYYYMMDD格式）
            start_date: 报告期开始日期（YYYYMMDD格式）
            end_date: 报告期结束日期（YYYYMMDD格式）
            period: 报告期(YYYYMMDD格式，每个季度最后一天的日期，比如20171231表示年报)
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_fina_indicator(ts_code=ts_code, ann_date=ann_date,
                                    start_date=start_date, end_date=end_date,
                                    period=period)
        
        if df_result is None or df_result.empty:
            print(f"未找到财务指标数据: ts_code={ts_code}, period={period}")
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
            date_fields = ['ann_date', 'end_date']
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
                # 将批次数据转换为FinaIndicatorData对象
                fina_indicator_data_list = []
                for record in batch:
                    try:
                        # 处理数字字段，确保它们是Decimal类型
                        for key, value in record.items():
                            if isinstance(value, (float, int)) and key not in ['id']:
                                record[key] = Decimal(str(value))
                        
                        fina_indicator_data = FinaIndicatorData(**record)
                        fina_indicator_data_list.append(fina_indicator_data)
                    except Exception as e:
                        print(f"创建FinaIndicatorData对象失败 {record.get('ts_code', '未知')}, {record.get('end_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if fina_indicator_data_list:
                    inserted = await self.batch_upsert_fina_indicator(fina_indicator_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条财务指标记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_fina_indicator(self, fina_indicator_list: List[FinaIndicatorData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            fina_indicator_list: 要插入或更新的财务指标数据列表
            
        返回:
            处理的记录数
        """
        if not fina_indicator_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = fina_indicator_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 优先选择update_flag为1的记录
        # 使用字典来存储记录，如果有重复键，根据update_flag决定是否替换
        unique_records = {}
        
        for fina_indicator in fina_indicator_list:
            # 创建唯一键
            key = (fina_indicator.ts_code, str(fina_indicator.end_date))
            
            # 获取update_flag，如果不存在则默认为0
            update_flag = getattr(fina_indicator, 'update_flag', '0')
            
            # 如果键不存在，或者当前记录的update_flag为1且已存记录的update_flag不为1，则更新
            if key not in unique_records or (update_flag == '1' and unique_records[key][1] != '1'):
                unique_records[key] = (fina_indicator, update_flag)
                print(f"保留记录: {fina_indicator.ts_code}, {fina_indicator.end_date}, update_flag={update_flag}")
            else:
                existing_flag = unique_records[key][1]
                print(f"跳过记录: {fina_indicator.ts_code}, {fina_indicator.end_date}, "
                    f"update_flag={update_flag}，已存在update_flag={existing_flag}的记录")
        
        # 提取最终的唯一记录列表
        unique_fina_indicator_list = [record[0] for record in unique_records.values()]
        
        # 准备数据
        records = []
        for fina_indicator in unique_fina_indicator_list:
            fina_indicator_dict = fina_indicator.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = fina_indicator_dict[col]
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
                    column_types = await self._get_column_type(conn, 'fina_indicator', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_fina_indicator (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_fina_indicator', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'end_date']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO fina_indicator ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_fina_indicator
                        ON CONFLICT (ts_code, end_date) DO UPDATE SET {update_clause}
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


# 快捷函数，用于导入特定股票的财务指标数据
async def import_stock_fina_indicator(db, ts_code: str, batch_size: int = 1000):
    """
    导入特定股票的财务指标数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = FinaIndicatorService(db)
    count = await service.import_fina_indicator_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条股票 {ts_code} 的财务指标记录")
    return count


# 快捷函数，用于导入特定公告日期的财务指标数据
async def import_ann_date_fina_indicator(db, ann_date: str, batch_size: int = 1000):
    """
    导入特定公告日期的财务指标数据
    
    参数:
        db: 数据库连接对象
        ann_date: 公告日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = FinaIndicatorService(db)
    count = await service.import_fina_indicator_data(ann_date=ann_date, batch_size=batch_size)
    print(f"成功导入 {count} 条公告日期为 {ann_date} 的财务指标记录")
    return count


# 快捷函数，用于导入特定时间段的财务指标数据
async def import_date_range_fina_indicator(db, start_date: str, end_date: str, batch_size: int = 1000):
    """
    导入特定时间段的财务指标数据
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期（YYYYMMDD格式）
        end_date: 结束日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = FinaIndicatorService(db)
    count = await service.import_fina_indicator_data(start_date=start_date, end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条报告期在 {start_date} 至 {end_date} 之间的财务指标记录")
    return count


# 快捷函数，用于导入特定报告期的财务指标数据
async def import_period_fina_indicator(db, period: str, batch_size: int = 1000):
    """
    导入特定报告期的财务指标数据
    
    参数:
        db: 数据库连接对象
        period: 报告期(每个季度最后一天的日期，比如20171231表示年报，20170630半年报，20170930三季报)
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = FinaIndicatorService(db)
    count = await service.import_fina_indicator_data(period=period, batch_size=batch_size)
    
    # 确定报告期类型的描述
    period_desc = ""
    if period and len(period) == 8:
        month_day = period[4:]
        if month_day == "1231":
            period_desc = "年报"
        elif month_day == "0630":
            period_desc = "半年报"
        elif month_day == "0930":
            period_desc = "三季报"
        elif month_day == "0331":
            period_desc = "一季报"
    
    period_info = f"{period} ({period_desc})" if period_desc else period
    print(f"成功导入 {count} 条报告期为 {period_info} 的财务指标记录")
    return count


# 综合导入函数，支持多种参数组合
async def import_fina_indicator_with_params(db, **kwargs):
    """
    根据提供的参数导入财务指标数据
    
    参数:
        db: 数据库连接对象
        **kwargs: 可包含 ts_code, ann_date, start_date, end_date, period, batch_size 等参数
        
    返回:
        导入的记录数
    """
    service = FinaIndicatorService(db)
    batch_size = kwargs.pop('batch_size', 1000)  # 提取并移除batch_size参数
    
    # 构建参数描述
    param_desc = []
    for key, value in kwargs.items():
        if value:
            param_desc.append(f"{key}={value}")
    
    params_info = ", ".join(param_desc) if param_desc else "所有可用参数"
    
    # 导入数据
    count = await service.import_fina_indicator_data(batch_size=batch_size, **kwargs)
    print(f"成功导入 {count} 条财务指标记录 ({params_info})")
    return count


# 导入所有财务指标数据
async def import_all_fina_indicator(db, batch_size: int = 1000):
    """
    导入所有可获取的财务指标数据
    
    注意: 这可能会请求大量数据，请确保有足够的网络带宽和系统资源。
    根据数据量大小，此操作可能需要较长时间完成。
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小，默认1000条
        
    返回:
        导入的记录总数
    """
    service = FinaIndicatorService(db)
    
    print("开始导入所有财务指标数据，此操作可能需要较长时间...")
    count = await service.import_fina_indicator_data(batch_size=batch_size)
    
    print(f"成功导入所有财务指标数据，共 {count} 条记录")
    return count


# 动态查询财务指标数据
async def query_fina_indicator_data(db, 
                                 filters: Optional[Dict[str, Any]] = None, 
                                 order_by: Optional[List[str]] = None,
                                 limit: Optional[int] = None,
                                 offset: Optional[int] = None):
    """
    动态查询财务指标数据，支持任意字段过滤和自定义排序
    
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
                 例如: {'ts_code__like': '600%', 'end_date__gt': '20230101'}
        order_by: 排序字段列表，字段前加"-"表示降序，例如['-end_date', 'ts_code']
        limit: 最大返回记录数
        offset: 跳过前面的记录数（用于分页）
        
    返回:
        List[FinaIndicatorData]: 符合条件的财务指标数据列表
    
    示例:
        # 查询某股票最近两年的年报财务指标，按报告期降序排列
        data = await query_fina_indicator_data(
            db,
            filters={
                'ts_code': '000001.SZ',
                'end_date__ge': '20220101'
            },
            order_by=['-end_date']
        )
        
        # 分页查询ROE超过15%的公司
        data = await query_fina_indicator_data(
            db,
            filters={'roe__gt': 15},
            order_by=['-roe', 'ts_code'],
            limit=20,
            offset=0
        )
    """
    crud = FinaIndicatorCRUD(db)
    results = await crud.get_fina_indicator(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 查询特定公司的财务指标趋势
async def get_company_fina_indicator_trend(db, ts_code: str, start_date: str = None, end_date: str = None, limit: int = 20):
    """
    查询特定公司在时间段内的财务指标趋势
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        start_date: 开始日期，格式YYYYMMDD
        end_date: 结束日期，格式YYYYMMDD
        limit: 最大返回记录数
        
    返回:
        List[FinaIndicatorData]: 该公司的财务指标趋势数据，按报告期降序排列
    """
    filters = {'ts_code': ts_code}
    
    if start_date:
        filters['end_date__ge'] = start_date
    
    if end_date:
        filters['end_date__le'] = end_date
    
    return await query_fina_indicator_data(
        db,
        filters=filters,
        order_by=['-end_date'],
        limit=limit
    )


# 对比多家公司的财务指标
async def compare_companies_fina_indicator(db, ts_codes: List[str], end_date: str):
    """
    对比多家公司在同一报告期的财务指标
    
    参数:
        db: 数据库连接对象
        ts_codes: 股票代码列表
        end_date: 报告期，格式YYYYMMDD
        
    返回:
        List[FinaIndicatorData]: 多家公司在指定报告期的财务指标数据
    """
    return await query_fina_indicator_data(
        db,
        filters={
            'ts_code__in': ts_codes,
            'end_date': end_date
        }
    )


# 筛选特定条件的公司
async def screen_companies_by_criteria(db, criteria: Dict[str, Any], end_date: str = None, limit: int = 100):
    """
    根据财务指标筛选符合条件的公司
    
    参数:
        db: 数据库连接对象
        criteria: 筛选条件，例如 {'roe__gt': 15, 'debt_to_assets__lt': 50}
        end_date: 筛选的报告期，不指定则使用最新报告期
        limit: 最大返回记录数
        
    返回:
        List[FinaIndicatorData]: 符合条件的公司财务指标数据
    """
    filters = criteria.copy()
    
    if end_date:
        filters['end_date'] = end_date
    
    # 按指定字段降序排序，默认按ROE
    sort_field = '-roe'
    if 'roe__gt' in criteria or 'roe__ge' in criteria:
        sort_field = '-roe'
    elif 'netprofit_yoy__gt' in criteria or 'netprofit_yoy__ge' in criteria:
        sort_field = '-netprofit_yoy'
    elif 'roa__gt' in criteria or 'roa__ge' in criteria:
        sort_field = '-roa'
    
    return await query_fina_indicator_data(
        db,
        filters=filters,
        order_by=[sort_field, 'ts_code'],
        limit=limit
    )


# 分析公司财务指标同比变化
async def analyze_fina_indicator_yoy_change(db, ts_code: str, indicators: List[str], periods: int = 5):
    """
    分析公司最近几个报告期的财务指标同比变化
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        indicators: 要分析的财务指标列表，例如 ['roe', 'eps', 'netprofit_margin']
        periods: 分析的报告期数量
        
    返回:
        List[Dict]: 包含原始数据和同比变化的列表
    """
    # 获取公司的财务指标数据，按报告期降序排序
    fina_indicator_data = await query_fina_indicator_data(
        db,
        filters={'ts_code': ts_code},
        order_by=['-end_date'],
        limit=periods * 2  # 获取更多数据以计算同比
    )
    
    if not fina_indicator_data or len(fina_indicator_data) < 2:
        return fina_indicator_data  # 数据不足，无法计算同比
    
    # 按年度分组
    year_data = {}
    for item in fina_indicator_data:
        if item.end_date:
            year = item.end_date.year
            month_day = item.end_date.strftime('%m%d')
            
            # 使用年份和月日组合作为键，确保比较相同报告期
            key = f"{year}_{month_day}"
            if key not in year_data:
                year_data[key] = item
    
    # 计算同比变化
    result = []
    keys = sorted(year_data.keys(), reverse=True)
    
    for i, key in enumerate(keys):
        if i >= periods:
            break
            
        current_data = year_data[key]
        current_dict = current_data.model_dump()
        
        # 提取年份和月日
        year, month_day = key.split('_')
        year = int(year)
        
        # 构建上一年同期的键
        prev_key = f"{year-1}_{month_day}"
        
        # 如果有上一年同期数据，计算同比变化
        if prev_key in year_data:
            prev_data = year_data[prev_key]
            
            # 计算指定财务指标的同比变化
            yoy_changes = {}
            for indicator in indicators:
                curr_val = getattr(current_data, indicator, None)
                prev_val = getattr(prev_data, indicator, None)
                
                if curr_val is not None and prev_val is not None and prev_val != 0:
                    yoy_changes[f"{indicator}_yoy_change"] = float((curr_val - prev_val) / abs(prev_val) * 100)
                else:
                    yoy_changes[f"{indicator}_yoy_change"] = None
            
            current_dict.update(yoy_changes)
        
        result.append(current_dict)
    
    return result


# 获取行业龙头企业财务指标
async def get_industry_leaders_fina_indicator(db, industry_code: str, indicator: str = 'roe', top_n: int = 10, end_date: str = None):
    """
    获取特定行业中按财务指标排名的龙头企业
    
    参数:
        db: 数据库连接对象
        industry_code: 行业代码
        indicator: 排序的财务指标，例如'roe'、'eps'等
        top_n: 返回前N家公司
        end_date: 筛选的报告期，不指定则使用最新报告期
        
    返回:
        List[FinaIndicatorData]: 行业龙头企业的财务指标数据
    """
    # 此处需要先获取该行业的所有股票代码
    # 实际实现时需要有行业分类表或API
    
    # 模拟实现，假设我们已经知道行业内的股票代码
    # 实际项目中，应该通过行业分类表查询获取
    industry_stocks = []  # 实际项目中从数据库获取行业内的股票代码
    
    # 构建过滤条件
    filters = {}
    
    if industry_stocks:  # 如果有行业股票列表，则添加到过滤条件
        filters['ts_code__in'] = industry_stocks
    else:
        # 如果无法获取行业股票，则使用传入的行业代码进行模糊匹配
        # 注意：这是一个不太准确的替代方案，实际项目应当使用行业分类表
        filters['ts_code__like'] = f"{industry_code}%"
    
    if end_date:
        filters['end_date'] = end_date
    
    # 确保所选指标有值
    filters[f"{indicator}__ne"] = None
    
    # 按指定指标降序排序获取龙头企业
    return await query_fina_indicator_data(
        db,
        filters=filters,
        order_by=[f"-{indicator}", 'ts_code'],
        limit=top_n
    )


# 分析公司关键财务指标
async def analyze_key_financial_ratios(db, ts_code: str, end_date: str = None):
    """
    分析公司关键财务比率，提供综合评估
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        end_date: 报告期，不指定则使用最新报告期
        
    返回:
        Dict: 财务比率分析结果和评估
    """
    # 构建过滤条件
    filters = {'ts_code': ts_code}
    
    if end_date:
        filters['end_date'] = end_date
    
    # 获取公司财务指标
    data = await query_fina_indicator_data(
        db,
        filters=filters,
        order_by=['-end_date'],
        limit=1
    )
    
    if not data:
        return {'status': 'error', 'message': '未找到财务指标数据'}
    
    # 获取最新财务指标
    indicator = data[0]
    
    # 定义评估范围
    assessment = {
        'profitability': {
            'roe': {
                'value': indicator.roe,
                'rating': _rate_financial_indicator('roe', indicator.roe),
                'description': '净资产收益率'
            },
            'netprofit_margin': {
                'value': indicator.netprofit_margin,
                'rating': _rate_financial_indicator('netprofit_margin', indicator.netprofit_margin),
                'description': '销售净利率'
            },
            'grossprofit_margin': {
                'value': indicator.grossprofit_margin,
                'rating': _rate_financial_indicator('grossprofit_margin', indicator.grossprofit_margin),
                'description': '销售毛利率'
            }
        },
        'solvency': {
            'current_ratio': {
                'value': indicator.current_ratio,
                'rating': _rate_financial_indicator('current_ratio', indicator.current_ratio),
                'description': '流动比率'
            },
            'quick_ratio': {
                'value': indicator.quick_ratio,
                'rating': _rate_financial_indicator('quick_ratio', indicator.quick_ratio),
                'description': '速动比率'
            },
            'debt_to_assets': {
                'value': indicator.debt_to_assets,
                'rating': _rate_financial_indicator('debt_to_assets', indicator.debt_to_assets),
                'description': '资产负债率'
            }
        },
        'growth': {
            'netprofit_yoy': {
                'value': indicator.netprofit_yoy,
                'rating': _rate_financial_indicator('netprofit_yoy', indicator.netprofit_yoy),
                'description': '净利润同比增长率'
            },
            'tr_yoy': {
                'value': indicator.tr_yoy,
                'rating': _rate_financial_indicator('tr_yoy', indicator.tr_yoy),
                'description': '营业总收入同比增长率'
            },
            'op_yoy': {
                'value': indicator.op_yoy,
                'rating': _rate_financial_indicator('op_yoy', indicator.op_yoy),
                'description': '营业利润同比增长率'
            }
        },
        'operation': {
            'assets_turn': {
                'value': indicator.assets_turn,
                'rating': _rate_financial_indicator('assets_turn', indicator.assets_turn),
                'description': '总资产周转率'
            },
            'ar_turn': {
                'value': indicator.ar_turn,
                'rating': _rate_financial_indicator('ar_turn', indicator.ar_turn),
                'description': '应收账款周转率'
            },
            'inv_turn': {
                'value': indicator.inv_turn,
                'rating': _rate_financial_indicator('inv_turn', indicator.inv_turn),
                'description': '存货周转率'
            }
        },
        'per_share': {
            'eps': {
                'value': indicator.eps,
                'rating': _rate_financial_indicator('eps', indicator.eps),
                'description': '每股收益'
            },
            'bps': {
                'value': indicator.bps,
                'rating': _rate_financial_indicator('bps', indicator.bps),
                'description': '每股净资产'
            },
            'cfps': {
                'value': indicator.cfps,
                'rating': _rate_financial_indicator('cfps', indicator.cfps),
                'description': '每股现金流量净额'
            }
        }
    }
    
    # 计算各类别的综合评分
    for category, indicators in assessment.items():
        valid_ratings = [item['rating'] for item in indicators.values() if item['rating'] is not None]
        if valid_ratings:
            assessment[category]['overall_rating'] = sum(valid_ratings) / len(valid_ratings)
        else:
            assessment[category]['overall_rating'] = None
    
    # 计算总体评分
    valid_category_ratings = [item['overall_rating'] for item in assessment.values() if item['overall_rating'] is not None]
    overall_rating = sum(valid_category_ratings) / len(valid_category_ratings) if valid_category_ratings else None
    
    return {
        'ts_code': ts_code,
        'end_date': indicator.end_date,
        'assessment': assessment,
        'overall_rating': overall_rating
    }


def _rate_financial_indicator(indicator_name, value):
    """
    对财务指标进行评级，返回0-5的得分
    
    参数:
        indicator_name: 指标名称
        value: 指标值
        
    返回:
        float: 0-5的评分，None表示无法评分
    """
    if value is None:
        return None
    
    # 定义各指标的评分标准
    rating_criteria = {
        # 盈利能力指标
        'roe': [(0, 1), (5, 2), (10, 3), (15, 4), (20, 5)],  # ROE: <0=1, 0-5=2, 5-10=3, 10-15=4, >15=5
        'netprofit_margin': [(0, 1), (5, 2), (10, 3), (15, 4), (20, 5)],
        'grossprofit_margin': [(0, 1), (10, 2), (20, 3), (30, 4), (40, 5)],
        
        # 偿债能力指标
        'current_ratio': [(0.5, 1), (1.0, 2), (1.5, 3), (2.0, 4), (3.0, 5)],
        'quick_ratio': [(0.3, 1), (0.5, 2), (1.0, 3), (1.5, 4), (2.0, 5)],
        'debt_to_assets': [(90, 1), (70, 2), (60, 3), (50, 4), (40, 5)],  # 资产负债率越低越好
        
        # 增长指标
        'netprofit_yoy': [(0, 1), (5, 2), (10, 3), (20, 4), (30, 5)],
        'tr_yoy': [(0, 1), (5, 2), (10, 3), (15, 4), (20, 5)],
        'op_yoy': [(0, 1), (5, 2), (10, 3), (20, 4), (30, 5)],
        
        # 运营能力指标
        'assets_turn': [(0.3, 1), (0.5, 2), (0.8, 3), (1.0, 4), (1.5, 5)],
        'ar_turn': [(2, 1), (4, 2), (6, 3), (8, 4), (10, 5)],
        'inv_turn': [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)],
        
        # 每股指标
        'eps': [(0, 1), (0.3, 2), (0.5, 3), (1.0, 4), (2.0, 5)],
        'bps': [(1, 1), (3, 2), (5, 3), (10, 4), (15, 5)],
        'cfps': [(0, 1), (0.5, 2), (1.0, 3), (2.0, 4), (3.0, 5)]
    }
    
    # 如果指标不在评分标准中，返回None
    if indicator_name not in rating_criteria:
        return None
    
    # 取得该指标的评分标准
    criteria = rating_criteria[indicator_name]
    
    # 特殊处理负值的情况
    if value < 0:
        # 对于ROE、利润率、增长率等，负值通常表现极差
        return 0
    
    # 资产负债率需要特殊处理（越低越好）
    if indicator_name == 'debt_to_assets':
        for threshold, score in criteria:
            if value >= threshold:
                return score
        return 5  # 如果低于所有阈值，给予最高分
    
    # 常规指标（越高越好）
    for threshold, score in criteria:
        if value < threshold:
            return score - 1 if score > 1 else 0
    
    # 如果高于所有阈值，给予最高分
    return 5