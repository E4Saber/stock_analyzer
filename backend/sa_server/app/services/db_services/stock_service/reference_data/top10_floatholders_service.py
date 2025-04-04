import pandas as pd
from decimal import Decimal
from typing import List, Optional, Dict, Any
from app.external.tushare_api.stock.reference_data_api import get_top10_floatholders
from app.data.db_modules.stock_modules.reference_data.top10_floatholders import Top10FloatholdersData

class Top10FloatholdersService:
    """十大流通股东数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_top10_floatholders_data(self, ts_code: Optional[str] = None, 
                                     period: Optional[str] = None,
                                     ann_date: Optional[str] = None,
                                     start_date: Optional[str] = None, 
                                     end_date: Optional[str] = None,
                                     batch_size: int = 1000) -> int:
        """
        从Tushare获取十大流通股东数据并高效导入数据库
        
        参数:
            ts_code: 股票代码
            period: 报告期(YYYYMMDD格式，一般为每个季度最后一天)
            ann_date: 公告日期（YYYYMMDD格式）
            start_date: 开始日期，格式YYYYMMDD
            end_date: 结束日期，格式YYYYMMDD
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_top10_floatholders(ts_code=ts_code, period=period, ann_date=ann_date,
                                   start_date=start_date, end_date=end_date)
        
        if df_result is None or df_result.empty:
            print(f"未找到十大流通股东数据: ts_code={ts_code}, period={period}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 定义必填字段及默认值
        required_fields = {
            'ts_code': '',
            'holder_name': '',
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
            if record['ts_code'] == '' or record['holder_name'] == '' or record['end_date'] is None:
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
                # 将批次数据转换为Top10FloatholdersData对象
                holder_data_list = []
                for record in batch:
                    try:
                        # 处理数字字段，确保它们是Decimal类型
                        for key, value in record.items():
                            if isinstance(value, (float, int)) and key not in ['id']:
                                record[key] = Decimal(str(value))
                        
                        holder_data = Top10FloatholdersData(**record)
                        holder_data_list.append(holder_data)
                    except Exception as e:
                        print(f"创建Top10FloatholdersData对象失败 {record.get('ts_code', '未知')}, {record.get('end_date', '未知')}, {record.get('holder_name', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if holder_data_list:
                    inserted = await self.batch_upsert_top10_floatholders(holder_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条十大流通股东记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_top10_floatholders(self, holders_list: List[Top10FloatholdersData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            holders_list: 要插入或更新的十大流通股东数据列表
            
        返回:
            处理的记录数
        """
        if not holders_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = holders_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 使用字典来存储记录，如果有重复键，保留最新记录
        unique_records = {}
        
        for holder in holders_list:
            # 创建唯一键
            key = (holder.ts_code, str(holder.end_date), holder.holder_name)
            unique_records[key] = holder
        
        # 提取最终的唯一记录列表
        unique_holders_list = list(unique_records.values())
        
        # 准备数据
        records = []
        for holder in unique_holders_list:
            holder_dict = holder.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = holder_dict[col]
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
                    column_types = await self._get_column_type(conn, 'top10_floatholders', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_top10_floatholders (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_top10_floatholders', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'end_date', 'holder_name']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO top10_floatholders ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_top10_floatholders
                        ON CONFLICT (ts_code, end_date, holder_name) DO UPDATE SET {update_clause}
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


# 快捷函数，用于导入特定股票的十大流通股东数据
async def import_stock_top10_floatholders(db, ts_code: str, batch_size: int = 1000):
    """
    导入特定股票的十大流通股东数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = Top10FloatholdersService(db)
    count = await service.import_top10_floatholders_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条股票 {ts_code} 的十大流通股东记录")
    return count


# 快捷函数，用于导入特定公告日期的十大流通股东数据
async def import_ann_date_top10_floatholders(db, ann_date: str, batch_size: int = 1000):
    """
    导入特定公告日期的十大流通股东数据
    
    参数:
        db: 数据库连接对象
        ann_date: 公告日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = Top10FloatholdersService(db)
    count = await service.import_top10_floatholders_data(ann_date=ann_date, batch_size=batch_size)
    print(f"成功导入 {count} 条公告日期为 {ann_date} 的十大流通股东记录")
    return count


# 快捷函数，用于导入特定报告期的十大流通股东数据
async def import_period_top10_floatholders(db, period: str, batch_size: int = 1000):
    """
    导入特定报告期的十大流通股东数据
    
    参数:
        db: 数据库连接对象
        period: 报告期(每个季度最后一天的日期，比如20171231表示年报，20170630半年报，20170930三季报)
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = Top10FloatholdersService(db)
    count = await service.import_top10_floatholders_data(period=period, batch_size=batch_size)
    
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
    print(f"成功导入 {count} 条报告期为 {period_info} 的十大流通股东记录")
    return count


# 快捷函数，用于导入特定日期范围的十大流通股东数据
async def import_date_range_top10_floatholders(db, start_date: str, end_date: str, batch_size: int = 1000):
    """
    导入特定日期范围的十大流通股东数据
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期（YYYYMMDD格式）
        end_date: 结束日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = Top10FloatholdersService(db)
    count = await service.import_top10_floatholders_data(start_date=start_date, end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条日期范围为 {start_date} 至 {end_date} 的十大流通股东记录")
    return count


# 综合导入函数，支持多种参数组合
async def import_top10_floatholders_with_params(db, **kwargs):
    """
    根据提供的参数导入十大流通股东数据
    
    参数:
        db: 数据库连接对象
        **kwargs: 可包含 ts_code, period, ann_date, start_date, end_date, batch_size 等参数
        
    返回:
        导入的记录数
    """
    service = Top10FloatholdersService(db)
    batch_size = kwargs.pop('batch_size', 1000)  # 提取并移除batch_size参数
    
    # 构建参数描述
    param_desc = []
    for key, value in kwargs.items():
        if value:
            param_desc.append(f"{key}={value}")
    
    params_info = ", ".join(param_desc) if param_desc else "所有可用参数"
    
    # 导入数据
    count = await service.import_top10_floatholders_data(batch_size=batch_size, **kwargs)
    print(f"成功导入 {count} 条十大流通股东记录 ({params_info})")
    return count


# 导入所有十大流通股东数据
async def import_all_top10_floatholders(db, batch_size: int = 1000):
    """
    导入所有可获取的十大流通股东数据
    
    注意: 这可能会请求大量数据，请确保有足够的网络带宽和系统资源。
    根据数据量大小，此操作可能需要较长时间完成。
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小，默认1000条
        
    返回:
        导入的记录总数
    """
    service = Top10FloatholdersService(db)
    
    print("开始导入所有十大流通股东数据，此操作可能需要较长时间...")
    count = await service.import_top10_floatholders_data(batch_size=batch_size)
    
    print(f"成功导入所有十大流通股东数据，共 {count} 条记录")
    return count


# 动态查询十大流通股东数据
async def query_top10_floatholders_data(db, 
                                filters: Optional[Dict[str, Any]] = None, 
                                order_by: Optional[List[str]] = None,
                                limit: Optional[int] = None,
                                offset: Optional[int] = None):
    """
    动态查询十大流通股东数据，支持任意字段过滤和自定义排序
    
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
                 例如: {'ts_code__like': '600%', 'hold_ratio__gt': 5}
        order_by: 排序字段列表，字段前加"-"表示降序，例如['-end_date', 'hold_ratio']
        limit: 最大返回记录数
        offset: 跳过前面的记录数（用于分页）
        
    返回:
        List[Top10FloatholdersData]: 符合条件的十大流通股东数据列表
    
    示例:
        # 查询某股票最近一期的十大流通股东，按持股比例降序排列
        data = await query_top10_floatholders_data(
            db,
            filters={'ts_code': '000001.SZ'},
            order_by=['-end_date', '-hold_ratio'],
            limit=10
        )
        
        # 分页查询持股比例超过5%的所有股东
        data = await query_top10_floatholders_data(
            db,
            filters={'hold_ratio__gt': 5},
            order_by=['-hold_ratio', 'ts_code'],
            limit=20,
            offset=0
        )
    """
    from app.db.crud.stock_crud.reference_data.top10_floatholders_crud import Top10FloatholdersCRUD
    
    crud = Top10FloatholdersCRUD(db)
    results = await crud.get_top10_floatholders(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 查询特定公司最近几期的十大流通股东变化
async def get_top10_floatholders_history(db, ts_code: str, periods: int = 4):
    """
    查询特定公司最近几期的十大流通股东变化历史
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        periods: 查询的报告期数量
        
    返回:
        List[Top10FloatholdersData]: 按报告期降序排列的十大流通股东数据
    """
    from app.db.crud.stock_crud.reference_data.top10_floatholders_crud import Top10FloatholdersCRUD
    
    crud = Top10FloatholdersCRUD(db)
    
    # 首先获取最近几期的不同报告期
    query = """
        SELECT DISTINCT end_date
        FROM top10_floatholders
        WHERE ts_code = $1
        ORDER BY end_date DESC
        LIMIT $2
    """
    distinct_dates = await db.fetch(query, ts_code, periods)
    
    if not distinct_dates:
        return []
    
    # 获取这些报告期的所有十大流通股东数据
    date_list = [row['end_date'] for row in distinct_dates]
    results = await crud.get_top10_floatholders(
        filters={'ts_code': ts_code, 'end_date__in': date_list},
        order_by=['-end_date', '-hold_ratio']
    )
    
    return results


# 跟踪特定股东在多个公司的持股
async def track_shareholder_holdings(db, holder_name: str, end_date: Optional[str] = None, limit: int = 100):
    """
    跟踪特定股东在多个公司的持股情况
    
    参数:
        db: 数据库连接对象
        holder_name: 股东名称（支持模糊匹配）
        end_date: 报告期，格式YYYYMMDD，为None时查询最新报告期
        limit: 最大返回记录数
        
    返回:
        List[Top10FloatholdersData]: 该股东在不同公司的持股数据
    """
    filters = {'holder_name__ilike': f'%{holder_name}%'}
    
    if end_date:
        filters['end_date'] = end_date
    
    return await query_top10_floatholders_data(
        db,
        filters=filters,
        order_by=['-hold_ratio', 'ts_code'],
        limit=limit
    )


# 分析股东类型分布
async def analyze_holder_types(db, ts_code: str, end_date: Optional[str] = None):
    """
    分析特定公司十大流通股东的类型分布
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        end_date: 报告期，格式YYYYMMDD，为None时查询最新报告期
        
    返回:
        Dict: 包含股东类型分布的统计数据
    """
    # 构建查询条件
    filters = {'ts_code': ts_code}
    
    if end_date:
        filters['end_date'] = end_date
    else:
        # 如果未指定日期，获取最新报告期
        query = """
            SELECT MAX(end_date) as latest_date
            FROM top10_floatholders
            WHERE ts_code = $1
        """
        latest_date = await db.fetchval(query, ts_code)
        
        if latest_date:
            filters['end_date'] = latest_date.strftime('%Y%m%d')
    
    # 获取该报告期的十大流通股东数据
    holders_data = await query_top10_floatholders_data(
        db,
        filters=filters,
        order_by=['-hold_ratio']
    )
    
    if not holders_data:
        return {"error": "未找到符合条件的数据"}
    
    # 分析股东类型分布
    type_stats = {}
    type_holdings = {}
    total_hold_ratio = 0
    
    for holder in holders_data:
        holder_type = holder.holder_type or "未知类型"
        
        # 统计数量
        if holder_type not in type_stats:
            type_stats[holder_type] = 1
            type_holdings[holder_type] = 0
        else:
            type_stats[holder_type] += 1
        
        # 累计持股比例
        if holder.hold_ratio:
            type_holdings[holder_type] += float(holder.hold_ratio)
            total_hold_ratio += float(holder.hold_ratio)
    
    # 整理结果
    result = {
        "ts_code": ts_code,
        "end_date": filters.get('end_date', None),
        "total_holders": len(holders_data),
        "total_hold_ratio": total_hold_ratio,
        "type_distribution": {
            "by_count": type_stats,
            "by_ratio": type_holdings
        },
        "holders_data": [holder.model_dump() for holder in holders_data]
    }
    
    return result


# 检测股东持股变动
async def detect_holder_changes(db, ts_code: str, current_period: str, compare_period: str):
    """
    检测两个报告期之间的股东持股变动情况
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        current_period: 当前报告期，格式YYYYMMDD
        compare_period: 比较报告期，格式YYYYMMDD
        
    返回:
        Dict: 包含股东变动分析的结果
    """
    from app.db.crud.stock_crud.reference_data.top10_floatholders_crud import Top10FloatholdersCRUD
    
    crud = Top10FloatholdersCRUD(db)
    
    # 获取两个报告期的十大流通股东数据
    current_holders = await crud.get_top10_floatholders_by_ts_code_and_date(ts_code, current_period)
    compare_holders = await crud.get_top10_floatholders_by_ts_code_and_date(ts_code, compare_period)
    
    if not current_holders or not compare_holders:
        missing = []
        if not current_holders:
            missing.append(f"当前报告期 {current_period}")
        if not compare_holders:
            missing.append(f"比较报告期 {compare_period}")
        return {"error": f"未找到 {', '.join(missing)} 的数据"}
    
    # 构建股东名称字典
    current_dict = {h.holder_name: h for h in current_holders}
    compare_dict = {h.holder_name: h for h in compare_holders}
    
    # 分析变动情况
    new_holders = []
    exited_holders = []
    increased_holders = []
    decreased_holders = []
    unchanged_holders = []
    
    # 检查新进入和持股增加的股东
    for name, current in current_dict.items():
        if name not in compare_dict:
            new_holders.append({
                "holder_name": name,
                "current_ratio": float(current.hold_ratio) if current.hold_ratio else 0,
                "current_amount": float(current.hold_amount) if current.hold_amount else 0
            })
        else:
            compare = compare_dict[name]
            if current.hold_ratio and compare.hold_ratio:
                change = float(current.hold_ratio) - float(compare.hold_ratio)
                change_data = {
                    "holder_name": name,
                    "current_ratio": float(current.hold_ratio),
                    "previous_ratio": float(compare.hold_ratio),
                    "ratio_change": change,
                    "current_amount": float(current.hold_amount) if current.hold_amount else 0,
                    "previous_amount": float(compare.hold_amount) if compare.hold_amount else 0,
                    "amount_change": float(current.hold_amount or 0) - float(compare.hold_amount or 0)
                }
                
                if abs(change) < 0.01:
                    unchanged_holders.append(change_data)
                elif change > 0:
                    increased_holders.append(change_data)
                else:
                    decreased_holders.append(change_data)
    
    # 检查退出的股东
    for name, compare in compare_dict.items():
        if name not in current_dict:
            exited_holders.append({
                "holder_name": name,
                "previous_ratio": float(compare.hold_ratio) if compare.hold_ratio else 0,
                "previous_amount": float(compare.hold_amount) if compare.hold_amount else 0
            })
    
    # 按变动幅度排序
    increased_holders.sort(key=lambda x: x["ratio_change"], reverse=True)
    decreased_holders.sort(key=lambda x: x["ratio_change"])
    
    # 构建结果
    result = {
        "ts_code": ts_code,
        "current_period": current_period,
        "compare_period": compare_period,
        "summary": {
            "total_holders_current": len(current_holders),
            "total_holders_previous": len(compare_holders),
            "new_holders": len(new_holders),
            "exited_holders": len(exited_holders),
            "increased_holders": len(increased_holders),
            "decreased_holders": len(decreased_holders),
            "unchanged_holders": len(unchanged_holders)
        },
        "details": {
            "new_holders": new_holders,
            "exited_holders": exited_holders,
            "increased_holders": increased_holders,
            "decreased_holders": decreased_holders,
            "unchanged_holders": unchanged_holders
        }
    }
    
    return result