import pandas as pd
import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from app.external.tushare_api.stock.hitting_limit_up_api import get_top_list
from app.data.db_modules.stock_modules.hitting_limit_up.top_list import TopListData

class TopListService:
    """龙虎榜数据导入服务，实现高效批量导入和数据管理"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_top_list_data(self, 
                                 trade_date: str,
                                 ts_code: Optional[str] = None,
                                 batch_size: int = 1000) -> int:
        """
        从Tushare获取龙虎榜数据并高效导入数据库
        
        参数:
            trade_date: 交易日期(YYYYMMDD格式)
            ts_code: 股票代码（可选）
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 构建参数说明用于日志
        params = []
        if trade_date:
            params.append(f"trade_date={trade_date}")
        if ts_code:
            params.append(f"ts_code={ts_code}")
        
        param_desc = ", ".join(params) if params else "所有"
        print(f"正在获取龙虎榜数据: {param_desc}")
        
        # 从Tushare获取数据
        try:
            df_result = get_top_list(trade_date=trade_date, ts_code=ts_code)
            
            if df_result is None or df_result.empty:
                print(f"未找到龙虎榜数据: {param_desc}")
                return 0
                
            print(f"获取到 {len(df_result)} 条龙虎榜数据")
        except Exception as e:
            print(f"获取龙虎榜数据失败: {str(e)}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 数据预处理和验证
        valid_records = await self._preprocess_records(records)
        
        if not valid_records:
            print("没有有效的龙虎榜数据记录可导入")
            return 0
            
        # 分批处理
        batches = [valid_records[i:i + batch_size] for i in range(0, len(valid_records), batch_size)]
        total_count = 0
        
        for batch_idx, batch in enumerate(batches):
            try:
                # 将批次数据转换为TopListData对象
                top_list_data_list = []
                for record in batch:
                    try:
                        # 为了确保数据类型正确，显式处理数值字段
                        numeric_fields = [
                            'close', 'pct_change', 'turnover_rate', 'amount', 
                            'l_sell', 'l_buy', 'l_amount', 'net_amount', 
                            'net_rate', 'amount_rate', 'float_values'
                        ]
                        
                        for field in numeric_fields:
                            if field in record and record[field] is not None:
                                if isinstance(record[field], str) and record[field].strip() == '':
                                    record[field] = None
                                elif record[field] is not None:
                                    try:
                                        record[field] = float(record[field])
                                    except (ValueError, TypeError):
                                        record[field] = None
                        
                        top_list_data = TopListData(**record)
                        top_list_data_list.append(top_list_data)
                    except Exception as e:
                        print(f"创建TopListData对象失败 {record.get('ts_code', '未知')}, {record.get('trade_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if top_list_data_list:
                    inserted = await self.batch_upsert_top_list(top_list_data_list)
                    total_count += inserted
                    print(f"批次 {batch_idx + 1}/{len(batches)} 导入成功: {inserted} 条龙虎榜记录")
            except Exception as e:
                print(f"批次 {batch_idx + 1}/{len(batches)} 导入失败: {str(e)}")
        
        print(f"总共成功导入 {total_count} 条龙虎榜记录")
        return total_count
    
    async def _preprocess_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        预处理和验证数据记录
        
        参数:
            records: 原始数据记录列表
            
        返回:
            处理后的有效记录列表
        """
        # 定义必填字段及默认值
        required_fields = {
            'ts_code': '',
            'name': '',
            'trade_date': None,
        }
        
        valid_records = []
        invalid_count = 0
        
        for record in records:
            # 确保必填字段存在且有值
            for field, default_value in required_fields.items():
                if field not in record or record[field] is None or (isinstance(record[field], str) and record[field].strip() == ''):
                    record[field] = default_value
            
            # 如果缺少关键字段，跳过该记录
            if record['ts_code'] == '' or record['name'] == '' or record['trade_date'] is None:
                invalid_count += 1
                continue
            
            # 处理日期格式，确保是YYYYMMDD格式
            if 'trade_date' in record and record['trade_date'] is not None:
                # 如果是pandas Timestamp对象，转换为YYYYMMDD格式字符串
                if hasattr(record['trade_date'], 'strftime'):
                    record['trade_date'] = record['trade_date'].strftime('%Y%m%d')
                # 如果已经是字符串但带有连字符（如"2023-12-31"），转换为YYYYMMDD
                elif isinstance(record['trade_date'], str) and '-' in record['trade_date']:
                    date_parts = record['trade_date'].split('-')
                    if len(date_parts) == 3:
                        record['trade_date'] = ''.join(date_parts)
            
            valid_records.append(record)
        
        if invalid_count > 0:
            print(f"警告: 跳过了 {invalid_count} 条无效记录")
            
        return valid_records
    
    async def batch_upsert_top_list(self, top_list_data_list: List[TopListData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            top_list_data_list: 要插入或更新的龙虎榜数据列表
            
        返回:
            处理的记录数
        """
        if not top_list_data_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = top_list_data_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 使用字典来存储记录，如果有重复键，保留最新记录
        unique_records = {}
        
        for top_list_data in top_list_data_list:
            # 创建唯一键 (ts_code, trade_date)
            key = (top_list_data.ts_code, str(top_list_data.trade_date))
            unique_records[key] = top_list_data
        
        # 提取最终的唯一记录列表
        unique_top_list_data_list = list(unique_records.values())
        
        # 准备数据
        records = []
        for top_list_data in unique_top_list_data_list:
            top_list_dict = top_list_data.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = top_list_dict[col]
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
                    column_types = await self._get_column_type(conn, 'top_list', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_top_list (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_top_list', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'trade_date']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO top_list ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_top_list
                        ON CONFLICT (ts_code, trade_date) DO UPDATE SET {update_clause}
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

# 快捷函数，用于导入特定交易日期的龙虎榜数据
async def import_date_top_list(db, trade_date: str, batch_size: int = 1000) -> int:
    """
    导入特定交易日期的龙虎榜数据
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = TopListService(db)
    count = await service.import_top_list_data(trade_date=trade_date, batch_size=batch_size)
    print(f"成功导入 {count} 条交易日期为 {trade_date} 的龙虎榜记录")
    return count


# 快捷函数，用于导入特定股票的龙虎榜数据
async def import_stock_top_list(db, ts_code: str, trade_date: str, batch_size: int = 1000) -> int:
    """
    导入特定股票特定日期的龙虎榜数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        trade_date: 交易日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = TopListService(db)
    count = await service.import_top_list_data(
        trade_date=trade_date,
        ts_code=ts_code,
        batch_size=batch_size
    )
    print(f"成功导入 {count} 条股票代码为 {ts_code}，交易日期为 {trade_date} 的龙虎榜记录")
    return count


# 从数据库中查询龙虎榜数据
async def query_top_list_data(db, 
                         filters: Optional[Dict[str, Any]] = None, 
                         order_by: Optional[List[str]] = None,
                         limit: Optional[int] = None,
                         offset: Optional[int] = None) -> List[TopListData]:
    """
    动态查询龙虎榜数据，支持任意字段过滤和自定义排序
    
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
                 例如: {'ts_code': '000001.SZ', 'net_amount__gt': 1000000}
        order_by: 排序字段列表，字段前加"-"表示降序，例如['-net_amount', 'trade_date']
        limit: 最大返回记录数
        offset: 跳过前面的记录数（用于分页）
        
    返回:
        List[TopListData]: 符合条件的龙虎榜数据列表
    """
    from app.db.crud.stock_crud.hitting_limit_up.top_list_crud import TopListCRUD
    
    crud = TopListCRUD(db)
    results = await crud.get_top_lists(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 获取某个交易日的龙虎榜净买入排行
async def get_top_net_buy_stocks(db, trade_date: str, limit: int = 20) -> Dict[str, Any]:
    """
    获取某个交易日龙虎榜净买入额排名靠前的股票
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期（YYYYMMDD格式）
        limit: 返回的记录数量
        
    返回:
        Dict: 包含净买入排名靠前的股票信息
    """
    # 处理trade_date格式
    formatted_trade_date = trade_date
    if trade_date and isinstance(trade_date, str) and trade_date.isdigit() and len(trade_date) == 8:
        formatted_trade_date = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:8]}"
    
    # 查询净买入额排名靠前的股票
    query = """
    SELECT 
        ts_code,
        name,
        close,
        pct_change,
        l_buy,
        l_sell,
        net_amount,
        net_rate,
        turnover_rate,
        reason
    FROM 
        top_list
    WHERE 
        trade_date = $1::date
    ORDER BY 
        net_amount DESC
    LIMIT $2
    """
    
    rows = await db.fetch(query, formatted_trade_date, limit)
    
    if not rows:
        return {
            "error": f"未找到交易日期 {trade_date} 的龙虎榜数据"
        }
    
    # 构建结果
    result = {
        "trade_date": trade_date,
        "top_net_buy_stocks": []
    }
    
    for row in rows:
        stock_data = {}
        for key in row.keys():
            if isinstance(row[key], (int, float, str)) or row[key] is None:
                if isinstance(row[key], (float, Decimal)):
                    stock_data[key] = float(row[key])
                else:
                    stock_data[key] = row[key]
        result["top_net_buy_stocks"].append(stock_data)
    
    return result


# 获取某个交易日的龙虎榜净卖出排行
async def get_top_net_sell_stocks(db, trade_date: str, limit: int = 20) -> Dict[str, Any]:
    """
    获取某个交易日龙虎榜净卖出额排名靠前的股票
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期（YYYYMMDD格式）
        limit: 返回的记录数量
        
    返回:
        Dict: 包含净卖出排名靠前的股票信息
    """
    # 处理trade_date格式
    formatted_trade_date = trade_date
    if trade_date and isinstance(trade_date, str) and trade_date.isdigit() and len(trade_date) == 8:
        formatted_trade_date = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:8]}"
    
    # 查询净卖出额排名靠前的股票
    query = """
    SELECT 
        ts_code,
        name,
        close,
        pct_change,
        l_buy,
        l_sell,
        net_amount,
        net_rate,
        turnover_rate,
        reason
    FROM 
        top_list
    WHERE 
        trade_date = $1::date
    ORDER BY 
        net_amount ASC
    LIMIT $2
    """
    
    rows = await db.fetch(query, formatted_trade_date, limit)
    
    if not rows:
        return {
            "error": f"未找到交易日期 {trade_date} 的龙虎榜数据"
        }
    
    # 构建结果
    result = {
        "trade_date": trade_date,
        "top_net_sell_stocks": []
    }
    
    for row in rows:
        stock_data = {}
        for key in row.keys():
            if isinstance(row[key], (int, float, str)) or row[key] is None:
                if isinstance(row[key], (float, Decimal)):
                    stock_data[key] = float(row[key])
                else:
                    stock_data[key] = row[key]
        result["top_net_sell_stocks"].append(stock_data)
    
    return result


# 获取某个股票的龙虎榜历史记录
async def get_stock_top_list_history(db, ts_code: str, limit: int = 20) -> Dict[str, Any]:
    """
    获取某个股票的龙虎榜历史记录
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        limit: 返回的记录数量
        
    返回:
        Dict: 包含股票龙虎榜历史记录的信息
    """
    # 查询股票龙虎榜历史记录
    query = """
    SELECT 
        trade_date,
        close,
        pct_change,
        l_buy,
        l_sell,
        net_amount,
        net_rate,
        turnover_rate,
        reason
    FROM 
        top_list
    WHERE 
        ts_code = $1
    ORDER BY 
        trade_date DESC
    LIMIT $2
    """
    
    rows = await db.fetch(query, ts_code, limit)
    
    if not rows:
        return {
            "error": f"未找到股票代码 {ts_code} 的龙虎榜数据"
        }
    
    # 获取股票名称
    name_query = "SELECT name FROM top_list WHERE ts_code = $1 LIMIT 1"
    name_row = await db.fetchrow(name_query, ts_code)
    stock_name = name_row["name"] if name_row else ""
    
    # 构建结果
    result = {
        "ts_code": ts_code,
        "name": stock_name,
        "history": []
    }
    
    for row in rows:
        history_data = {}
        for key in row.keys():
            if isinstance(row[key], (int, float, str)) or row[key] is None:
                if isinstance(row[key], (float, Decimal)):
                    history_data[key] = float(row[key])
                elif isinstance(row[key], datetime.date):
                    history_data[key] = row[key].strftime("%Y%m%d")
                else:
                    history_data[key] = row[key]
        result["history"].append(history_data)
    
    return result


# 按上榜理由分析龙虎榜数据
async def analyze_top_list_by_reason(db, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    按上榜理由分析龙虎榜数据
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期（YYYYMMDD格式）
        end_date: 结束日期（YYYYMMDD格式）
        
    返回:
        Dict: 按上榜理由分组的分析结果
    """
    # 处理日期格式
    formatted_start_date = start_date
    if start_date and isinstance(start_date, str) and start_date.isdigit() and len(start_date) == 8:
        formatted_start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
        
    formatted_end_date = end_date
    if end_date and isinstance(end_date, str) and end_date.isdigit() and len(end_date) == 8:
        formatted_end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
    
    # 查询上榜理由分组统计
    query = """
    SELECT 
        reason,
        COUNT(*) as count,
        AVG(pct_change) as avg_pct_change,
        AVG(net_amount) as avg_net_amount,
        AVG(net_rate) as avg_net_rate,
        AVG(turnover_rate) as avg_turnover_rate
    FROM 
        top_list
    WHERE 
        trade_date BETWEEN $1::date AND $2::date
        AND reason IS NOT NULL
        AND reason != ''
    GROUP BY 
        reason
    ORDER BY 
        count DESC
    """
    
    rows = await db.fetch(query, formatted_start_date, formatted_end_date)
    
    if not rows:
        return {
            "error": f"未找到 {start_date} 至 {end_date} 期间的龙虎榜数据"
        }
    
    # 构建结果
    result = {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "reason_statistics": []
    }
    
    for row in rows:
        reason_data = {
            "reason": row["reason"],
            "count": row["count"],
            "avg_pct_change": float(row["avg_pct_change"]) if row["avg_pct_change"] is not None else None,
            "avg_net_amount": float(row["avg_net_amount"]) if row["avg_net_amount"] is not None else None,
            "avg_net_rate": float(row["avg_net_rate"]) if row["avg_net_rate"] is not None else None,
            "avg_turnover_rate": float(row["avg_turnover_rate"]) if row["avg_turnover_rate"] is not None else None
        }
        result["reason_statistics"].append(reason_data)
    
    return result


# 分析龙虎榜数据与股票表现的关系
async def analyze_top_list_performance(db, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    分析龙虎榜数据与股票后续表现的关系
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期（YYYYMMDD格式）
        end_date: 结束日期（YYYYMMDD格式）
        
    返回:
        Dict: 龙虎榜数据与股票表现关系的分析结果
    """
    # 处理日期格式
    formatted_start_date = start_date
    if start_date and isinstance(start_date, str) and start_date.isdigit() and len(start_date) == 8:
        formatted_start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
        
    formatted_end_date = end_date
    if end_date and isinstance(end_date, str) and end_date.isdigit() and len(end_date) == 8:
        formatted_end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
    
    # 查询净买入额与涨跌幅的关系
    query = """
    WITH net_buy_groups AS (
        SELECT 
            ts_code,
            name,
            trade_date,
            net_amount,
            CASE 
                WHEN net_amount < 0 THEN '净卖出'
                WHEN net_amount BETWEEN 0 AND 10000000 THEN '小额净买入'
                WHEN net_amount BETWEEN 10000000 AND 50000000 THEN '中额净买入'
                ELSE '大额净买入'
            END as net_amount_group
        FROM 
            top_list
        WHERE 
            trade_date BETWEEN $1::date AND $2::date
    )
    SELECT 
        net_amount_group,
        COUNT(*) as stock_count,
        AVG(pct_change) as avg_day_change,
        AVG(net_amount) as avg_net_amount
    FROM 
        net_buy_groups g
        JOIN top_list t ON g.ts_code = t.ts_code AND g.trade_date = t.trade_date
    GROUP BY 
        net_amount_group
    ORDER BY 
        avg_net_amount DESC
    """
    
    rows = await db.fetch(query, formatted_start_date, formatted_end_date)
    
    if not rows:
        return {
            "error": f"未找到 {start_date} 至 {end_date} 期间的龙虎榜数据"
        }
    
    # 构建结果
    result = {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "performance_by_net_amount": []
    }
    
    for row in rows:
        performance_data = {
            "net_amount_group": row["net_amount_group"],
            "stock_count": row["stock_count"],
            "avg_day_change": float(row["avg_day_change"]) if row["avg_day_change"] is not None else None,
            "avg_net_amount": float(row["avg_net_amount"]) if row["avg_net_amount"] is not None else None
        }
        result["performance_by_net_amount"].append(performance_data)
    
    return result