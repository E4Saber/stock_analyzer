import pandas as pd
from decimal import Decimal
from typing import List, Optional, Dict, Any
from app.external.tushare_api.stock.hitting_limit_up_api import get_kpl_list
from app.data.db_modules.stock_modules.hitting_limit_up.kpl_list import KplListData

class KplListService:
    """涨停板列表数据导入服务，实现高效批量导入和数据管理"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_kpl_list_data(self, 
                                 ts_code: Optional[str] = None, 
                                 trade_date: Optional[str] = None,
                                 tag: Optional[str] = None,
                                 start_date: Optional[str] = None,
                                 end_date: Optional[str] = None,
                                 batch_size: int = 1000) -> int:
        """
        从Tushare获取涨停板列表数据并高效导入数据库
        
        参数:
            ts_code: 股票代码
            trade_date: 交易日期(YYYYMMDD格式)
            tag: 板单类型（涨停/炸板/跌停/自然涨停/竞价)
            start_date: 开始日期（用于查询日期范围，YYYYMMDD格式）
            end_date: 结束日期（用于查询日期范围，YYYYMMDD格式）
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 构建参数说明用于日志
        params = []
        if ts_code:
            params.append(f"ts_code={ts_code}")
        if trade_date:
            params.append(f"trade_date={trade_date}")
        if tag:
            params.append(f"tag={tag}")
        if start_date:
            params.append(f"start_date={start_date}")
        if end_date:
            params.append(f"end_date={end_date}")
        
        param_desc = ", ".join(params) if params else "所有"
        print(f"正在获取涨停板列表数据: {param_desc}")
        
        # 从Tushare获取数据
        try:
            df_result = get_kpl_list(
                ts_code=ts_code, 
                trade_date=trade_date, 
                tag=tag,
                start_date=start_date,
                end_date=end_date
            )
            
            if df_result is None or df_result.empty:
                print(f"未找到涨停板列表数据: {param_desc}")
                return 0
                
            print(f"获取到 {len(df_result)} 条涨停板列表数据")
        except Exception as e:
            print(f"获取涨停板列表数据失败: {str(e)}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 数据预处理和验证
        valid_records = await self._preprocess_records(records)
        
        if not valid_records:
            print("没有有效的涨停板列表数据记录可导入")
            return 0
            
        # 分批处理
        batches = [valid_records[i:i + batch_size] for i in range(0, len(valid_records), batch_size)]
        total_count = 0
        
        for batch_idx, batch in enumerate(batches):
            try:
                # 将批次数据转换为KplListData对象
                kpl_list_data_list = []
                for record in batch:
                    try:
                        # 为了确保数据类型正确，显式处理数值字段
                        numeric_fields = [
                            'net_change', 'bid_amount', 'bid_change', 'bid_turnover', 
                            'lu_bid_vol', 'pct_chg', 'bid_pct_chg', 'rt_pct_chg', 
                            'limit_order', 'amount', 'turnover_rate', 'free_float', 
                            'lu_limit_order'
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
                        
                        kpl_list_data = KplListData(**record)
                        kpl_list_data_list.append(kpl_list_data)
                    except Exception as e:
                        print(f"创建KplListData对象失败 {record.get('ts_code', '未知')}, {record.get('trade_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if kpl_list_data_list:
                    inserted = await self.batch_upsert_kpl_list(kpl_list_data_list)
                    total_count += inserted
                    print(f"批次 {batch_idx + 1}/{len(batches)} 导入成功: {inserted} 条涨停板列表记录")
            except Exception as e:
                print(f"批次 {batch_idx + 1}/{len(batches)} 导入失败: {str(e)}")
        
        print(f"总共成功导入 {total_count} 条涨停板列表记录")
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
    
    async def batch_upsert_kpl_list(self, kpl_list_data_list: List[KplListData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            kpl_list_data_list: 要插入或更新的涨停板列表数据列表
            
        返回:
            处理的记录数
        """
        if not kpl_list_data_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = kpl_list_data_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 使用字典来存储记录，如果有重复键，保留最新记录
        unique_records = {}
        
        for kpl_list_data in kpl_list_data_list:
            # 创建唯一键 (ts_code, trade_date)
            key = (kpl_list_data.ts_code, str(kpl_list_data.trade_date))
            unique_records[key] = kpl_list_data
        
        # 提取最终的唯一记录列表
        unique_kpl_list_data_list = list(unique_records.values())
        
        # 准备数据
        records = []
        for kpl_list_data in unique_kpl_list_data_list:
            kpl_list_dict = kpl_list_data.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = kpl_list_dict[col]
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
                    column_types = await self._get_column_type(conn, 'kpl_list', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_kpl_list (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_kpl_list', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'trade_date']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO kpl_list ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_kpl_list
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


# 快捷函数，用于导入特定交易日期的涨停板列表数据
async def import_date_kpl_list(db, trade_date: str, tag: Optional[str] = None, batch_size: int = 1000) -> int:
    """
    导入特定交易日期的涨停板列表数据
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期（YYYYMMDD格式）
        tag: 可选的板单类型过滤
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = KplListService(db)
    count = await service.import_kpl_list_data(trade_date=trade_date, tag=tag, batch_size=batch_size)
    print(f"成功导入 {count} 条交易日期为 {trade_date} 的涨停板列表记录")
    return count


# 快捷函数，用于导入特定股票代码的涨停板列表数据
async def import_ts_code_kpl_list(db, ts_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, batch_size: int = 1000) -> int:
    """
    导入特定股票代码的涨停板列表数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        start_date: 可选的开始日期
        end_date: 可选的结束日期
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = KplListService(db)
    count = await service.import_kpl_list_data(
        ts_code=ts_code, 
        start_date=start_date,
        end_date=end_date,
        batch_size=batch_size
    )
    print(f"成功导入 {count} 条股票代码为 {ts_code} 的涨停板列表记录")
    return count


# 快捷函数，用于导入特定标签的涨停板列表数据
async def import_tag_kpl_list(db, tag: str, trade_date: Optional[str] = None, batch_size: int = 1000) -> int:
    """
    导入特定标签的涨停板列表数据
    
    参数:
        db: 数据库连接对象
        tag: 板单类型（涨停/炸板/跌停/自然涨停/竞价)
        trade_date: 可选的交易日期
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = KplListService(db)
    count = await service.import_kpl_list_data(tag=tag, trade_date=trade_date, batch_size=batch_size)
    print(f"成功导入 {count} 条标签为 '{tag}' 的涨停板列表记录")
    return count


# 快捷函数，用于导入特定日期范围的涨停板列表数据
async def import_date_range_kpl_list(db, start_date: str, end_date: str, tag: Optional[str] = None, batch_size: int = 1000) -> int:
    """
    导入特定日期范围的涨停板列表数据
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期（YYYYMMDD格式）
        end_date: 结束日期（YYYYMMDD格式）
        tag: 可选的板单类型过滤
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = KplListService(db)
    count = await service.import_kpl_list_data(
        start_date=start_date, 
        end_date=end_date, 
        tag=tag,
        batch_size=batch_size
    )
    print(f"成功导入 {count} 条日期范围为 {start_date} 至 {end_date} 的涨停板列表记录")
    return count


# 综合导入函数，支持多种参数组合
async def import_kpl_list_with_params(db, **kwargs) -> int:
    """
    根据提供的参数导入涨停板列表数据
    
    参数:
        db: 数据库连接对象
        **kwargs: 可包含 ts_code, trade_date, tag, start_date, end_date, batch_size 等参数
        
    返回:
        导入的记录数
    """
    service = KplListService(db)
    batch_size = kwargs.pop('batch_size', 1000)  # 提取并移除batch_size参数
    
    # 构建参数描述
    param_desc = []
    for key, value in kwargs.items():
        if value:
            param_desc.append(f"{key}={value}")
    
    params_info = ", ".join(param_desc) if param_desc else "所有可用参数"
    
    # 导入数据
    count = await service.import_kpl_list_data(batch_size=batch_size, **kwargs)
    print(f"成功导入 {count} 条涨停板列表记录 ({params_info})")
    return count


# 导入所有涨停板列表数据
async def import_all_kpl_list(db, batch_size: int = 1000) -> int:
    """
    导入所有可获取的涨停板列表数据
    
    注意: 这可能会请求大量数据，请确保有足够的网络带宽和系统资源。
    根据数据量大小，此操作可能需要较长时间完成。
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小，默认1000条
        
    返回:
        导入的记录总数
    """
    service = KplListService(db)
    
    print("开始导入所有涨停板列表数据，此操作可能需要较长时间...")
    count = await service.import_kpl_list_data(batch_size=batch_size)
    
    print(f"成功导入所有涨停板列表数据，共 {count} 条记录")
    return count


# 从数据库中查询涨停板列表数据
async def query_kpl_list_data(db, 
                         filters: Optional[Dict[str, Any]] = None, 
                         order_by: Optional[List[str]] = None,
                         limit: Optional[int] = None,
                         offset: Optional[int] = None) -> List[KplListData]:
    """
    动态查询涨停板列表数据，支持任意字段过滤和自定义排序
    
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
                 例如: {'tag': '涨停', 'pct_chg__gt': 9.5}
        order_by: 排序字段列表，字段前加"-"表示降序，例如['-pct_chg', 'name']
        limit: 最大返回记录数
        offset: 跳过前面的记录数（用于分页）
        
    返回:
        List[KplListData]: 符合条件的涨停板列表数据
    
    示例:
        # 查询某个交易日的所有涨停股，按涨跌幅降序排列
        data = await query_kpl_list_data(
            db,
            filters={'trade_date': '20230101', 'tag': '涨停'},
            order_by=['-pct_chg'],
            limit=10
        )
        
        # 分页查询某个板块的所有涨停股
        data = await query_kpl_list_data(
            db,
            filters={'theme__ilike': '%半导体%'},
            order_by=['-trade_date', '-pct_chg'],
            limit=20,
            offset=0
        )
    """
    from app.db.crud.stock_crud.hitting_limit_up.kpl_list_crud import KplListCRUD
    
    crud = KplListCRUD(db)
    results = await crud.get_kpl_lists(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return result


# 分析主力资金流入最多的涨停股
async def analyze_top_capital_inflow(db, trade_date: str, limit: int = 20) -> Dict[str, Any]:
    """
    分析特定交易日主力资金流入最多的涨停股
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期（YYYYMMDD格式）
        limit: 返回的记录数量
        
    返回:
        Dict: 主力资金流入分析结果
    """
    # 处理trade_date格式
    formatted_trade_date = trade_date
    if trade_date and isinstance(trade_date, str) and trade_date.isdigit() and len(trade_date) == 8:
        formatted_trade_date = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:8]}"
    
    # 查询主力资金流入最多的涨停股
    query = """
    SELECT 
        ts_code,
        name,
        tag,
        theme,
        status,
        net_change,
        pct_chg,
        amount,
        turnover_rate,
        lu_time,
        lu_desc
    FROM 
        kpl_list
    WHERE 
        trade_date = $1::date
        AND tag = '涨停'
        AND net_change IS NOT NULL
    ORDER BY 
        net_change DESC
    LIMIT $2
    """
    
    rows = await db.fetch(query, formatted_trade_date, limit)
    
    if not rows:
        return {
            "error": f"未找到交易日期 {trade_date} 的主力资金流入数据"
        }
    
    # 构建结果
    result = {
        "trade_date": trade_date,
        "top_capital_inflow": []
    }
    
    for row in rows:
        stock_data = {}
        for key in row.keys():
            if isinstance(row[key], (int, float, str)) or row[key] is None:
                if isinstance(row[key], (float, Decimal)):
                    stock_data[key] = float(row[key])
                else:
                    stock_data[key] = row[key]
        result["top_capital_inflow"].append(stock_data)
    
    return result


# 分析竞价表现最好的股票
async def analyze_top_bid_performance(db, trade_date: str, limit: int = 20) -> Dict[str, Any]:
    """
    分析特定交易日竞价表现最好的股票
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期（YYYYMMDD格式）
        limit: 返回的记录数量
        
    返回:
        Dict: 竞价表现分析结果
    """
    # 处理trade_date格式
    formatted_trade_date = trade_date
    if trade_date and isinstance(trade_date, str) and trade_date.isdigit() and len(trade_date) == 8:
        formatted_trade_date = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:8]}"
    
    # 查询竞价表现最好的股票
    query = """
    SELECT 
        ts_code,
        name,
        tag,
        theme,
        bid_pct_chg,
        bid_amount,
        bid_turnover,
        pct_chg,
        status
    FROM 
        kpl_list
    WHERE 
        trade_date = $1::date
        AND bid_pct_chg IS NOT NULL
    ORDER BY 
        bid_pct_chg DESC
    LIMIT $2
    """
    
    rows = await db.fetch(query, formatted_trade_date, limit)
    
    if not rows:
        return {
            "error": f"未找到交易日期 {trade_date} 的竞价表现数据"
        }
    
    # 构建结果
    result = {
        "trade_date": trade_date,
        "top_bid_performance": []
    }
    
    for row in rows:
        stock_data = {}
        for key in row.keys():
            if isinstance(row[key], (int, float, str)) or row[key] is None:
                if isinstance(row[key], (float, Decimal)):
                    stock_data[key] = float(row[key])
                else:
                    stock_data[key] = row[key]
        result["top_bid_performance"].append(stock_data)
    
    return result


# 分析最近N天的涨停趋势
async def analyze_limit_up_trends(db, days: int = 10) -> Dict[str, Any]:
    """
    分析最近N天的涨停趋势
    
    参数:
        db: 数据库连接对象
        days: 分析的天数
        
    返回:
        Dict: 涨停趋势分析结果
    """
    # 获取最近N天的交易日期
    date_query = """
    SELECT DISTINCT trade_date
    FROM kpl_list
    ORDER BY trade_date DESC
    LIMIT $1
    """
    
    date_rows = await db.fetch(date_query, days)
    
    if not date_rows or len(date_rows) == 0:
        return {"error": "未找到足够的数据进行趋势分析"}
    
    dates = [row["trade_date"].strftime("%Y%m%d") for row in date_rows]
    
    # 查询每天的涨停数据
    daily_data = []
    for date in dates:
        daily_stats = await analyze_limit_up_by_date(db, date)
        if "error" not in daily_stats:
            daily_data.append(daily_stats)
    
    # 计算趋势
    trend_data = {
        "period": {
            "days": len(daily_data),
            "start_date": dates[-1] if daily_data else None,
            "end_date": dates[0] if daily_data else None
        },
        "daily_summary": [],
        "trend_analysis": {
            "limit_up_trend": [],
            "theme_frequency": {},
            "consecutive_days": {}
        }
    }
    
    # 统计每日数据
    for day_data in daily_data:
        summary = {
            "trade_date": day_data["trade_date"],
            "limit_up_count": day_data["summary"]["limit_up_count"],
            "first_limit_up_count": day_data["summary"]["first_limit_up_count"],
            "continuous_limit_up_count": day_data["summary"]["continuous_limit_up_count"],
            "blown_board_count": day_data["summary"]["blown_board_count"]
        }
        trend_data["daily_summary"].append(summary)
        
        # 统计主题频率
        for theme in day_data["theme_distribution"]:
            theme_name = theme["theme"]
            if theme_name not in trend_data["trend_analysis"]["theme_frequency"]:
                trend_data["trend_analysis"]["theme_frequency"][theme_name] = 0
            trend_data["trend_analysis"]["theme_frequency"][theme_name] += theme["count"]
    
    # 排序主题频率
    sorted_themes = sorted(
        trend_data["trend_analysis"]["theme_frequency"].items(),
        key=lambda x: x[1],
        reverse=True
    )
    trend_data["trend_analysis"]["theme_frequency"] = {k: v for k, v in sorted_themes[:15]}
    
    # 计算涨停数据趋势
    if len(trend_data["daily_summary"]) >= 2:
        # 按日期排序（最早的在前）
        sorted_summary = sorted(trend_data["daily_summary"], key=lambda x: x["trade_date"])
        
        for i in range(1, len(sorted_summary)):
            prev = sorted_summary[i-1]
            curr = sorted_summary[i]
            
            trend_data["trend_analysis"]["limit_up_trend"].append({
                "date": curr["trade_date"],
                "limit_up_count": curr["limit_up_count"],
                "change": curr["limit_up_count"] - prev["limit_up_count"],
                "change_percent": round((curr["limit_up_count"] - prev["limit_up_count"]) / max(prev["limit_up_count"], 1) * 100, 2)
            })
    
    return trend_data

# 获取股票的涨停历史
async def get_stock_limit_up_history(db, ts_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 50) -> List[KplListData]:
    """
    获取特定股票的涨停历史记录
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        start_date: 可选的开始日期（YYYYMMDD格式）
        end_date: 可选的结束日期（YYYYMMDD格式）
        limit: 返回的最大记录数
        
    返回:
        List[KplListData]: 该股票的涨停历史列表
    """
    # 构建过滤条件
    filters = {
        'ts_code': ts_code,
        'tag__in': ['涨停', '炸板']  # 包括涨停和炸板记录
    }
    
    if start_date:
        filters['trade_date__ge'] = start_date
    
    if end_date:
        filters['trade_date__le'] = end_date
    
    # 查询数据
    from app.db.crud.stock_crud.hitting_limit_up.kpl_list_crud import KplListCRUD
    
    crud = KplListCRUD(db)
    results = await crud.get_kpl_lists(
        filters=filters,
        order_by=['-trade_date'],
        limit=limit
    )
    
    return results


# 获取某个交易日的热门板块
async def get_hot_themes_by_date(db, trade_date: str, limit: int = 10) -> Dict[str, Any]:
    """
    获取某个交易日的热门题材板块
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期（YYYYMMDD格式）
        limit: 返回的板块数量
        
    返回:
        Dict: 包含热门板块信息的字典
    """
    # 处理trade_date格式
    formatted_trade_date = trade_date
    if trade_date and isinstance(trade_date, str) and trade_date.isdigit() and len(trade_date) == 8:
        formatted_trade_date = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:8]}"
    
    # 查询热门板块
    query = """
    SELECT 
        theme,
        COUNT(*) as stock_count,
        AVG(pct_chg) as avg_pct_chg,
        AVG(turnover_rate) as avg_turnover_rate,
        STRING_AGG(ts_code || '(' || name || ')', ', ' ORDER BY pct_chg DESC) as stocks
    FROM 
        kpl_list
    WHERE 
        trade_date = $1::date
        AND tag = '涨停'
        AND theme IS NOT NULL
        AND theme != ''
    GROUP BY 
        theme
    ORDER BY 
        stock_count DESC, avg_pct_chg DESC
    LIMIT $2
    """
    
    rows = await db.fetch(query, formatted_trade_date, limit)
    
    if not rows:
        return {
            "error": f"未找到交易日期 {trade_date} 的热门板块数据"
        }
    
    # 构建结果
    result = {
        "trade_date": trade_date,
        "hot_themes": []
    }
    
    for row in rows:
        theme_data = {
            "theme": row["theme"],
            "stock_count": row["stock_count"],
            "avg_pct_chg": float(row["avg_pct_chg"]) if row["avg_pct_chg"] is not None else None,
            "avg_turnover_rate": float(row["avg_turnover_rate"]) if row["avg_turnover_rate"] is not None else None,
            "stocks": row["stocks"]
        }
        result["hot_themes"].append(theme_data)
    
    return results


# 获取连板数据分析
async def analyze_continuous_limit_up(db, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    分析指定日期范围内的连板情况
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期（YYYYMMDD格式）
        end_date: 结束日期（YYYYMMDD格式）
        
    返回:
        Dict: 连板数据分析结果
    """
    # 处理日期格式
    formatted_start_date = start_date
    if start_date and isinstance(start_date, str) and start_date.isdigit() and len(start_date) == 8:
        formatted_start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
        
    formatted_end_date = end_date
    if end_date and isinstance(end_date, str) and end_date.isdigit() and len(end_date) == 8:
        formatted_end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
    
    # 查询连板情况
    query = """
    SELECT 
        status,
        COUNT(*) as count,
        AVG(pct_chg) as avg_pct_chg,
        AVG(turnover_rate) as avg_turnover_rate,
        AVG(amount) as avg_amount
    FROM 
        kpl_list
    WHERE 
        trade_date BETWEEN $1::date AND $2::date
        AND status IS NOT NULL
        AND status != ''
        AND tag = '涨停'
    GROUP BY 
        status
    ORDER BY 
        CASE 
            WHEN status ~ E'^\\\\d+$' THEN CAST(status AS INTEGER)
            ELSE 0
        END DESC
    """
    
    rows = await db.fetch(query, formatted_start_date, formatted_end_date)
    
    if not rows:
        return {
            "error": f"未找到 {start_date} 至 {end_date} 期间的连板数据"
        }
    
    # 构建结果
    result = {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "continuous_data": []
    }
    
    for row in rows:
        data = {
            "status": row["status"],
            "count": row["count"],
            "avg_pct_chg": float(row["avg_pct_chg"]) if row["avg_pct_chg"] is not None else None,
            "avg_turnover_rate": float(row["avg_turnover_rate"]) if row["avg_turnover_rate"] is not None else None,
            "avg_amount": float(row["avg_amount"]) if row["avg_amount"] is not None else None
        }
        result["continuous_data"].append(data)
    
    return result


# 获取特定交易日的涨停板分析
async def analyze_limit_up_by_date(db, trade_date: str) -> Dict[str, Any]:
    """
    获取特定交易日的涨停板数据分析
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期（YYYYMMDD格式）
        
    返回:
        Dict: 涨停板数据分析结果
    """
    # 处理trade_date格式
    formatted_trade_date = trade_date
    if trade_date and isinstance(trade_date, str) and trade_date.isdigit() and len(trade_date) == 8:
        formatted_trade_date = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:8]}"
    
    # 查询基本统计数据
    stats_query = """
    SELECT 
        COUNT(*) FILTER (WHERE tag = '涨停') as limit_up_count,
        COUNT(*) FILTER (WHERE tag = '涨停' AND status = '1') as first_limit_up_count,
        COUNT(*) FILTER (WHERE tag = '涨停' AND status != '1' AND status ~ E'^\\\\d+$') as continuous_limit_up_count,
        COUNT(*) FILTER (WHERE tag = '炸板') as blown_board_count,
        AVG(pct_chg) FILTER (WHERE tag = '涨停') as avg_limit_up_pct,
        AVG(turnover_rate) FILTER (WHERE tag = '涨停') as avg_turnover_rate,
        AVG(amount) FILTER (WHERE tag = '涨停') as avg_amount
    FROM 
        kpl_list
    WHERE 
        trade_date = $1::date
    """
    
    # 查询主题分布
    theme_query = """
    SELECT 
        theme,
        COUNT(*) as count
    FROM 
        kpl_list
    WHERE 
        trade_date = $1::date
        AND tag = '涨停'
        AND theme IS NOT NULL
        AND theme != ''
    GROUP BY 
        theme
    ORDER BY 
        count DESC
    LIMIT 10
    """
    
    # 查询连板分布
    status_query = """
    SELECT 
        status,
        COUNT(*) as count
    FROM 
        kpl_list
    WHERE 
        trade_date = $1::date
        AND tag = '涨停'
        AND status IS NOT NULL
        AND status != ''
    GROUP BY 
        status
    ORDER BY 
        CASE 
            WHEN status ~ E'^\\\\d+$' THEN CAST(status AS INTEGER)
            ELSE 0
        END DESC
    """
    
    # 查询涨停时间分布
    time_query = """
    SELECT 
        CASE
            WHEN lu_time <= '10:00:00' THEN '10点前'
            WHEN lu_time <= '11:30:00' THEN '上午'
            WHEN lu_time <= '14:00:00' THEN '14点前'
            WHEN lu_time <= '15:00:00' THEN '收盘前'
            ELSE '其他'
        END as time_period,
        COUNT(*) as count
    FROM 
        kpl_list
    WHERE 
        trade_date = $1::date
        AND tag = '涨停'
        AND lu_time IS NOT NULL
    GROUP BY 
        time_period
    ORDER BY 
        CASE
            WHEN time_period = '10点前' THEN 1
            WHEN time_period = '上午' THEN 2
            WHEN time_period = '14点前' THEN 3
            WHEN time_period = '收盘前' THEN 4
            ELSE 5
        END
    """
    
    # 执行查询
    stats_row = await db.fetchrow(stats_query, formatted_trade_date)
    theme_rows = await db.fetch(theme_query, formatted_trade_date)
    status_rows = await db.fetch(status_query, formatted_trade_date)
    time_rows = await db.fetch(time_query, formatted_trade_date)
    
    if not stats_row:
        return {
            "error": f"未找到交易日期 {trade_date} 的涨停板数据"
        }
    
    # 构建结果
    result = {
        "trade_date": trade_date,
        "summary": {
            "limit_up_count": stats_row["limit_up_count"],
            "first_limit_up_count": stats_row["first_limit_up_count"],
            "continuous_limit_up_count": stats_row["continuous_limit_up_count"],
            "blown_board_count": stats_row["blown_board_count"],
            "avg_limit_up_pct": float(stats_row["avg_limit_up_pct"]) if stats_row["avg_limit_up_pct"] is not None else None,
            "avg_turnover_rate": float(stats_row["avg_turnover_rate"]) if stats_row["avg_turnover_rate"] is not None else None,
            "avg_amount": float(stats_row["avg_amount"]) if stats_row["avg_amount"] is not None else None
        },
        "theme_distribution": [],
        "status_distribution": [],
        "time_distribution": []
    }
    
    # 填充主题分布数据
    for row in theme_rows:
        result["theme_distribution"].append({
            "theme": row["theme"],
            "count": row["count"]
        })
    
    # 填充连板分布数据
    for row in status_rows:
        result["status_distribution"].append({
            "status": row["status"],
            "count": row["count"]
        })
    
    # 填充时间分布数据
    for row in time_rows:
        result["time_distribution"].append({
            "time_period": row["time_period"],
            "count": row["count"]
        })
    
    return result 