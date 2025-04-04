import pandas as pd
from decimal import Decimal
from typing import List, Optional, Dict, Any
from app.external.tushare_api.stock.reference_data_api import get_pledge_detail
from app.data.db_modules.stock_modules.reference_data.pledge_detail import PledgeDetailData

class PledgeDetailService:
    """股票质押明细数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_pledge_detail_data(self, ts_code: str, batch_size: int = 1000) -> int:
        """
        从Tushare获取股票质押明细数据并高效导入数据库
        
        参数:
            ts_code: 股票代码（必须提供）
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        if not ts_code:
            print("必须提供有效的股票代码")
            return 0
            
        # 从Tushare获取数据
        df_result = get_pledge_detail(ts_code=ts_code)
        
        if df_result is None or df_result.empty:
            print(f"未找到股票 {ts_code} 的质押明细数据")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 定义必填字段及默认值
        required_fields = {
            'ts_code': ts_code,
            'holder_name': '',
        }
        
        # 处理数据并确保所有必填字段都有值
        valid_records = []
        for record in records:
            # 确保必填字段存在且有值
            for field, default_value in required_fields.items():
                if field not in record or record[field] is None or (isinstance(record[field], str) and record[field] == ''):
                    record[field] = default_value
            
            # 如果缺少关键字段，跳过该记录
            if record['ts_code'] == '' or record['holder_name'] == '':
                continue
            
            # 处理日期格式，确保是YYYYMMDD格式
            date_fields = ['ann_date', 'start_date', 'end_date', 'release_date']
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
                # 将批次数据转换为PledgeDetailData对象
                pledge_data_list = []
                for record in batch:
                    try:
                        # 处理数字字段，确保它们是Decimal类型
                        for key, value in record.items():
                            if isinstance(value, (float, int)) and key not in ['id']:
                                record[key] = Decimal(str(value))
                        
                        pledge_data = PledgeDetailData(**record)
                        pledge_data_list.append(pledge_data)
                    except Exception as e:
                        print(f"创建PledgeDetailData对象失败 {record.get('ts_code', '未知')}, {record.get('ann_date', '未知')}, {record.get('holder_name', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if pledge_data_list:
                    inserted = await self.batch_upsert_pledge_detail(pledge_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条质押明细记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_pledge_detail(self, pledge_list: List[PledgeDetailData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            pledge_list: 要插入或更新的股票质押明细数据列表
            
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
            # 创建唯一键(ts_code, ann_date, holder_name, start_date, pledgor)
            pledgor = pledge.pledgor or ''
            key = (pledge.ts_code, str(pledge.ann_date or ''), pledge.holder_name, str(pledge.start_date or ''), pledgor)
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
                    column_types = await self._get_column_type(conn, 'pledge_detail', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_pledge_detail (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_pledge_detail', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'ann_date', 'holder_name', 'start_date', 'pledgor']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO pledge_detail ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_pledge_detail
                        ON CONFLICT (ts_code, ann_date, holder_name, start_date, pledgor) DO UPDATE SET {update_clause}
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


# 快捷函数，用于导入特定股票的质押明细数据
async def import_stock_pledge_detail(db, ts_code: str, batch_size: int = 1000):
    """
    导入特定股票的质押明细数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = PledgeDetailService(db)
    count = await service.import_pledge_detail_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条股票 {ts_code} 的质押明细记录")
    return count


# 导入多只股票的质押明细数据
async def import_stocks_pledge_detail(db, ts_codes: List[str], batch_size: int = 1000):
    """
    导入多只股票的质押明细数据
    
    参数:
        db: 数据库连接对象
        ts_codes: 股票TS代码列表
        batch_size: 批量处理大小
        
    返回:
        导入的记录总数
    """
    service = PledgeDetailService(db)
    total_count = 0
    
    for ts_code in ts_codes:
        try:
            count = await service.import_pledge_detail_data(ts_code=ts_code, batch_size=batch_size)
            total_count += count
            print(f"成功导入 {count} 条股票 {ts_code} 的质押明细记录")
        except Exception as e:
            print(f"导入股票 {ts_code} 的质押明细数据失败: {str(e)}")
    
    print(f"总共成功导入 {total_count} 条质押明细记录")
    return total_count


# 动态查询质押明细数据
async def query_pledge_detail_data(db, 
                             filters: Optional[Dict[str, Any]] = None, 
                             order_by: Optional[List[str]] = None,
                             limit: Optional[int] = None,
                             offset: Optional[int] = None):
    """
    动态查询质押明细数据，支持任意字段过滤和自定义排序
    
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
                 例如: {'ts_code__like': '600%', 'holder_name__ilike': '%公司%'}
        order_by: 排序字段列表，字段前加"-"表示降序，例如['-ann_date', 'pledge_amount']
        limit: 最大返回记录数
        offset: 跳过前面的记录数（用于分页）
        
    返回:
        List[PledgeDetailData]: 符合条件的质押明细数据列表
    
    示例:
        # 查询某股票最近的质押明细数据
        data = await query_pledge_detail_data(
            db,
            filters={'ts_code': '000001.SZ'},
            order_by=['-ann_date'],
            limit=10
        )
        
        # 查询特定股东的质押记录
        data = await query_pledge_detail_data(
            db,
            filters={'holder_name__ilike': '%张三%'},
            order_by=['-ann_date'],
            limit=20,
            offset=0
        )
    """
    from app.db.crud.stock_crud.reference_data.pledge_detail_crud import PledgeDetailCRUD
    
    crud = PledgeDetailCRUD(db)
    results = await crud.get_pledge_details(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 获取未解押的质押记录
async def get_unreleased_pledges(db, ts_code: Optional[str] = None, limit: int = 100):
    """
    获取未解押的质押记录
    
    参数:
        db: 数据库连接对象
        ts_code: 可选的股票代码过滤
        limit: 最大返回记录数
        
    返回:
        List[PledgeDetailData]: 未解押的质押记录列表
    """
    from app.db.crud.stock_crud.reference_data.pledge_detail_crud import PledgeDetailCRUD
    
    crud = PledgeDetailCRUD(db)
    results = await crud.get_active_pledges(ts_code, limit)
    
    return results


# 获取股东质押汇总信息
async def get_holder_pledge_summary(db, ts_code: str):
    """
    获取特定股票的股东质押汇总信息
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        
    返回:
        Dict: 股东质押汇总信息
    """
    # 查询该股票的股东质押汇总
    query = """
        SELECT 
            holder_name,
            COUNT(*) as pledge_count,
            SUM(CASE WHEN is_release = 'Y' THEN 0 ELSE 1 END) as active_count,
            SUM(pledge_amount) as total_pledge_amount,
            MAX(holding_amount) as latest_holding_amount,
            MAX(h_total_ratio) as latest_h_total_ratio,
            MAX(ann_date) as latest_ann_date
        FROM 
            pledge_detail
        WHERE 
            ts_code = $1
        GROUP BY 
            holder_name
        ORDER BY 
            total_pledge_amount DESC
    """
    
    rows = await db.fetch(query, ts_code)
    
    if not rows:
        return {"error": f"未找到股票 {ts_code} 的质押记录"}
    
    # 查询总质押比例
    total_query = """
        SELECT 
            SUM(p_total_ratio) as total_p_ratio
        FROM 
            pledge_detail
        WHERE 
            ts_code = $1
            AND is_release != 'Y'
    """
    
    total_row = await db.fetchrow(total_query, ts_code)
    total_p_ratio = float(total_row['total_p_ratio']) if total_row and total_row['total_p_ratio'] else 0
    
    # 转换结果
    holder_summary = []
    for row in rows:
        holder_summary.append({
            "holder_name": row['holder_name'],
            "pledge_count": row['pledge_count'],
            "active_count": row['active_count'],
            "total_pledge_amount": float(row['total_pledge_amount']) if row['total_pledge_amount'] else 0,
            "latest_holding_amount": float(row['latest_holding_amount']) if row['latest_holding_amount'] else 0,
            "latest_h_total_ratio": float(row['latest_h_total_ratio']) if row['latest_h_total_ratio'] else 0,
            "latest_ann_date": row['latest_ann_date'].strftime('%Y%m%d') if row['latest_ann_date'] else None
        })
    
    # 构建结果
    result = {
        "ts_code": ts_code,
        "holder_count": len(holder_summary),
        "total_pledge_ratio": total_p_ratio,
        "holders": holder_summary
    }
    
    return result


# 分析质押风险
async def analyze_pledge_risk(db, ts_code: str):
    """
    分析特定股票的质押风险
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        
    返回:
        Dict: 质押风险分析结果
    """
    # 查询该股票的活跃质押记录
    query = """
        SELECT * FROM pledge_detail
        WHERE ts_code = $1
        AND (is_release != 'Y' OR is_release IS NULL)
        ORDER BY p_total_ratio DESC
    """
    
    rows = await db.fetch(query, ts_code)
    
    if not rows:
        return {
            "ts_code": ts_code,
            "risk_level": "无风险",
            "risk_score": 0,
            "message": "未找到活跃的质押记录",
            "active_pledges": 0,
            "total_pledge_ratio": 0
        }
    
    # 转换查询结果为PledgeDetailData对象
    active_pledges = [PledgeDetailData.model_validate(dict(row)) for row in rows]
    
    # 计算总质押比例
    total_pledge_ratio = sum(float(pledge.p_total_ratio or 0) for pledge in active_pledges)
    
    # 计算大股东质押比例
    holder_pledge_ratio = {}
    for pledge in active_pledges:
        if pledge.holder_name not in holder_pledge_ratio:
            holder_pledge_ratio[pledge.holder_name] = 0
        
        holder_pledge_ratio[pledge.holder_name] += float(pledge.p_total_ratio or 0)
    
    max_holder_ratio = max(holder_pledge_ratio.values()) if holder_pledge_ratio else 0
    
    # 风险评估标准
    # 风险级别: 高风险(>80%), 中高风险(50-80%), 中等风险(30-50%), 低风险(<30%)
    risk_level = "未知"
    risk_score = 0
    message = ""
    
    if total_pledge_ratio >= 80:
        risk_level = "高风险"
        risk_score = 5
        message = "总质押比例超过80%，存在高风险"
    elif total_pledge_ratio >= 50:
        risk_level = "中高风险"
        risk_score = 4
        message = "总质押比例在50%-80%之间，存在中高风险"
    elif total_pledge_ratio >= 30:
        risk_level = "中等风险"
        risk_score = 3
        message = "总质押比例在30%-50%之间，存在中等风险"
    elif total_pledge_ratio >= 10:
        risk_level = "低风险"
        risk_score = 2
        message = "总质押比例在10%-30%之间，风险较低"
    else:
        risk_level = "无风险"
        risk_score = 1
        message = "总质押比例低于10%，几乎无风险"
    
    # 如果单一大股东质押比例过高，增加风险级别
    if max_holder_ratio >= 30:
        message += f"，且存在大股东高比例质押(最高{max_holder_ratio:.2f}%)"
        if risk_score < 5:
            risk_score += 1
    
    # 构建结果
    result = {
        "ts_code": ts_code,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "message": message,
        "active_pledges": len(active_pledges),
        "total_pledge_ratio": total_pledge_ratio,
        "max_holder_pledge_ratio": max_holder_ratio,
        "pledge_details": [pledge.model_dump() for pledge in active_pledges[:5]]  # 返回前5条记录
    }
    
    return result


# 查询特定质押方的质押记录
async def get_pledgor_records(db, pledgor: str, limit: int = 100):
    """
    查询特定质押方的质押记录
    
    参数:
        db: 数据库连接对象
        pledgor: 质押方名称（支持模糊匹配）
        limit: 最大返回记录数
        
    返回:
        List[PledgeDetailData]: 质押方的质押记录列表
    """
    query = """
        SELECT * FROM pledge_detail
        WHERE pledgor ILIKE $1
        ORDER BY ann_date DESC, ts_code
        LIMIT $2
    """
    
    rows = await db.fetch(query, f"%{pledgor}%", limit)
    
    if not rows:
        return []
    
    return [PledgeDetailData.model_validate(dict(row)) for row in rows]


# 分析股票质押解押趋势
async def analyze_pledge_release_trend(db, ts_code: str, months: int = 12):
    """
    分析特定股票的质押/解押趋势
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        months: 分析的月数
        
    返回:
        Dict: 质押/解押趋势分析结果
    """
    # 查询该股票近期的质押和解押记录
    query = """
        WITH date_series AS (
            SELECT date_trunc('month', current_date - (n || ' month')::interval) as month_start
            FROM generate_series(0, $2 - 1) n
        ),
        pledge_stats AS (
            SELECT 
                date_trunc('month', start_date) as month,
                count(*) as new_pledges,
                sum(pledge_amount) as pledge_amount
            FROM 
                pledge_detail
            WHERE 
                ts_code = $1
                AND start_date >= (current_date - ($2 || ' month')::interval)
            GROUP BY 
                date_trunc('month', start_date)
        ),
        release_stats AS (
            SELECT 
                date_trunc('month', release_date) as month,
                count(*) as releases,
                sum(pledge_amount) as release_amount
            FROM 
                pledge_detail
            WHERE 
                ts_code = $1
                AND is_release = 'Y'
                AND release_date >= (current_date - ($2 || ' month')::interval)
            GROUP BY 
                date_trunc('month', release_date)
        )
        SELECT 
            ds.month_start,
            coalesce(ps.new_pledges, 0) as new_pledges,
            coalesce(ps.pledge_amount, 0) as pledge_amount,
            coalesce(rs.releases, 0) as releases,
            coalesce(rs.release_amount, 0) as release_amount
        FROM 
            date_series ds
        LEFT JOIN 
            pledge_stats ps ON ds.month_start = ps.month
        LEFT JOIN 
            release_stats rs ON ds.month_start = rs.month
        ORDER BY 
            ds.month_start
    """
    
    rows = await db.fetch(query, ts_code, months)
    
    if not rows:
        return {"error": f"未找到股票 {ts_code} 的质押/解押记录"}
    
    # 转换结果
    trend_data = []
    total_new_pledges = 0
    total_pledge_amount = 0
    total_releases = 0
    total_release_amount = 0
    
    for row in rows:
        month_data = {
            "month": row['month_start'].strftime('%Y-%m'),
            "new_pledges": row['new_pledges'],
            "pledge_amount": float(row['pledge_amount']) if row['pledge_amount'] else 0,
            "releases": row['releases'],
            "release_amount": float(row['release_amount']) if row['release_amount'] else 0,
            "net_pledges": row['new_pledges'] - row['releases'],
            "net_amount": float(row['pledge_amount'] or 0) - float(row['release_amount'] or 0)
        }
        trend_data.append(month_data)
        
        total_new_pledges += row['new_pledges']
        total_pledge_amount += float(row['pledge_amount'] or 0)
        total_releases += row['releases']
        total_release_amount += float(row['release_amount'] or 0)
    
    # 构建结果
    result = {
        "ts_code": ts_code,
        "period": f"最近{months}个月",
        "summary": {
            "total_new_pledges": total_new_pledges,
            "total_pledge_amount": total_pledge_amount,
            "total_releases": total_releases,
            "total_release_amount": total_release_amount,
            "net_pledges": total_new_pledges - total_releases,
            "net_amount": total_pledge_amount - total_release_amount
        },
        "trend": trend_data
    }
    
    return result