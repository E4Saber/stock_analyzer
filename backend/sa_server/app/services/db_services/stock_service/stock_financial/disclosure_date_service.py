import pandas as pd
from typing import List, Optional, Dict, Any
from app.external.tushare_api.financial_info_api import get_disclosure_date
from app.data.db_modules.stock_modules.stock_financial.disclosure_date import DisclosureDateData
from app.db.crud.stock_crud.stock_financial.disclosure_date_crud import DisclosureDateCRUD

class DisclosureDateService:
    """财报披露日期数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_disclosure_date_data(self, ts_code: Optional[str] = None, 
                                       end_date: Optional[str] = None,
                                       pre_date: Optional[str] = None, 
                                       actual_date: Optional[str] = None,
                                       batch_size: int = 1000) -> int:
        """
        从Tushare获取财报披露日期数据并高效导入数据库
        
        参数:
            ts_code: 股票代码
            end_date: 报告期(每个季度最后一天的日期，比如20171231表示年报)
            pre_date: 预计披露日期
            actual_date: 实际披露日期
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_disclosure_date(ts_code=ts_code, end_date=end_date,
                                     pre_date=pre_date, actual_date=actual_date)
        
        if df_result is None or df_result.empty:
            print(f"未找到财报披露日期数据: ts_code={ts_code}, end_date={end_date}")
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
            date_fields = ['end_date', 'ann_date', 'pre_date', 'actual_date', 'modify_date']
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
                # 将批次数据转换为DisclosureDateData对象
                disclosure_date_data_list = []
                for record in batch:
                    try:
                        disclosure_date_data = DisclosureDateData(**record)
                        disclosure_date_data_list.append(disclosure_date_data)
                    except Exception as e:
                        print(f"创建DisclosureDateData对象失败 {record.get('ts_code', '未知')}, {record.get('end_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if disclosure_date_data_list:
                    inserted = await self.batch_upsert_disclosure_date(disclosure_date_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条财报披露日期记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_disclosure_date(self, disclosure_date_list: List[DisclosureDateData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            disclosure_date_list: 要插入或更新的财报披露日期数据列表
            
        返回:
            处理的记录数
        """
        if not disclosure_date_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = disclosure_date_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 使用字典来存储记录，避免重复
        unique_records = {}
        
        for disclosure_date in disclosure_date_list:
            # 创建唯一键
            key = (disclosure_date.ts_code, str(disclosure_date.end_date))
            
            # 如果键不存在，或者当前记录有更新的日期，则更新
            if key not in unique_records or (disclosure_date.modify_date and (not unique_records[key].modify_date or disclosure_date.modify_date > unique_records[key].modify_date)):
                unique_records[key] = disclosure_date
                print(f"保留记录: {disclosure_date.ts_code}, {disclosure_date.end_date}")
            else:
                print(f"跳过记录: {disclosure_date.ts_code}, {disclosure_date.end_date}, 已存在更新的记录")
        
        # 提取最终的唯一记录列表
        unique_disclosure_date_list = list(unique_records.values())
        
        # 准备数据
        records = []
        for disclosure_date in unique_disclosure_date_list:
            disclosure_date_dict = disclosure_date.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = disclosure_date_dict[col]
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
                    column_types = await self._get_column_type(conn, 'disclosure_date', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_disclosure_date (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_disclosure_date', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'end_date']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO disclosure_date ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_disclosure_date
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


# 快捷函数，用于导入特定股票的财报披露日期数据
async def import_stock_disclosure_date(db, ts_code: str, batch_size: int = 1000):
    """
    导入特定股票的财报披露日期数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = DisclosureDateService(db)
    count = await service.import_disclosure_date_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条股票 {ts_code} 的财报披露日期记录")
    return count


# 快捷函数，用于导入特定报告期的财报披露日期数据
async def import_end_date_disclosure_date(db, end_date: str, batch_size: int = 1000):
    """
    导入特定报告期的财报披露日期数据
    
    参数:
        db: 数据库连接对象
        end_date: 报告期(每个季度最后一天的日期，比如20171231表示年报)
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = DisclosureDateService(db)
    count = await service.import_disclosure_date_data(end_date=end_date, batch_size=batch_size)
    
    # 确定报告期类型的描述
    period_desc = ""
    if end_date and len(end_date) == 8:
        month_day = end_date[4:]
        if month_day == "1231":
            period_desc = "年报"
        elif month_day == "0630":
            period_desc = "半年报"
        elif month_day == "0930":
            period_desc = "三季报"
        elif month_day == "0331":
            period_desc = "一季报"
    
    period_info = f"{end_date} ({period_desc})" if period_desc else end_date
    print(f"成功导入 {count} 条报告期为 {period_info} 的财报披露日期记录")
    return count


# 快捷函数，用于导入特定预计披露日期的财报披露日期数据
async def import_pre_date_disclosure_date(db, pre_date: str, batch_size: int = 1000):
    """
    导入特定预计披露日期的财报披露日期数据
    
    参数:
        db: 数据库连接对象
        pre_date: 预计披露日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = DisclosureDateService(db)
    count = await service.import_disclosure_date_data(pre_date=pre_date, batch_size=batch_size)
    print(f"成功导入 {count} 条预计披露日期为 {pre_date} 的财报披露日期记录")
    return count


# 快捷函数，用于导入特定实际披露日期的财报披露日期数据
async def import_actual_date_disclosure_date(db, actual_date: str, batch_size: int = 1000):
    """
    导入特定实际披露日期的财报披露日期数据
    
    参数:
        db: 数据库连接对象
        actual_date: 实际披露日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = DisclosureDateService(db)
    count = await service.import_disclosure_date_data(actual_date=actual_date, batch_size=batch_size)
    print(f"成功导入 {count} 条实际披露日期为 {actual_date} 的财报披露日期记录")
    return count


# 综合导入函数，支持多种参数组合
async def import_disclosure_date_with_params(db, **kwargs):
    """
    根据提供的参数导入财报披露日期数据
    
    参数:
        db: 数据库连接对象
        **kwargs: 可包含 ts_code, end_date, pre_date, actual_date, batch_size 等参数
        
    返回:
        导入的记录数
    """
    service = DisclosureDateService(db)
    batch_size = kwargs.pop('batch_size', 1000)  # 提取并移除batch_size参数
    
    # 构建参数描述
    param_desc = []
    for key, value in kwargs.items():
        if value:
            param_desc.append(f"{key}={value}")
    
    params_info = ", ".join(param_desc) if param_desc else "所有可用参数"
    
    # 导入数据
    count = await service.import_disclosure_date_data(batch_size=batch_size, **kwargs)
    print(f"成功导入 {count} 条财报披露日期记录 ({params_info})")
    return count


# 导入所有财报披露日期数据
async def import_all_disclosure_date(db, batch_size: int = 1000):
    """
    导入所有可获取的财报披露日期数据
    
    注意: 这可能会请求大量数据，请确保有足够的网络带宽和系统资源。
    根据数据量大小，此操作可能需要较长时间完成。
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小，默认1000条
        
    返回:
        导入的记录总数
    """
    service = DisclosureDateService(db)
    
    print("开始导入所有财报披露日期数据，此操作可能需要较长时间...")
    count = await service.import_disclosure_date_data(batch_size=batch_size)
    
    print(f"成功导入所有财报披露日期数据，共 {count} 条记录")
    return count


# 动态查询财报披露日期数据
async def query_disclosure_date_data(db, 
                                  filters: Optional[Dict[str, Any]] = None, 
                                  order_by: Optional[List[str]] = None,
                                  limit: Optional[int] = None,
                                  offset: Optional[int] = None):
    """
    动态查询财报披露日期数据，支持任意字段过滤和自定义排序
    
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
        List[DisclosureDateData]: 符合条件的财报披露日期数据列表
    
    示例:
        # 查询某股票最近的财报披露日期记录
        data = await query_disclosure_date_data(
            db,
            filters={'ts_code': '000001.SZ'},
            order_by=['-end_date']
        )
        
        # 查询即将披露财报的公司
        data = await query_disclosure_date_data(
            db,
            filters={'pre_date__ge': '20230101', 'pre_date__le': '20230131'},
            order_by=['pre_date', 'ts_code']
        )
    """
    crud = DisclosureDateCRUD(db)
    results = await crud.get_disclosure_date(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 获取公司财报披露历史
async def get_company_disclosure_history(db, ts_code: str, limit: int = 10):
    """
    获取公司的财报披露历史记录
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        limit: 最大返回记录数
        
    返回:
        List[DisclosureDateData]: 公司财报披露历史数据
    """
    return await query_disclosure_date_data(
        db,
        filters={'ts_code': ts_code},
        order_by=['-end_date'],
        limit=limit
    )


# 获取即将披露财报的公司
async def get_upcoming_disclosure_companies(db, days: int = 30):
    """
    获取未来特定天数内即将披露财报的公司
    
    参数:
        db: 数据库连接对象
        days: 未来天数
        
    返回:
        List[DisclosureDateData]: 即将披露财报的公司数据
    """
    from datetime import datetime, timedelta
    
    today = datetime.today().strftime('%Y%m%d')
    future_date = (datetime.today() + timedelta(days=days)).strftime('%Y%m%d')
    
    return await query_disclosure_date_data(
        db,
        filters={
            'pre_date__ge': today,
            'pre_date__le': future_date
        },
        order_by=['pre_date', 'ts_code']
    )


# 分析公司财报披露及时性
async def analyze_company_disclosure_timeliness(db, ts_code: str, periods: int = 8):
    """
    分析公司财报披露的及时性
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        periods: 分析的报告期数量
        
    返回:
        Dict: 公司财报披露及时性分析结果
    """
    # 获取公司的财报披露历史数据
    data = await query_disclosure_date_data(
        db,
        filters={'ts_code': ts_code},
        order_by=['-end_date'],
        limit=periods
    )
    
    if not data:
        return {
            'ts_code': ts_code,
            'message': '未找到财报披露日期数据'
        }
    
    # 计算实际披露日期与预计披露日期的差异
    disclosure_records = []
    delay_count = 0
    advance_count = 0
    on_time_count = 0
    
    for item in data:
        record = {
            'end_date': item.end_date,
            'pre_date': item.pre_date,
            'actual_date': item.actual_date
        }
        
        # 计算披露差异天数
        if item.pre_date and item.actual_date:
            diff_days = (item.actual_date - item.pre_date).days
            record['diff_days'] = diff_days
            
            if diff_days > 0:
                record['status'] = '延迟披露'
                delay_count += 1
            elif diff_days < 0:
                record['status'] = '提前披露'
                advance_count += 1
            else:
                record['status'] = '按时披露'
                on_time_count += 1
        else:
            record['diff_days'] = None
            record['status'] = '未知'
        
        disclosure_records.append(record)
    
    # 计算平均延迟/提前天数
    valid_diffs = [r['diff_days'] for r in disclosure_records if r['diff_days'] is not None]
    avg_diff = sum(valid_diffs) / len(valid_diffs) if valid_diffs else None
    
    # 计算及时性评级
    timeliness_score = None
    timeliness_rating = None
    
    if valid_diffs:
        total_records = len(valid_diffs)
        weighted_score = (on_time_count * 100 + advance_count * 80 + delay_count * 20) / total_records
        timeliness_score = weighted_score
        
        if weighted_score >= 90:
            timeliness_rating = '优秀'
        elif weighted_score >= 70:
            timeliness_rating = '良好'
        elif weighted_score >= 50:
            timeliness_rating = '一般'
        else:
            timeliness_rating = '较差'
    
    return {
        'ts_code': ts_code,
        'records_analyzed': len(data),
        'disclosure_records': disclosure_records,
        'delay_count': delay_count,
        'advance_count': advance_count,
        'on_time_count': on_time_count,
        'avg_diff_days': avg_diff,
        'timeliness_score': timeliness_score,
        'timeliness_rating': timeliness_rating
    }


# 分析特定报告期的行业披露情况
async def analyze_industry_disclosure_pattern(db, end_date: str, industry_codes: Optional[List[str]] = None):
    """
    分析特定报告期的行业披露情况
    
    参数:
        db: 数据库连接对象
        end_date: 报告期（YYYYMMDD格式）
        industry_codes: 行业代码列表，为None则分析所有行业
        
    返回:
        Dict: 行业披露情况分析结果
    """
    # 构建查询条件
    filters = {'end_date': end_date}
    
    # 获取该报告期的所有披露记录
    data = await query_disclosure_date_data(
        db,
        filters=filters,
        order_by=['actual_date', 'ts_code']
    )
    
    if not data:
        return {
            'end_date': end_date,
            'message': '未找到该报告期的披露日期数据'
        }
    
    # 假设我们有行业分类信息，这里需要根据实际情况调整
    # 此处仅作示例，实际应从数据库获取股票所属行业
    # industry_map = {stock_code: industry_code, ...}
    
    # 按披露日期分组
    disclosure_date_groups = {}
    
    for item in data:
        if item.actual_date:
            date_str = item.actual_date.strftime('%Y%m%d')
            if date_str not in disclosure_date_groups:
                disclosure_date_groups[date_str] = []
            disclosure_date_groups[date_str].append(item)
    
    # 找出披露高峰期
    peak_dates = sorted(disclosure_date_groups.items(), key=lambda x: len(x[1]), reverse=True)[:5]
    
    # 计算披露时间分布
    early_period = []
    mid_period = []
    late_period = []
    
    # 假设报告期结束后的60天内为早期，60-90天为中期，90天以后为晚期
    # 对于年报可能需要调整这些阈值
    report_end_date = datetime.strptime(end_date, '%Y%m%d') if isinstance(end_date, str) else end_date
    
    for item in data:
        if item.actual_date:
            days_after_end = (item.actual_date - report_end_date).days
            if days_after_end <= 60:
                early_period.append(item)
            elif days_after_end <= 90:
                mid_period.append(item)
            else:
                late_period.append(item)
    
    return {
        'end_date': end_date,
        'total_companies': len(data),
        'disclosure_distribution': {
            'early_period': len(early_period),
            'early_percentage': len(early_period) / len(data) * 100 if data else 0,
            'mid_period': len(mid_period),
            'mid_percentage': len(mid_period) / len(data) * 100 if data else 0,
            'late_period': len(late_period),
            'late_percentage': len(late_period) / len(data) * 100 if data else 0
        },
        'peak_disclosure_dates': [
            {
                'date': date,
                'company_count': len(companies),
                'percentage': len(companies) / len(data) * 100
            }
            for date, companies in peak_dates
        ]
    }