import pandas as pd
from decimal import Decimal
from typing import List, Optional, Dict, Any
from app.external.tushare_api.stock.reference_data_api import get_pledge_stat
from app.data.db_modules.stock_modules.reference_data.pledge_stat import PledgeStatData

class PledgeStatService:
    """股票质押统计数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_pledge_stat_data(self, ts_code: Optional[str] = None, 
                                       end_date: Optional[str] = None,
                                       batch_size: int = 1000) -> int:
        """
        从Tushare获取股票质押统计数据并高效导入数据库
        
        参数:
            ts_code: 股票代码
            end_date: 截止日期，格式YYYYMMDD
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_pledge_stat(ts_code=ts_code, end_date=end_date)
        
        if df_result is None or df_result.empty:
            print(f"未找到股票质押统计数据: ts_code={ts_code}, end_date={end_date}")
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
            date_fields = ['end_date']
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
                # 将批次数据转换为PledgeStatData对象
                pledge_data_list = []
                for record in batch:
                    try:
                        # 处理数字字段，确保它们是Decimal类型或整型
                        for key, value in record.items():
                            if key == 'pledge_count' and isinstance(value, (float, int)):
                                record[key] = int(value)
                            elif isinstance(value, (float, int)) and key not in ['id', 'pledge_count']:
                                record[key] = Decimal(str(value))
                        
                        pledge_data = PledgeStatData(**record)
                        pledge_data_list.append(pledge_data)
                    except Exception as e:
                        print(f"创建PledgeStatData对象失败 {record.get('ts_code', '未知')}, {record.get('end_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if pledge_data_list:
                    inserted = await self.batch_upsert_pledge_stat(pledge_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条股票质押统计记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_pledge_stat(self, pledge_list: List[PledgeStatData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            pledge_list: 要插入或更新的股票质押统计数据列表
            
        返回:
            处理的记录数
        """
        if not pledge_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = pledge_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 使用字典来存储记录，如果有重复键，保留最新记录
        unique_records = {}
        
        for pledge in pledge_list:
            # 创建唯一键
            key = (pledge.ts_code, str(pledge.end_date))
            unique_records[key] = pledge
        
        # 提取最终的唯一记录列表
        unique_pledge_list = list(unique_records.values())
        
        # 准备数据
        records = []
        for pledge in unique_pledge_list:
            pledge_dict = pledge.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = pledge_dict[col]
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
                    column_types = await self._get_column_type(conn, 'pledge_stat', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_pledge_stat (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_pledge_stat', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'end_date']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO pledge_stat ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_pledge_stat
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


# 快捷函数，用于导入特定股票的质押统计数据
async def import_stock_pledge_stat(db, ts_code: str, batch_size: int = 1000):
    """
    导入特定股票的质押统计数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = PledgeStatService(db)
    count = await service.import_pledge_stat_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条股票 {ts_code} 的质押统计记录")
    return count


# 快捷函数，用于导入特定日期的质押统计数据
async def import_date_pledge_stat(db, end_date: str, batch_size: int = 1000):
    """
    导入特定日期的质押统计数据
    
    参数:
        db: 数据库连接对象
        end_date: 截止日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = PledgeStatService(db)
    count = await service.import_pledge_stat_data(end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条截止日期为 {end_date} 的质押统计记录")
    return count


# 导入所有质押统计数据
async def import_all_pledge_stat(db, batch_size: int = 1000):
    """
    导入所有可获取的质押统计数据
    
    注意: 这可能会请求大量数据，请确保有足够的网络带宽和系统资源。
    根据数据量大小，此操作可能需要较长时间完成。
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小，默认1000条
        
    返回:
        导入的记录总数
    """
    service = PledgeStatService(db)
    
    print("开始导入所有质押统计数据，此操作可能需要较长时间...")
    count = await service.import_pledge_stat_data(batch_size=batch_size)
    
    print(f"成功导入所有质押统计数据，共 {count} 条记录")
    return count


# 动态查询质押统计数据
async def query_pledge_stat_data(db, 
                            filters: Optional[Dict[str, Any]] = None, 
                            order_by: Optional[List[str]] = None,
                            limit: Optional[int] = None,
                            offset: Optional[int] = None):
    """
    动态查询质押统计数据，支持任意字段过滤和自定义排序
    
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
                 例如: {'ts_code__like': '600%', 'pledge_ratio__gt': 5}
        order_by: 排序字段列表，字段前加"-"表示降序，例如['-end_date', 'pledge_ratio']
        limit: 最大返回记录数
        offset: 跳过前面的记录数（用于分页）
        
    返回:
        List[PledgeStatData]: 符合条件的质押统计数据列表
    
    示例:
        # 查询某股票最近的质押统计数据
        data = await query_pledge_stat_data(
            db,
            filters={'ts_code': '000001.SZ'},
            order_by=['-end_date'],
            limit=1
        )
        
        # 分页查询质押比例超过50%的所有股票
        data = await query_pledge_stat_data(
            db,
            filters={'pledge_ratio__gt': 50},
            order_by=['-pledge_ratio', 'ts_code'],
            limit=20,
            offset=0
        )
    """
    from app.db.crud.stock_crud.reference_data.pledge_stat_crud import PledgeStatCRUD
    
    crud = PledgeStatCRUD(db)
    results = await crud.get_pledge_stats(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 获取高质押风险股票列表
async def get_high_pledge_risk_stocks(db, threshold: float = 50.0, limit: int = 100):
    """
    获取质押比例超过阈值的高风险股票列表
    
    参数:
        db: 数据库连接对象
        threshold: 质押比例阈值，默认50%
        limit: 最大返回记录数
        
    返回:
        List[PledgeStatData]: 高质押风险股票列表
    """
    # 获取每只股票最新的质押记录
    query = """
        WITH latest_dates AS (
            SELECT ts_code, MAX(end_date) as latest_date
            FROM pledge_stat
            GROUP BY ts_code
        )
        SELECT p.* 
        FROM pledge_stat p
        JOIN latest_dates ld 
            ON p.ts_code = ld.ts_code AND p.end_date = ld.latest_date
        WHERE p.pledge_ratio >= $1
        ORDER BY p.pledge_ratio DESC
        LIMIT $2
    """
    
    rows = await db.fetch(query, threshold, limit)
    
    if not rows:
        return []
    
    return [PledgeStatData.model_validate(dict(row)) for row in rows]


# 计算股票质押排名
async def calculate_pledge_ranking(db, end_date: Optional[str] = None):
    """
    计算特定日期的股票质押比例排名
    
    参数:
        db: 数据库连接对象
        end_date: 截止日期，格式YYYYMMDD，为None时使用最新日期
        
    返回:
        Dict: 包含排名信息的字典
    """
    from app.db.crud.stock_crud.reference_data.pledge_stat_crud import PledgeStatCRUD
    
    crud = PledgeStatCRUD(db)
    
    # 确定要使用的日期
    if end_date:
        formatted_end_date = end_date
        if end_date.isdigit() and len(end_date) == 8:
            formatted_end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
        
        # 获取该日期是否有数据
        query = "SELECT COUNT(*) FROM pledge_stat WHERE end_date = $1::date"
        count = await db.fetchval(query, formatted_end_date)
        
        if count == 0:
            # 如果指定日期没有数据，找最近的日期
            query = """
                SELECT MAX(end_date) FROM pledge_stat 
                WHERE end_date <= $1::date
            """
            latest_date = await db.fetchval(query, formatted_end_date)
            if latest_date:
                formatted_end_date = latest_date
            else:
                return {"error": f"未找到 {end_date} 或之前的质押统计数据"}
    else:
        # 获取最新日期
        query = "SELECT MAX(end_date) FROM pledge_stat"
        latest_date = await db.fetchval(query)
        if not latest_date:
            return {"error": "未找到任何质押统计数据"}
        formatted_end_date = latest_date
    
    # 查询指定日期的所有数据，按质押比例降序排序
    query = """
        SELECT *, 
               RANK() OVER (ORDER BY pledge_ratio DESC) as rank_by_ratio,
               RANK() OVER (ORDER BY pledge_count DESC) as rank_by_count
        FROM pledge_stat
        WHERE end_date = $1::date
        ORDER BY pledge_ratio DESC
    """
    
    rows = await db.fetch(query, formatted_end_date)
    
    if not rows:
        return {"error": f"未找到日期为 {formatted_end_date} 的质押统计数据"}
    
    # 准备结果
    result = {
        "end_date": formatted_end_date.strftime('%Y%m%d') if hasattr(formatted_end_date, 'strftime') else formatted_end_date,
        "total_stocks": len(rows),
        "stats": {
            "high_risk_count": sum(1 for row in rows if row['pledge_ratio'] and row['pledge_ratio'] >= 50),
            "medium_risk_count": sum(1 for row in rows if row['pledge_ratio'] and 20 <= row['pledge_ratio'] < 50),
            "low_risk_count": sum(1 for row in rows if row['pledge_ratio'] and row['pledge_ratio'] < 20),
        },
        "top_by_ratio": [
            {
                "ts_code": row['ts_code'], 
                "pledge_ratio": float(row['pledge_ratio']) if row['pledge_ratio'] else 0,
                "pledge_count": row['pledge_count'],
                "rank": row['rank_by_ratio']
            } 
            for row in rows[:10]  # 获取前10名
        ],
        "top_by_count": sorted(
            [
                {
                    "ts_code": row['ts_code'], 
                    "pledge_ratio": float(row['pledge_ratio']) if row['pledge_ratio'] else 0,
                    "pledge_count": row['pledge_count'],
                    "rank": row['rank_by_count']
                } 
                for row in rows if row['pledge_count']
            ],
            key=lambda x: x['pledge_count'],
            reverse=True
        )[:10]  # 获取前10名
    }
    
    return result


# 分析质押变化趋势
async def analyze_pledge_trend(db, ts_code: str, periods: int = 10):
    """
    分析特定股票的质押变化趋势
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        periods: 分析的历史期数，默认10期
        
    返回:
        Dict: 包含趋势分析结果的字典
    """
    # 获取该股票最近几期的质押数据
    query = """
        SELECT * FROM pledge_stat
        WHERE ts_code = $1
        ORDER BY end_date DESC
        LIMIT $2
    """
    
    rows = await db.fetch(query, ts_code, periods)
    
    if not rows:
        return {"error": f"未找到股票 {ts_code} 的质押统计数据"}
    
    # 降序排列的数据，需要反转以便计算趋势
    data = [dict(row) for row in rows]
    data.reverse()  # 按时间升序排列
    
    # 计算趋势数据
    trend_data = []
    prev_ratio = None
    prev_count = None
    
    for item in data:
        trend = {
            "end_date": item['end_date'].strftime('%Y%m%d') if hasattr(item['end_date'], 'strftime') else item['end_date'],
            "pledge_ratio": float(item['pledge_ratio']) if item['pledge_ratio'] else 0,
            "pledge_count": item['pledge_count'] if item['pledge_count'] else 0,
            "ratio_change": None,
            "count_change": None
        }
        
        if prev_ratio is not None:
            trend["ratio_change"] = float(item['pledge_ratio'] or 0) - prev_ratio
            
        if prev_count is not None:
            trend["count_change"] = (item['pledge_count'] or 0) - prev_count
        
        trend_data.append(trend)
        
        prev_ratio = float(item['pledge_ratio'] or 0)
        prev_count = item['pledge_count'] or 0
    
    # 计算整体变化
    if len(trend_data) >= 2:
        first = trend_data[0]
        last = trend_data[-1]
        overall_change = {
            "period_start": first["end_date"],
            "period_end": last["end_date"],
            "ratio_change": last["pledge_ratio"] - first["pledge_ratio"],
            "count_change": last["pledge_count"] - first["pledge_count"],
            "ratio_change_percent": (last["pledge_ratio"] / first["pledge_ratio"] - 1) * 100 if first["pledge_ratio"] > 0 else None,
            "count_change_percent": (last["pledge_count"] / first["pledge_count"] - 1) * 100 if first["pledge_count"] > 0 else None
        }
    else:
        overall_change = None
    
    # 分析趋势
    result = {
        "ts_code": ts_code,
        "periods": len(trend_data),
        "latest": trend_data[-1] if trend_data else None,
        "overall_change": overall_change,
        "trend_data": trend_data,
        "trend_analysis": {
            "ratio": {
                "increasing": all(item["ratio_change"] >= 0 for item in trend_data if item["ratio_change"] is not None),
                "decreasing": all(item["ratio_change"] <= 0 for item in trend_data if item["ratio_change"] is not None),
                "stable": all(abs(item["ratio_change"] or 0) < 1 for item in trend_data if item["ratio_change"] is not None)
            },
            "count": {
                "increasing": all(item["count_change"] >= 0 for item in trend_data if item["count_change"] is not None),
                "decreasing": all(item["count_change"] <= 0 for item in trend_data if item["count_change"] is not None),
                "stable": all(abs(item["count_change"] or 0) < 1 for item in trend_data if item["count_change"] is not None)
            }
        }
    }
    
    return result