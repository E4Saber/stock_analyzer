import pandas as pd
from decimal import Decimal
from typing import List, Optional, Dict, Any
from app.external.tushare_api.stock.reference_data_api import get_share_float
from app.data.db_modules.stock_modules.reference_data.share_float import ShareFloatData

class ShareFloatService:
    """限售股解禁数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_share_float_data(self, ts_code: Optional[str] = None, 
                                   ann_date: Optional[str] = None, 
                                   float_date: Optional[str] = None,
                                   start_date: Optional[str] = None, 
                                   end_date: Optional[str] = None,
                                   batch_size: int = 1000) -> int:
        """
        从Tushare获取限售股解禁数据并高效导入数据库
        
        参数:
            ts_code: 股票代码
            ann_date: 公告日期（YYYYMMDD格式）
            float_date: 解禁日期（YYYYMMDD格式）
            start_date: 解禁开始日期，格式YYYYMMDD
            end_date: 解禁结束日期，格式YYYYMMDD
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_share_float(ts_code=ts_code, ann_date=ann_date, float_date=float_date,
                                 start_date=start_date, end_date=end_date)
        
        if df_result is None or df_result.empty:
            print(f"未找到限售股解禁数据: ts_code={ts_code}, ann_date={ann_date}, float_date={float_date}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 定义必填字段及默认值
        required_fields = {
            'ts_code': '',
            'float_date': None
        }
        
        # 处理数据并确保所有必填字段都有值
        valid_records = []
        for record in records:
            # 确保必填字段存在且有值
            for field, default_value in required_fields.items():
                if field not in record or record[field] is None or (isinstance(record[field], str) and record[field] == ''):
                    record[field] = default_value
            
            # 如果缺少关键字段，跳过该记录
            if record['ts_code'] == '' or record['float_date'] is None:
                continue
            
            # 处理日期格式，确保是YYYYMMDD格式
            date_fields = ['ann_date', 'float_date']
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
                # 将批次数据转换为ShareFloatData对象
                share_float_data_list = []
                for record in batch:
                    try:
                        # 处理数字字段，确保它们是Decimal类型
                        for key, value in record.items():
                            if isinstance(value, (float, int)) and key not in ['id']:
                                record[key] = Decimal(str(value))
                        
                        share_float_data = ShareFloatData(**record)
                        share_float_data_list.append(share_float_data)
                    except Exception as e:
                        print(f"创建ShareFloatData对象失败 {record.get('ts_code', '未知')}, {record.get('float_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if share_float_data_list:
                    inserted = await self.batch_upsert_share_float(share_float_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条限售股解禁记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_share_float(self, share_float_list: List[ShareFloatData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            share_float_list: 要插入或更新的限售股解禁数据列表
            
        返回:
            处理的记录数
        """
        if not share_float_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = share_float_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 使用字典来存储记录，如果有重复键，保留最新记录
        unique_records = {}
        
        for share_float in share_float_list:
            # 创建唯一键
            holder_name = share_float.holder_name or ''
            key = (share_float.ts_code, str(share_float.ann_date or ''), str(share_float.float_date), holder_name)
            unique_records[key] = share_float
        
        # 提取最终的唯一记录列表
        unique_share_float_list = list(unique_records.values())
        
        # 准备数据
        records = []
        for share_float in unique_share_float_list:
            share_float_dict = share_float.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = share_float_dict[col]
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
                    column_types = await self._get_column_type(conn, 'share_float', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_share_float (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_share_float', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'ann_date', 'float_date', 'holder_name']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO share_float ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_share_float
                        ON CONFLICT (ts_code, ann_date, float_date, holder_name) DO UPDATE SET {update_clause}
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


# 快捷函数，用于导入特定股票的限售股解禁数据
async def import_stock_share_float(db, ts_code: str, batch_size: int = 1000):
    """
    导入特定股票的限售股解禁数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = ShareFloatService(db)
    count = await service.import_share_float_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条股票 {ts_code} 的限售股解禁记录")
    return count


# 快捷函数，用于导入特定公告日期的限售股解禁数据
async def import_ann_date_share_float(db, ann_date: str, batch_size: int = 1000):
    """
    导入特定公告日期的限售股解禁数据
    
    参数:
        db: 数据库连接对象
        ann_date: 公告日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = ShareFloatService(db)
    count = await service.import_share_float_data(ann_date=ann_date, batch_size=batch_size)
    print(f"成功导入 {count} 条公告日期为 {ann_date} 的限售股解禁记录")
    return count


# 快捷函数，用于导入特定解禁日期的限售股解禁数据
async def import_float_date_share_float(db, float_date: str, batch_size: int = 1000):
    """
    导入特定解禁日期的限售股解禁数据
    
    参数:
        db: 数据库连接对象
        float_date: 解禁日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = ShareFloatService(db)
    count = await service.import_share_float_data(float_date=float_date, batch_size=batch_size)
    print(f"成功导入 {count} 条解禁日期为 {float_date} 的限售股解禁记录")
    return count


# 快捷函数，用于导入特定日期范围的限售股解禁数据
async def import_date_range_share_float(db, start_date: str, end_date: str, batch_size: int = 1000):
    """
    导入特定日期范围的限售股解禁数据
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期（YYYYMMDD格式）
        end_date: 结束日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = ShareFloatService(db)
    count = await service.import_share_float_data(start_date=start_date, end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条日期范围为 {start_date} 至 {end_date} 的限售股解禁记录")
    return count


# 综合导入函数，支持多种参数组合
async def import_share_float_with_params(db, **kwargs):
    """
    根据提供的参数导入限售股解禁数据
    
    参数:
        db: 数据库连接对象
        **kwargs: 可包含 ts_code, ann_date, float_date, start_date, end_date, batch_size 等参数
        
    返回:
        导入的记录数
    """
    service = ShareFloatService(db)
    batch_size = kwargs.pop('batch_size', 1000)  # 提取并移除batch_size参数
    
    # 构建参数描述
    param_desc = []
    for key, value in kwargs.items():
        if value:
            param_desc.append(f"{key}={value}")
    
    params_info = ", ".join(param_desc) if param_desc else "所有可用参数"
    
    # 导入数据
    count = await service.import_share_float_data(batch_size=batch_size, **kwargs)
    print(f"成功导入 {count} 条限售股解禁记录 ({params_info})")
    return count


# 动态查询限售股解禁数据
async def query_share_float_data(db, 
                            filters: Optional[Dict[str, Any]] = None, 
                            order_by: Optional[List[str]] = None,
                            limit: Optional[int] = None,
                            offset: Optional[int] = None):
    """
    动态查询限售股解禁数据，支持任意字段过滤和自定义排序
    
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
                 例如: {'ts_code__like': '600%', 'float_ratio__gt': 5}
        order_by: 排序字段列表，字段前加"-"表示降序，例如['-float_date', 'float_ratio']
        limit: 最大返回记录数
        offset: 跳过前面的记录数（用于分页）
        
    返回:
        List[ShareFloatData]: 符合条件的限售股解禁数据列表
    
    示例:
        # 查询某支股票的解禁记录
        data = await query_share_float_data(
            db,
            filters={'ts_code': '000001.SZ'},
            order_by=['-float_date'],
            limit=10
        )
        
        # 查询高比例解禁记录
        data = await query_share_float_data(
            db,
            filters={'float_ratio__gt': 5},
            order_by=['-float_ratio'],
            limit=20,
            offset=0
        )
    """
    from app.db.crud.stock_crud.reference_data.share_float_crud import ShareFloatCRUD
    
    crud = ShareFloatCRUD(db)
    results = await crud.get_share_floats(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 获取即将到来的解禁统计
async def get_upcoming_share_floats(db, days: int = 30, limit: int = 100):
    """
    获取未来一段时间内的解禁统计信息
    
    参数:
        db: 数据库连接对象
        days: 未来的天数
        limit: 最大返回记录数
        
    返回:
        Dict: 未来解禁统计信息
    """
    query = """
        SELECT * FROM share_float
        WHERE float_date BETWEEN CURRENT_DATE AND (CURRENT_DATE + $1::interval)
        ORDER BY float_date, float_ratio DESC
        LIMIT $2
    """
    
    rows = await db.fetch(query, f"{days} days", limit)
    
    if not rows:
        return {
            "count": 0,
            "total_ratio": 0,
            "message": f"未来 {days} 天内无解禁记录"
        }
    
    # 转换为ShareFloatData对象
    share_floats = [ShareFloatData.model_validate(dict(row)) for row in rows]
    
    # 按日期分组
    date_groups = {}
    for float_data in share_floats:
        float_date_str = float_data.float_date.strftime('%Y-%m-%d') if float_data.float_date else 'Unknown'
        
        if float_date_str not in date_groups:
            date_groups[float_date_str] = {
                "date": float_date_str,
                "count": 0,
                "total_share": 0,
                "total_ratio": 0,
                "details": []
            }
        
        date_groups[float_date_str]["count"] += 1
        date_groups[float_date_str]["total_share"] += float(float_data.float_share or 0)
        date_groups[float_date_str]["total_ratio"] += float(float_data.float_ratio or 0)
        date_groups[float_date_str]["details"].append({
            "ts_code": float_data.ts_code,
            "holder_name": float_data.holder_name,
            "float_share": float(float_data.float_share or 0),
            "float_ratio": float(float_data.float_ratio or 0),
            "share_type": float_data.share_type
        })
    
    # 计算总体统计
    total_count = len(share_floats)
    total_share = sum(float(float_data.float_share or 0) for float_data in share_floats)
    total_ratio = sum(float(float_data.float_ratio or 0) for float_data in share_floats)
    
    # 按日期排序
    date_summary = sorted(date_groups.values(), key=lambda x: x["date"])
    
    # 构建结果
    result = {
        "period": f"未来{days}天",
        "count": total_count,
        "total_share": total_share,
        "total_ratio": total_ratio,
        "by_date": date_summary
    }
    
    return result


# 获取大比例解禁记录
async def get_large_ratio_share_floats(db, ratio_threshold: float = 5.0, limit: int = 50):
    """
    获取高比例解禁统计信息
    
    参数:
        db: 数据库连接对象
        ratio_threshold: 比例阈值（默认5%）
        limit: 最大返回记录数
        
    返回:
        Dict: 高比例解禁统计结果
    """
    query = """
        SELECT * FROM share_float
        WHERE float_ratio >= $1
        ORDER BY float_ratio DESC
        LIMIT $2
    """
    
    rows = await db.fetch(query, ratio_threshold, limit)
    
    if not rows:
        return {
            "count": 0,
            "message": f"未找到比例大于 {ratio_threshold}% 的解禁记录"
        }
    
    # 转换为ShareFloatData对象
    share_floats = [ShareFloatData.model_validate(dict(row)) for row in rows]
    
    # 计算统计数据
    total_share = sum(float(float_data.float_share or 0) for float_data in share_floats)
    avg_ratio = sum(float(float_data.float_ratio or 0) for float_data in share_floats) / len(share_floats)
    
    # 构建结果
    result = {
        "threshold": f"{ratio_threshold}%",
        "count": len(share_floats),
        "total_share": total_share,
        "average_ratio": avg_ratio,
        "records": [
            {
                "ts_code": float_data.ts_code,
                "float_date": float_data.float_date.strftime('%Y-%m-%d') if float_data.float_date else None,
                "holder_name": float_data.holder_name,
                "float_share": float(float_data.float_share or 0),
                "float_ratio": float(float_data.float_ratio or 0),
                "share_type": float_data.share_type
            }
            for float_data in share_floats[:10]  # 只返回前10条详细记录
        ]
    }
    
    return result


# 分析股东解禁情况
async def analyze_holder_share_floats(db, holder_name: str, limit: int = 100):
    """
    分析特定股东的限售股解禁情况
    
    参数:
        db: 数据库连接对象
        holder_name: 股东名称（支持模糊匹配）
        limit: 最大返回记录数
        
    返回:
        Dict: 股东解禁分析结果
    """
    query = """
        SELECT * FROM share_float
        WHERE holder_name ILIKE $1
        ORDER BY float_date DESC
        LIMIT $2
    """
    
    rows = await db.fetch(query, f"%{holder_name}%", limit)
    
    if not rows:
        return {
            "count": 0,
            "message": f"未找到股东名称包含 '{holder_name}' 的解禁记录"
        }
    
    # 转换为ShareFloatData对象
    share_floats = [ShareFloatData.model_validate(dict(row)) for row in rows]
    
    # 按股票分组
    stock_groups = {}
    for float_data in share_floats:
        if float_data.ts_code not in stock_groups:
            stock_groups[float_data.ts_code] = []
        
        stock_groups[float_data.ts_code].append({
            "float_date": float_data.float_date.strftime('%Y-%m-%d') if float_data.float_date else None,
            "ann_date": float_data.ann_date.strftime('%Y-%m-%d') if float_data.ann_date else None,
            "float_share": float(float_data.float_share or 0),
            "float_ratio": float(float_data.float_ratio or 0),
            "share_type": float_data.share_type
        })
    
    # 计算总体统计
    total_share = sum(float(float_data.float_share or 0) for float_data in share_floats)
    
    # 构建结果
    result = {
        "holder_name": holder_name,
        "count": len(share_floats),
        "stock_count": len(stock_groups),
        "total_share": total_share,
        "by_stock": [
            {
                "ts_code": ts_code,
                "float_count": len(records),
                "total_share": sum(record["float_share"] for record in records),
                "records": sorted(records, key=lambda x: x["float_date"] if x["float_date"] else "", reverse=True)
            }
            for ts_code, records in stock_groups.items()
        ]
    }
    
    return result


# 分析解禁流通对股价的影响
async def analyze_float_impact(db, ts_code: str, days_before: int = 30, days_after: int = 30):
    """
    分析限售股解禁对股价的影响
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        days_before: 解禁前的天数
        days_after: 解禁后的天数
        
    返回:
        Dict: 解禁影响分析结果
    """
    # 查询该股票的解禁记录
    float_query = """
        SELECT * FROM share_float
        WHERE ts_code = $1
        ORDER BY float_date DESC
    """
    
    float_rows = await db.fetch(float_query, ts_code)
    
    if not float_rows:
        return {
            "ts_code": ts_code,
            "message": f"未找到股票 {ts_code} 的解禁记录"
        }
    
    # 转换为ShareFloatData对象
    share_floats = [ShareFloatData.model_validate(dict(row)) for row in float_rows]
    
    # 查询股价数据（假设有daily_basic表存储日线数据）
    # 注意：实际项目中需要根据具体的数据表结构调整此查询
    price_query = """
        SELECT trade_date, close, pct_chg
        FROM daily_basic
        WHERE ts_code = $1
        ORDER BY trade_date
    """
    
    price_rows = await db.fetch(price_query, ts_code)
    
    if not price_rows:
        return {
            "ts_code": ts_code,
            "float_count": len(share_floats),
            "message": f"未找到股票 {ts_code} 的价格数据，无法分析影响"
        }
    
    # 构建日期到价格的映射
    date_to_price = {
        row['trade_date'].strftime('%Y-%m-%d'): {
            'close': float(row['close']),
            'pct_chg': float(row['pct_chg'])
        }
        for row in price_rows if row['close'] is not None
    }
    
    # 分析每次解禁的影响
    impacts = []
    for float_data in share_floats:
        if not float_data.float_date:
            continue
            
        float_date_str = float_data.float_date.strftime('%Y-%m-%d')
        
        # 查找解禁日的股价
        float_price = date_to_price.get(float_date_str)
        if not float_price:
            continue
            
        # 查找解禁前后的价格变化
        before_dates = []
        after_dates = []
        
        # 构建日期列表
        all_dates = sorted(date_to_price.keys())
        try:
            float_idx = all_dates.index(float_date_str)
            before_start = max(0, float_idx - days_before)
            after_end = min(len(all_dates), float_idx + days_after + 1)
            
            before_dates = all_dates[before_start:float_idx]
            after_dates = all_dates[float_idx+1:after_end]
        except ValueError:
            continue
        
        # 计算解禁前后的平均涨跌幅
        before_changes = [date_to_price[date]['pct_chg'] for date in before_dates if date in date_to_price]
        after_changes = [date_to_price[date]['pct_chg'] for date in after_dates if date in date_to_price]
        
        avg_before = sum(before_changes) / len(before_changes) if before_changes else 0
        avg_after = sum(after_changes) / len(after_changes) if after_changes else 0
        
        # 构建影响分析
        impacts.append({
            "float_date": float_date_str,
            "float_share": float(float_data.float_share or 0),
            "float_ratio": float(float_data.float_ratio or 0),
            "before_price": date_to_price[before_dates[-1]]['close'] if before_dates else None,
            "float_price": float_price['close'],
            "after_price": date_to_price[after_dates[-1]]['close'] if after_dates else None,
            "before_avg_change": avg_before,
            "after_avg_change": avg_after,
            "impact": avg_after - avg_before,
            "holder_name": float_data.holder_name,
            "share_type": float_data.share_type
        })
    
    # 构建结果
    result = {
        "ts_code": ts_code,
        "analysis_period": f"解禁前{days_before}天，解禁后{days_after}天",
        "float_count": len(share_floats),
        "analyzed_count": len(impacts),
        "avg_impact": sum(impact["impact"] for impact in impacts) / len(impacts) if impacts else 0,
        "impacts": impacts
    }
    
    return result