import pandas as pd
from decimal import Decimal
from typing import List, Optional, Dict, Any
from app.external.tushare_api.stock.reference_data_api import get_repurchase
from app.data.db_modules.stock_modules.reference_data.repurchase import RepurchaseData

class RepurchaseService:
    """股票回购数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_repurchase_data(self, ann_date: Optional[str] = None, 
                                  start_date: Optional[str] = None, 
                                  end_date: Optional[str] = None,
                                  batch_size: int = 1000) -> int:
        """
        从Tushare获取股票回购数据并高效导入数据库
        
        参数:
            ann_date: 公告日期（YYYYMMDD格式）
            start_date: 开始日期，格式YYYYMMDD
            end_date: 结束日期，格式YYYYMMDD
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_repurchase(ann_date=ann_date, start_date=start_date, end_date=end_date)
        
        if df_result is None or df_result.empty:
            print(f"未找到股票回购数据: ann_date={ann_date}, start_date={start_date}, end_date={end_date}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 定义必填字段及默认值
        required_fields = {
            'ts_code': '',
            'ann_date': None,
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
            if record['ts_code'] == '' or record['ann_date'] is None:
                continue
            
            # 处理日期格式，确保是YYYYMMDD格式
            date_fields = ['ann_date', 'end_date', 'exp_date']
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
                # 将批次数据转换为RepurchaseData对象
                repurchase_data_list = []
                for record in batch:
                    try:
                        # 处理数字字段，确保它们是Decimal类型
                        for key, value in record.items():
                            if isinstance(value, (float, int)) and key not in ['id']:
                                record[key] = Decimal(str(value))
                        
                        repurchase_data = RepurchaseData(**record)
                        repurchase_data_list.append(repurchase_data)
                    except Exception as e:
                        print(f"创建RepurchaseData对象失败 {record.get('ts_code', '未知')}, {record.get('ann_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if repurchase_data_list:
                    inserted = await self.batch_upsert_repurchase(repurchase_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条股票回购记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_repurchase(self, repurchase_list: List[RepurchaseData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            repurchase_list: 要插入或更新的股票回购数据列表
            
        返回:
            处理的记录数
        """
        if not repurchase_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = repurchase_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 使用字典来存储记录，如果有重复键，保留最新记录
        unique_records = {}
        
        for repurchase in repurchase_list:
            # 创建唯一键
            end_date_str = str(repurchase.end_date or '')
            key = (repurchase.ts_code, str(repurchase.ann_date), end_date_str)
            unique_records[key] = repurchase
        
        # 提取最终的唯一记录列表
        unique_repurchase_list = list(unique_records.values())
        
        # 准备数据
        records = []
        for repurchase in unique_repurchase_list:
            repurchase_dict = repurchase.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = repurchase_dict[col]
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
                    column_types = await self._get_column_type(conn, 'repurchase', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_repurchase (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_repurchase', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'ann_date', 'end_date']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO repurchase ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_repurchase
                        ON CONFLICT (ts_code, ann_date, end_date) DO UPDATE SET {update_clause}
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


# 快捷函数，用于导入特定公告日期的回购数据
async def import_ann_date_repurchase(db, ann_date: str, batch_size: int = 1000):
    """
    导入特定公告日期的股票回购数据
    
    参数:
        db: 数据库连接对象
        ann_date: 公告日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = RepurchaseService(db)
    count = await service.import_repurchase_data(ann_date=ann_date, batch_size=batch_size)
    print(f"成功导入 {count} 条公告日期为 {ann_date} 的股票回购记录")
    return count


# 快捷函数，用于导入特定日期范围的回购数据
async def import_date_range_repurchase(db, start_date: str, end_date: str, batch_size: int = 1000):
    """
    导入特定日期范围的股票回购数据
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期（YYYYMMDD格式）
        end_date: 结束日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = RepurchaseService(db)
    count = await service.import_repurchase_data(start_date=start_date, end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条日期范围为 {start_date} 至 {end_date} 的股票回购记录")
    return count


# 导入所有回购数据
async def import_all_repurchase(db, batch_size: int = 1000):
    """
    导入所有可获取的股票回购数据
    
    注意: 这可能会请求大量数据，请确保有足够的网络带宽和系统资源。
    根据数据量大小，此操作可能需要较长时间完成。
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小，默认1000条
        
    返回:
        导入的记录总数
    """
    service = RepurchaseService(db)
    
    print("开始导入所有股票回购数据，此操作可能需要较长时间...")
    count = await service.import_repurchase_data(batch_size=batch_size)
    
    print(f"成功导入所有股票回购数据，共 {count} 条记录")
    return count


# 动态查询回购数据
async def query_repurchase_data(db, 
                            filters: Optional[Dict[str, Any]] = None, 
                            order_by: Optional[List[str]] = None,
                            limit: Optional[int] = None,
                            offset: Optional[int] = None):
    """
    动态查询股票回购数据，支持任意字段过滤和自定义排序
    
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
                 例如: {'ts_code__like': '600%', 'amount__gt': 1000}
        order_by: 排序字段列表，字段前加"-"表示降序，例如['-ann_date', 'amount']
        limit: 最大返回记录数
        offset: 跳过前面的记录数（用于分页）
        
    返回:
        List[RepurchaseData]: 符合条件的股票回购数据列表
    
    示例:
        # 查询某支股票的回购记录
        data = await query_repurchase_data(
            db,
            filters={'ts_code': '000001.SZ'},
            order_by=['-ann_date'],
            limit=10
        )
        
        # 查询回购金额大于1亿的记录
        data = await query_repurchase_data(
            db,
            filters={'amount__gt': 100000000},
            order_by=['-amount'],
            limit=20,
            offset=0
        )
    """
    from app.db.crud.stock_crud.reference_data.repurchase_crud import RepurchaseCRUD
    
    crud = RepurchaseCRUD(db)
    results = await crud.get_repurchases(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 获取最新回购公告
async def get_latest_repurchases(db, days: int = 30, limit: int = 100):
    """
    获取最近一段时间内的回购公告
    
    参数:
        db: 数据库连接对象
        days: 最近的天数
        limit: 最大返回记录数
        
    返回:
        List[RepurchaseData]: 最近回购公告列表
    """
    query = """
        SELECT * FROM repurchase
        WHERE ann_date >= (CURRENT_DATE - $1::interval)
        ORDER BY ann_date DESC
        LIMIT $2
    """
    
    rows = await db.fetch(query, f"{days} days", limit)
    
    return [RepurchaseData.model_validate(dict(row)) for row in rows]


# 获取大额回购统计
async def get_large_repurchase_stats(db, amount_threshold: float = 100000000, limit: int = 50):
    """
    获取大额回购统计信息
    
    参数:
        db: 数据库连接对象
        amount_threshold: 金额阈值（默认1亿）
        limit: 最大返回记录数
        
    返回:
        Dict: 大额回购统计结果
    """
    # 查询大额回购记录
    query = """
        SELECT * FROM repurchase
        WHERE amount >= $1
        ORDER BY amount DESC
        LIMIT $2
    """
    
    rows = await db.fetch(query, amount_threshold, limit)
    
    if not rows:
        return {
            "count": 0,
            "total_amount": 0,
            "message": f"未找到金额大于 {amount_threshold} 的回购记录"
        }
    
    # 转换为RepurchaseData对象
    large_repurchases = [RepurchaseData.model_validate(dict(row)) for row in rows]
    
    # 计算统计数据
    total_amount = sum(float(repurchase.amount or 0) for repurchase in large_repurchases)
    
    # 按公司分组统计
    company_stats = {}
    for repurchase in large_repurchases:
        if repurchase.ts_code not in company_stats:
            company_stats[repurchase.ts_code] = {
                "count": 0,
                "total_amount": 0,
                "latest_ann_date": None
            }
        
        company_stats[repurchase.ts_code]["count"] += 1
        company_stats[repurchase.ts_code]["total_amount"] += float(repurchase.amount or 0)
        
        if company_stats[repurchase.ts_code]["latest_ann_date"] is None or repurchase.ann_date > company_stats[repurchase.ts_code]["latest_ann_date"]:
            company_stats[repurchase.ts_code]["latest_ann_date"] = repurchase.ann_date
    
    # 构建结果
    result = {
        "count": len(large_repurchases),
        "total_amount": total_amount,
        "average_amount": total_amount / len(large_repurchases),
        "company_count": len(company_stats),
        "top_companies": sorted(
            [{"ts_code": ts_code, **stats} for ts_code, stats in company_stats.items()],
            key=lambda x: x["total_amount"],
            reverse=True
        )[:10],  # 前10家公司
        "repurchases": [repurchase.model_dump() for repurchase in large_repurchases[:10]]  # 前10条记录
    }
    
    return result


# 分析股票回购进度
async def analyze_repurchase_progress(db, ts_code: Optional[str] = None, limit: int = 100):
    """
    分析股票回购进度情况
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码（可选，为None时分析所有股票）
        limit: 最大返回记录数
        
    返回:
        Dict: 回购进度分析结果
    """
    # 构建查询条件
    where_clause = ""
    params = []
    
    if ts_code:
        where_clause = "WHERE ts_code = $1"
        params.append(ts_code)
    
    # 查询最新回购记录
    query = f"""
        WITH latest_records AS (
            SELECT ts_code, MAX(ann_date) as latest_ann_date
            FROM repurchase
            {where_clause}
            GROUP BY ts_code
        )
        SELECT r.* 
        FROM repurchase r
        JOIN latest_records lr ON r.ts_code = lr.ts_code AND r.ann_date = lr.latest_ann_date
        ORDER BY r.ann_date DESC
        LIMIT ${{1 if ts_code else 2}}
    """
    
    params.append(limit)
    rows = await db.fetch(query, *params)
    
    if not rows:
        return {
            "count": 0,
            "message": f"未找到{'股票 ' + ts_code if ts_code else '任何'}回购记录"
        }
    
    # 转换为RepurchaseData对象
    repurchase_records = [RepurchaseData.model_validate(dict(row)) for row in rows]
    
    # 分析进度情况
    progress_stats = {
        "进行中": 0,
        "已完成": 0,
        "已到期": 0,
        "其他状态": 0
    }
    
    for record in repurchase_records:
        if record.proc:
            status = None
            if "完成" in record.proc:
                status = "已完成"
            elif "进行" in record.proc:
                status = "进行中"
            elif "到期" in record.proc or "截止" in record.proc:
                status = "已到期"
            else:
                status = "其他状态"
            
            progress_stats[status] += 1
    
    # 构建结果
    result = {
        "count": len(repurchase_records),
        "progress_stats": progress_stats,
        "repurchases": [record.model_dump() for record in repurchase_records[:10]]  # 前10条记录
    }
    
    if ts_code:
        result["ts_code"] = ts_code
    
    return result


# 分析回购金额与回购价格范围
async def analyze_repurchase_price_range(db, ts_code: Optional[str] = None, limit: int = 100):
    """
    分析股票回购的价格范围与金额
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码（可选，为None时分析所有股票）
        limit: 最大返回记录数
        
    返回:
        Dict: 回购价格范围与金额分析结果
    """
    # 构建查询条件
    conditions = []
    params = []
    param_idx = 1
    
    if ts_code:
        conditions.append(f"ts_code = ${param_idx}")
        params.append(ts_code)
        param_idx += 1
    
    # 需要有价格范围和金额
    conditions.extend([
        "high_limit IS NOT NULL", 
        "low_limit IS NOT NULL", 
        "amount IS NOT NULL"
    ])
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    # 查询回购记录
    query = f"""
        SELECT * FROM repurchase
        {where_clause}
        ORDER BY ann_date DESC
        LIMIT ${param_idx}
    """
    
    params.append(limit)
    rows = await db.fetch(query, *params)
    
    if not rows:
        return {
            "count": 0,
            "message": f"未找到{'股票 ' + ts_code if ts_code else '任何'}符合条件的回购记录"
        }
    
    # 转换为RepurchaseData对象
    repurchase_records = [RepurchaseData.model_validate(dict(row)) for row in rows]
    
    # 计算统计数据
    total_amount = sum(float(record.amount or 0) for record in repurchase_records)
    avg_amount = total_amount / len(repurchase_records)
    
    price_ranges = []
    for record in repurchase_records:
        if record.high_limit and record.low_limit:
            high = float(record.high_limit)
            low = float(record.low_limit)
            price_range = high - low
            range_percent = (price_range / low) * 100 if low > 0 else 0
            
            price_ranges.append({
                "ts_code": record.ts_code,
                "ann_date": str(record.ann_date),
                "high_limit": high,
                "low_limit": low,
                "price_range": price_range,
                "range_percent": range_percent,
                "amount": float(record.amount) if record.amount else 0
            })
    
    # 按价格范围百分比排序
    price_ranges.sort(key=lambda x: x["range_percent"], reverse=True)
    
    # 构建结果
    result = {
        "count": len(repurchase_records),
        "total_amount": total_amount,
        "average_amount": avg_amount,
        "price_range_stats": {
            "max_range_percent": max(r["range_percent"] for r in price_ranges) if price_ranges else 0,
            "min_range_percent": min(r["range_percent"] for r in price_ranges) if price_ranges else 0,
            "avg_range_percent": sum(r["range_percent"] for r in price_ranges) / len(price_ranges) if price_ranges else 0
        },
        "price_ranges": price_ranges[:10]  # 前10条记录
    }
    
    if ts_code:
        result["ts_code"] = ts_code
    
    return result