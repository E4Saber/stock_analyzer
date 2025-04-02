import pandas as pd
from decimal import Decimal
from typing import List, Optional, Dict, Any
from app.external.tushare_api.financial_info_api import get_fina_audit
from app.data.db_modules.stock_modules.stock_financial.fina_audit import FinaAuditData
from app.db.crud.stock_crud.stock_financial.fina_audit_crud import FinaAuditCRUD

class FinaAuditService:
    """财务审计数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_fina_audit_data(self, ts_code: Optional[str] = None, 
                                  ann_date: Optional[str] = None,
                                  start_date: Optional[str] = None, 
                                  end_date: Optional[str] = None,
                                  period: Optional[str] = None,
                                  batch_size: int = 1000) -> int:
        """
        从Tushare获取财务审计数据并高效导入数据库
        
        参数:
            ts_code: 股票代码
            ann_date: 公告日期（YYYYMMDD格式）
            start_date: 公告开始日期（YYYYMMDD格式）
            end_date: 公告结束日期（YYYYMMDD格式）
            period: 报告期(YYYYMMDD格式，每个季度最后一天的日期，比如20171231表示年报)
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_fina_audit(ts_code=ts_code, ann_date=ann_date,
                                start_date=start_date, end_date=end_date,
                                period=period)
        
        if df_result is None or df_result.empty:
            print(f"未找到财务审计数据: ts_code={ts_code}, period={period}")
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
                # 将批次数据转换为FinaAuditData对象
                fina_audit_data_list = []
                for record in batch:
                    try:
                        # 处理数字字段，确保它们是Decimal类型
                        if 'audit_fees' in record and record['audit_fees'] is not None and isinstance(record['audit_fees'], (float, int)):
                            record['audit_fees'] = Decimal(str(record['audit_fees']))
                        
                        fina_audit_data = FinaAuditData(**record)
                        fina_audit_data_list.append(fina_audit_data)
                    except Exception as e:
                        print(f"创建FinaAuditData对象失败 {record.get('ts_code', '未知')}, {record.get('end_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if fina_audit_data_list:
                    inserted = await self.batch_upsert_fina_audit(fina_audit_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条财务审计记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_fina_audit(self, fina_audit_list: List[FinaAuditData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            fina_audit_list: 要插入或更新的财务审计数据列表
            
        返回:
            处理的记录数
        """
        if not fina_audit_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = fina_audit_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 使用字典来存储记录，避免重复
        unique_records = {}
        
        for fina_audit in fina_audit_list:
            # 创建唯一键
            key = (fina_audit.ts_code, str(fina_audit.end_date))
            
            # 如果键不存在，或者当前记录比已存在的记录更新（以公告日期为准），则更新
            if key not in unique_records or (fina_audit.ann_date and (not unique_records[key].ann_date or fina_audit.ann_date > unique_records[key].ann_date)):
                unique_records[key] = fina_audit
                print(f"保留记录: {fina_audit.ts_code}, {fina_audit.end_date}")
            else:
                print(f"跳过记录: {fina_audit.ts_code}, {fina_audit.end_date}, 已存在更新的记录")
        
        # 提取最终的唯一记录列表
        unique_fina_audit_list = list(unique_records.values())
        
        # 准备数据
        records = []
        for fina_audit in unique_fina_audit_list:
            fina_audit_dict = fina_audit.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = fina_audit_dict[col]
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
                    column_types = await self._get_column_type(conn, 'fina_audit', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_fina_audit (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_fina_audit', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'end_date']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO fina_audit ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_fina_audit
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


# 快捷函数，用于导入特定股票的财务审计数据
async def import_stock_fina_audit(db, ts_code: str, batch_size: int = 1000):
    """
    导入特定股票的财务审计数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = FinaAuditService(db)
    count = await service.import_fina_audit_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条股票 {ts_code} 的财务审计记录")
    return count


# 快捷函数，用于导入特定公告日期的财务审计数据
async def import_ann_date_fina_audit(db, ann_date: str, batch_size: int = 1000):
    """
    导入特定公告日期的财务审计数据
    
    参数:
        db: 数据库连接对象
        ann_date: 公告日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = FinaAuditService(db)
    count = await service.import_fina_audit_data(ann_date=ann_date, batch_size=batch_size)
    print(f"成功导入 {count} 条公告日期为 {ann_date} 的财务审计记录")
    return count


# 快捷函数，用于导入特定公告日期范围的财务审计数据
async def import_date_range_fina_audit(db, start_date: str, end_date: str, batch_size: int = 1000):
    """
    导入特定公告日期范围的财务审计数据
    
    参数:
        db: 数据库连接对象
        start_date: 公告开始日期（YYYYMMDD格式）
        end_date: 公告结束日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = FinaAuditService(db)
    count = await service.import_fina_audit_data(start_date=start_date, end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条公告日期在 {start_date} 至 {end_date} 之间的财务审计记录")
    return count


# 快捷函数，用于导入特定报告期的财务审计数据
async def import_period_fina_audit(db, period: str, batch_size: int = 1000):
    """
    导入特定报告期的财务审计数据
    
    参数:
        db: 数据库连接对象
        period: 报告期(每个季度最后一天的日期，比如20171231表示年报)
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = FinaAuditService(db)
    count = await service.import_fina_audit_data(period=period, batch_size=batch_size)
    
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
    print(f"成功导入 {count} 条报告期为 {period_info} 的财务审计记录")
    return count


# 综合导入函数，支持多种参数组合
async def import_fina_audit_with_params(db, **kwargs):
    """
    根据提供的参数导入财务审计数据
    
    参数:
        db: 数据库连接对象
        **kwargs: 可包含 ts_code, ann_date, start_date, end_date, period, batch_size 等参数
        
    返回:
        导入的记录数
    """
    service = FinaAuditService(db)
    batch_size = kwargs.pop('batch_size', 1000)  # 提取并移除batch_size参数
    
    # 构建参数描述
    param_desc = []
    for key, value in kwargs.items():
        if value:
            param_desc.append(f"{key}={value}")
    
    params_info = ", ".join(param_desc) if param_desc else "所有可用参数"
    
    # 导入数据
    count = await service.import_fina_audit_data(batch_size=batch_size, **kwargs)
    print(f"成功导入 {count} 条财务审计记录 ({params_info})")
    return count


# 导入所有财务审计数据
async def import_all_fina_audit(db, batch_size: int = 1000):
    """
    导入所有可获取的财务审计数据
    
    注意: 这可能会请求大量数据，请确保有足够的网络带宽和系统资源。
    根据数据量大小，此操作可能需要较长时间完成。
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小，默认1000条
        
    返回:
        导入的记录总数
    """
    service = FinaAuditService(db)
    
    print("开始导入所有财务审计数据，此操作可能需要较长时间...")
    count = await service.import_fina_audit_data(batch_size=batch_size)
    
    print(f"成功导入所有财务审计数据，共 {count} 条记录")
    return count


# 动态查询财务审计数据
async def query_fina_audit_data(db, 
                             filters: Optional[Dict[str, Any]] = None, 
                             order_by: Optional[List[str]] = None,
                             limit: Optional[int] = None,
                             offset: Optional[int] = None):
    """
    动态查询财务审计数据，支持任意字段过滤和自定义排序
    
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
        List[FinaAuditData]: 符合条件的财务审计数据列表
    
    示例:
        # 查询某股票最近的财务审计记录
        data = await query_fina_audit_data(
            db,
            filters={'ts_code': '000001.SZ'},
            order_by=['-end_date']
        )
        
        # 查询特定会计事务所的审计记录
        data = await query_fina_audit_data(
            db,
            filters={'audit_agency__like': '%普华永道%'},
            order_by=['-end_date', 'ts_code'],
            limit=20,
            offset=0
        )
    """
    crud = FinaAuditCRUD(db)
    results = await crud.get_fina_audit(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 查询特定公司的审计历史
async def get_company_audit_history(db, ts_code: str, start_date: str = None, end_date: str = None, limit: int = 20):
    """
    查询特定公司的审计历史记录
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        start_date: 开始日期，格式YYYYMMDD
        end_date: 结束日期，格式YYYYMMDD
        limit: 最大返回记录数
        
    返回:
        List[FinaAuditData]: 该公司的审计历史数据，按报告期降序排列
    """
    filters = {'ts_code': ts_code}
    
    if start_date:
        filters['end_date__ge'] = start_date
    
    if end_date:
        filters['end_date__le'] = end_date
    
    return await query_fina_audit_data(
        db,
        filters=filters,
        order_by=['-end_date'],
        limit=limit
    )


# 查询会计事务所的审计客户
async def get_audit_agency_clients(db, audit_agency: str, end_date: str = None, limit: int = 100):
    """
    查询特定会计事务所的审计客户
    
    参数:
        db: 数据库连接对象
        audit_agency: 会计事务所名称（支持模糊匹配）
        end_date: 特定报告期，格式YYYYMMDD
        limit: 最大返回记录数
        
    返回:
        List[FinaAuditData]: 该会计事务所的审计记录
    """
    filters = {'audit_agency__ilike': f'%{audit_agency}%'}
    
    if end_date:
        filters['end_date'] = end_date
    
    return await query_fina_audit_data(
        db,
        filters=filters,
        order_by=['-end_date', 'ts_code'],
        limit=limit
    )


# 分析公司审计费用变化
async def analyze_audit_fees_trend(db, ts_code: str, periods: int = 5):
    """
    分析公司审计费用的历年变化趋势
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        periods: 分析的报告期数量
        
    返回:
        Dict: 审计费用分析结果，包括变化趋势和会计师事务所变更情况
    """
    # 获取公司的财务审计数据，按报告期降序排序
    audit_data = await query_fina_audit_data(
        db,
        filters={'ts_code': ts_code},
        order_by=['-end_date'],
        limit=periods
    )
    
    if not audit_data or len(audit_data) < 2:
        return {
            'ts_code': ts_code,
            'status': 'insufficient_data',
            'message': '数据不足，无法分析趋势'
        }
    
    # 提取年报数据
    year_data = []
    for item in audit_data:
        if item.end_date and item.end_date.month == 12 and item.end_date.day == 31:
            year_data.append({
                'year': item.end_date.year,
                'end_date': item.end_date,
                'audit_fees': item.audit_fees,
                'audit_agency': item.audit_agency,
                'audit_sign': item.audit_sign,
                'audit_result': item.audit_result
            })
    
    # 按年份排序
    year_data.sort(key=lambda x: x['year'], reverse=True)
    
    # 分析审计费用变化
    fees_changes = []
    for i in range(1, len(year_data)):
        current = year_data[i-1]
        previous = year_data[i]
        
        if current['audit_fees'] is not None and previous['audit_fees'] is not None and previous['audit_fees'] != 0:
            change_pct = float((current['audit_fees'] - previous['audit_fees']) / previous['audit_fees'] * 100)
            fees_changes.append({
                'from_year': previous['year'],
                'to_year': current['year'],
                'from_fees': previous['audit_fees'],
                'to_fees': current['audit_fees'],
                'change_pct': change_pct
            })
    
    # 分析会计师事务所变更
    agency_changes = []
    for i in range(1, len(year_data)):
        current = year_data[i-1]
        previous = year_data[i]
        
        if current['audit_agency'] != previous['audit_agency']:
            agency_changes.append({
                'year': current['year'],
                'from_agency': previous['audit_agency'],
                'to_agency': current['audit_agency']
            })
    
    # 计算平均审计费用
    valid_fees = [item['audit_fees'] for item in year_data if item['audit_fees'] is not None]
    avg_fees = sum(valid_fees) / len(valid_fees) if valid_fees else None
    
    # 计算年均变化率
    avg_change_pct = sum(item['change_pct'] for item in fees_changes) / len(fees_changes) if fees_changes else None
    
    return {
        'ts_code': ts_code,
        'years_analyzed': len(year_data),
        'yearly_data': year_data,
        'fees_changes': fees_changes,
        'agency_changes': agency_changes,
        'avg_fees': avg_fees,
        'avg_annual_change_pct': avg_change_pct,
        'agency_change_count': len(agency_changes),
        'has_consistent_agency': len(agency_changes) == 0
    }


# 统计会计事务所市场份额
async def analyze_audit_agencies_market_share(db, year: int, top_n: int = 20):
    """
    分析会计事务所的市场份额统计
    
    参数:
        db: 数据库连接对象
        year: 分析的年份
        top_n: 返回前N家会计事务所
        
    返回:
        Dict: 会计事务所市场份额分析结果
    """
    # 构建日期范围查询条件
    start_date = f"{year}0101"
    end_date = f"{year}1231"
    
    # 获取该年度的所有审计记录
    audit_data = await query_fina_audit_data(
        db,
        filters={
            'end_date__ge': start_date,
            'end_date__le': end_date
        },
        limit=10000  # 设置较大的限制，以获取足够的数据
    )
    
    if not audit_data:
        return {
            'year': year,
            'status': 'no_data',
            'message': f'未找到{year}年的审计数据'
        }
    
    # 按会计事务所分组统计
    agency_stats = {}
    total_clients = 0
    total_fees = Decimal('0')
    
    for item in audit_data:
        agency = item.audit_agency if item.audit_agency else '未知'
        
        if agency not in agency_stats:
            agency_stats[agency] = {
                'name': agency,
                'client_count': 0,
                'total_fees': Decimal('0'),
                'clients': []
            }
        
        agency_stats[agency]['client_count'] += 1
        total_clients += 1
        
        if item.audit_fees:
            agency_stats[agency]['total_fees'] += item.audit_fees
            total_fees += item.audit_fees
        
        agency_stats[agency]['clients'].append({
            'ts_code': item.ts_code,
            'audit_fees': item.audit_fees
        })
    
    # 计算市场份额并排序
    agency_list = []
    for agency, stats in agency_stats.items():
        stats['client_share'] = stats['client_count'] / total_clients * 100 if total_clients > 0 else 0
        stats['fees_share'] = stats['total_fees'] / total_fees * 100 if total_fees > 0 else 0
        stats['avg_fees'] = stats['total_fees'] / stats['client_count'] if stats['client_count'] > 0 else 0
        agency_list.append(stats)
    
    # 按客户数量排序
    agency_list.sort(key=lambda x: x['client_count'], reverse=True)
    top_agencies = agency_list[:top_n]
    
    # 计算前N家的总体份额
    top_client_count = sum(agency['client_count'] for agency in top_agencies)
    top_fees = sum(agency['total_fees'] for agency in top_agencies)
    
    top_client_share = top_client_count / total_clients * 100 if total_clients > 0 else 0
    top_fees_share = top_fees / total_fees * 100 if total_fees > 0 else 0
    
    return {
        'year': year,
        'total_records': len(audit_data),
        'total_clients': total_clients,
        'total_fees': float(total_fees),
        'agency_count': len(agency_stats),
        'top_agencies': top_agencies,
        'top_client_share': top_client_share,
        'top_fees_share': top_fees_share
    }