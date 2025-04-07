import pandas as pd
from typing import List, Optional, Dict, Any
from app.external.tushare_api.hk_stock_api import get_hk_daily_adj
from app.data.db_modules.hk_stock_modules.hk_daily_adj import HkDailyAdjData

class HkDailyAdjService:
    """香港股票复权日线行情数据导入服务，实现高效批量导入和数据管理"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_hk_daily_adj_data(self, 
                                      ts_code: Optional[str] = None, 
                                      trade_date: Optional[str] = None,
                                      start_date: Optional[str] = None,
                                      end_date: Optional[str] = None,
                                      batch_size: int = 1000) -> int:
        """
        从Tushare获取香港股票复权日线数据并高效导入数据库
        
        参数:
            ts_code: 股票代码
            trade_date: 交易日期 (YYYYMMDD格式)
            start_date: 开始日期 (YYYYMMDD格式)
            end_date: 结束日期 (YYYYMMDD格式)
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
        if start_date:
            params.append(f"start_date={start_date}")
        if end_date:
            params.append(f"end_date={end_date}")
        
        param_desc = ", ".join(params) if params else "所有"
        print(f"正在获取香港股票复权日线数据: {param_desc}")
        
        # 从Tushare获取数据
        try:
            df_result = get_hk_daily_adj(
                ts_code=ts_code, 
                trade_date=trade_date, 
                start_date=start_date,
                end_date=end_date
            )
            
            if df_result is None or df_result.empty:
                print(f"未找到香港股票复权日线数据: {param_desc}")
                return 0
                
            print(f"获取到 {len(df_result)} 条香港股票复权日线数据")
        except Exception as e:
            print(f"获取香港股票复权日线数据失败: {str(e)}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 数据预处理和验证
        valid_records = await self._preprocess_records(records)
        
        if not valid_records:
            print("没有有效的香港股票复权日线数据记录可导入")
            return 0
            
        # 分批处理
        batches = [valid_records[i:i + batch_size] for i in range(0, len(valid_records), batch_size)]
        total_count = 0
        
        for batch_idx, batch in enumerate(batches):
            try:
                # 将批次数据转换为HkDailyAdjData对象
                daily_adj_data_list = []
                for record in batch:
                    try:
                        # 为了确保数据类型正确，显式处理数值字段
                        float_fields = ['open', 'high', 'low', 'close', 'pre_close', 'change', 
                                      'pct_change', 'amount', 'vwap', 'adj_factor', 
                                      'turnover_ratio', 'free_mv', 'total_mv']
                        
                        for field in float_fields:
                            if field in record and record[field] is not None:
                                if isinstance(record[field], str) and record[field].strip() == '':
                                    record[field] = None
                                elif record[field] is not None:
                                    try:
                                        record[field] = float(record[field])
                                    except (ValueError, TypeError):
                                        record[field] = None
                        
                        int_fields = ['vol', 'free_share', 'total_share']
                        for field in int_fields:
                            if field in record and record[field] is not None:
                                if isinstance(record[field], str) and record[field].strip() == '':
                                    record[field] = None
                                elif record[field] is not None:
                                    try:
                                        record[field] = int(float(record[field]))
                                    except (ValueError, TypeError):
                                        record[field] = None
                        
                        daily_adj_data = HkDailyAdjData(**record)
                        daily_adj_data_list.append(daily_adj_data)
                    except Exception as e:
                        print(f"创建HkDailyAdjData对象失败 {record.get('ts_code', '未知')}, {record.get('trade_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if daily_adj_data_list:
                    inserted = await self.batch_upsert_hk_daily_adj(daily_adj_data_list)
                    total_count += inserted
                    print(f"批次 {batch_idx + 1}/{len(batches)} 导入成功: {inserted} 条香港股票复权日线数据")
            except Exception as e:
                print(f"批次 {batch_idx + 1}/{len(batches)} 导入失败: {str(e)}")
        
        print(f"总共成功导入 {total_count} 条香港股票复权日线数据")
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
            if record['ts_code'] == '' or record['trade_date'] is None:
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
    
    async def batch_upsert_hk_daily_adj(self, daily_adj_list: List[HkDailyAdjData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            daily_adj_list: 要插入或更新的香港股票复权日线数据列表
            
        返回:
            处理的记录数
        """
        if not daily_adj_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = daily_adj_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 使用字典来存储记录，如果有重复键，保留最新记录
        unique_records = {}
        
        for daily_adj in daily_adj_list:
            # 创建唯一键 (ts_code, trade_date)
            key = (daily_adj.ts_code, str(daily_adj.trade_date))
            unique_records[key] = daily_adj
        
        # 提取最终的唯一记录列表
        unique_daily_adj_list = list(unique_records.values())
        
        # 准备数据
        records = []
        for daily_adj in unique_daily_adj_list:
            daily_adj_dict = daily_adj.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = daily_adj_dict[col]
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
                    column_types = await self._get_column_type(conn, 'hk_daily_adj', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_hk_daily_adj (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_hk_daily_adj', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'trade_date']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO hk_daily_adj ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_hk_daily_adj
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


# 快捷函数，用于导入特定股票代码的复权日线数据
async def import_hk_daily_adj_by_ts_code(db, ts_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, batch_size: int = 1000) -> int:
    """
    导入特定股票代码的香港股票复权日线数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        start_date: 开始日期 (YYYYMMDD格式，可选)
        end_date: 结束日期 (YYYYMMDD格式，可选)
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = HkDailyAdjService(db)
    count = await service.import_hk_daily_adj_data(
        ts_code=ts_code,
        start_date=start_date,
        end_date=end_date,
        batch_size=batch_size
    )
    
    date_range = ""
    if start_date and end_date:
        date_range = f"从 {start_date} 到 {end_date} 的"
    elif start_date:
        date_range = f"从 {start_date} 开始的"
    elif end_date:
        date_range = f"截止到 {end_date} 的"
    
    print(f"成功导入 {count} 条{date_range}股票 {ts_code} 的复权日线数据")
    return count


# 快捷函数，用于导入特定交易日期的复权日线数据
async def import_hk_daily_adj_by_trade_date(db, trade_date: str, batch_size: int = 1000) -> int:
    """
    导入特定交易日期的香港股票复权日线数据
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期 (YYYYMMDD格式)
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = HkDailyAdjService(db)
    count = await service.import_hk_daily_adj_data(
        trade_date=trade_date,
        batch_size=batch_size
    )
    print(f"成功导入 {count} 条交易日期为 {trade_date} 的香港股票复权日线数据")
    return count


# 快捷函数，用于导入指定日期范围的复权日线数据
async def import_hk_daily_adj_by_date_range(db, start_date: str, end_date: str, batch_size: int = 1000) -> int:
    """
    导入指定日期范围的香港股票复权日线数据
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期 (YYYYMMDD格式)
        end_date: 结束日期 (YYYYMMDD格式)
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = HkDailyAdjService(db)
    count = await service.import_hk_daily_adj_data(
        start_date=start_date,
        end_date=end_date,
        batch_size=batch_size
    )
    print(f"成功导入 {count} 条从 {start_date} 到 {end_date} 的香港股票复权日线数据")
    return count


# 从数据库中查询香港股票复权日线数据
async def query_hk_daily_adj_data(db, 
                                filters: Optional[Dict[str, Any]] = None, 
                                order_by: Optional[List[str]] = None,
                                limit: Optional[int] = None,
                                offset: Optional[int] = None) -> List[HkDailyAdjData]:
    """
    动态查询香港股票复权日线数据，支持任意字段过滤和自定义排序
    
    参数:
        db: 数据库连接对象
        filters: 过滤条件字典，支持以下操作符后缀:
                 - __eq: 等于 (默认)
                 - __ne: 不等于
                 - __gt: 大于
                 - __ge: 大于等于
                 - __lt: 小于
                 - __le: 小于等于
                 - __in: IN包含查询
                 例如: {'ts_code': '00700.HK', 'close__gt': 300}
        order_by: 排序字段列表，字段前加"-"表示降序，例如['-trade_date', 'ts_code']
        limit: 最大返回记录数
        offset: 跳过前面的记录数（用于分页）
        
    返回:
        List[HkDailyAdjData]: 符合条件的香港股票复权日线数据列表
    
    示例:
        # 查询腾讯控股最近10天的复权数据
        data = await query_hk_daily_adj_data(
            db,
            filters={'ts_code': '00700.HK'},
            order_by=['-trade_date'],
            limit=10
        )
        
        # 查询所有流通市值大于1000亿的股票
        data = await query_hk_daily_adj_data(
            db,
            filters={'free_mv__gt': 100000000000, 'trade_date': '20230101'},
            order_by=['ts_code'],
            limit=20
        )
    """
    from app.db.crud.hk_stock_crud.hk_daily_adj_crud import HkDailyAdjCRUD
    
    crud = HkDailyAdjCRUD(db)
    results = await crud.get_hk_daily_adj(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 计算前复权数据
async def calculate_qfq_prices(db, ts_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    计算指定股票的前复权价格
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        start_date: 开始日期 (YYYYMMDD格式，可选)
        end_date: 结束日期 (YYYYMMDD格式，可选)
        
    返回:
        List[Dict]: 包含前复权价格的数据列表
    """
    # 获取原始数据
    from app.db.crud.hk_stock_crud.hk_daily_adj_crud import HkDailyAdjCRUD
    
    crud = HkDailyAdjCRUD(db)
    filters = {'ts_code': ts_code}
    
    if start_date:
        filters['trade_date__ge'] = start_date
    if end_date:
        filters['trade_date__le'] = end_date
        
    daily_adj_data = await crud.get_hk_daily_adj(
        filters=filters,
        order_by=['trade_date']  # 按时间正序排列，便于计算复权
    )
    
    if not daily_adj_data:
        return []
    
    # 将数据转换为pandas DataFrame便于计算
    import pandas as pd
    df = pd.DataFrame([d.model_dump() for d in daily_adj_data])
    
    # 确保有复权因子列
    if 'adj_factor' not in df.columns or df['adj_factor'].isna().all():
        print(f"警告: 股票 {ts_code} 缺少复权因子数据，无法计算前复权价格")
        return df.to_dict('records')
    
    # 获取最新的复权因子作为基准
    latest_factor = df['adj_factor'].iloc[-1]
    
    # 计算前复权价格
    df['qfq_open'] = df['open'] * df['adj_factor'] / latest_factor
    df['qfq_high'] = df['high'] * df['adj_factor'] / latest_factor
    df['qfq_low'] = df['low'] * df['adj_factor'] / latest_factor
    df['qfq_close'] = df['close'] * df['adj_factor'] / latest_factor
    df['qfq_pre_close'] = df['pre_close'] * df['adj_factor'] / latest_factor
    
    # 保留两位小数
    for col in ['qfq_open', 'qfq_high', 'qfq_low', 'qfq_close', 'qfq_pre_close']:
        df[col] = df[col].round(2)
    
    # 转换回字典列表
    result = df.to_dict('records')
    
    return result


# 计算后复权数据
async def calculate_hfq_prices(db, ts_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    计算指定股票的后复权价格
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        start_date: 开始日期 (YYYYMMDD格式，可选)
        end_date: 结束日期 (YYYYMMDD格式，可选)
        
    返回:
        List[Dict]: 包含后复权价格的数据列表
    """
    # 获取原始数据
    from app.db.crud.hk_stock_crud.hk_daily_adj_crud import HkDailyAdjCRUD
    
    crud = HkDailyAdjCRUD(db)
    filters = {'ts_code': ts_code}
    
    if start_date:
        filters['trade_date__ge'] = start_date
    if end_date:
        filters['trade_date__le'] = end_date
        
    daily_adj_data = await crud.get_hk_daily_adj(
        filters=filters,
        order_by=['trade_date']  # 按时间正序排列，便于计算复权
    )
    
    if not daily_adj_data:
        return []
    
    # 将数据转换为pandas DataFrame便于计算
    import pandas as pd
    df = pd.DataFrame([d.model_dump() for d in daily_adj_data])
    
    # 确保有复权因子列
    if 'adj_factor' not in df.columns or df['adj_factor'].isna().all():
        print(f"警告: 股票 {ts_code} 缺少复权因子数据，无法计算后复权价格")
        return df.to_dict('records')
    
    # 获取第一个有效的复权因子作为基准
    first_valid_factor = df.loc[df['adj_factor'].notna(), 'adj_factor'].iloc[0]
    
    # 计算后复权价格
    df['hfq_open'] = df['open'] * df['adj_factor'] / first_valid_factor
    df['hfq_high'] = df['high'] * df['adj_factor'] / first_valid_factor
    df['hfq_low'] = df['low'] * df['adj_factor'] / first_valid_factor
    df['hfq_close'] = df['close'] * df['adj_factor'] / first_valid_factor
    df['hfq_pre_close'] = df['pre_close'] * df['adj_factor'] / first_valid_factor
    
    # 保留两位小数
    for col in ['hfq_open', 'hfq_high', 'hfq_low', 'hfq_close', 'hfq_pre_close']:
        df[col] = df[col].round(2)
    
    # 转换回字典列表
    result = df.to_dict('records')
    
    return result


# 获取最大市值股票排行
async def get_top_market_value_stocks(db, trade_date: str, top_n: int = 20, mv_type: str = 'total') -> Dict[str, Any]:
    """
    获取特定交易日市值最大的股票排行
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期 (YYYYMMDD格式)
        top_n: 返回前几名，默认20
        mv_type: 市值类型，'total'表示总市值，'free'表示流通市值
        
    返回:
        Dict: 包含市值排行的字典
    """
    # 处理日期格式
    formatted_date = trade_date
    if isinstance(trade_date, str) and trade_date.isdigit() and len(trade_date) == 8:
        formatted_date = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:8]}"
    
    # 根据市值类型选择查询字段
    mv_field = 'total_mv' if mv_type == 'total' else 'free_mv'
    
    # 查询市值排行
    query = f"""
    SELECT 
        d.ts_code, 
        b.name, 
        d.{mv_field}, 
        d.close, 
        d.pct_change, 
        d.vol, 
        d.amount,
        d.free_share,
        d.total_share
    FROM 
        hk_daily_adj d
    LEFT JOIN
        hk_basic b ON d.ts_code = b.ts_code
    WHERE 
        d.trade_date = $1::date
        AND d.{mv_field} IS NOT NULL
    ORDER BY 
        d.{mv_field} DESC
    LIMIT $2
    """
    
    rows = await db.fetch(query, formatted_date, top_n)
    
    if not rows:
        return {
            "error": f"未找到交易日 {trade_date} 的香港股票市值数据"
        }
    
    # 构建结果
    result = {
        "trade_date": trade_date,
        "mv_type": "总市值" if mv_type == 'total' else "流通市值",
        "top_stocks": []
    }
    
    total_mv = 0
    for row in rows:
        stock_data = dict(row)
        result["top_stocks"].append(stock_data)
        total_mv += stock_data[mv_field] if stock_data[mv_field] else 0
    
    # 添加汇总信息
    result["summary"] = {
        "total_count": len(rows),
        "total_market_value": total_mv
    }
    
    return result


# 获取换手率统计信息
async def get_turnover_statistics(db, trade_date: str, top_n: int = 20) -> Dict[str, Any]:
    """
    获取特定交易日换手率统计信息
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期 (YYYYMMDD格式)
        top_n: 返回的高换手率股票数量，默认20
        
    返回:
        Dict: 包含换手率统计信息的字典
    """
    # 处理日期格式
    formatted_date = trade_date
    if isinstance(trade_date, str) and trade_date.isdigit() and len(trade_date) == 8:
        formatted_date = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:8]}"
    
    # 查询换手率统计
    avg_query = """
    SELECT 
        AVG(turnover_ratio) as avg_turnover,
        MIN(turnover_ratio) as min_turnover,
        MAX(turnover_ratio) as max_turnover,
        STDDEV(turnover_ratio) as std_turnover,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY turnover_ratio) as median_turnover,
        COUNT(*) as total_stocks
    FROM 
        hk_daily_adj
    WHERE 
        trade_date = $1::date
        AND turnover_ratio IS NOT NULL
    """
    
    # 查询高换手率股票
    top_query = """
    SELECT 
        d.ts_code, 
        b.name, 
        d.turnover_ratio, 
        d.vol, 
        d.amount, 
        d.close, 
        d.pct_change
    FROM 
        hk_daily_adj d
    LEFT JOIN
        hk_basic b ON d.ts_code = b.ts_code
    WHERE 
        d.trade_date = $1::date
        AND d.turnover_ratio IS NOT NULL
    ORDER BY 
        d.turnover_ratio DESC
    LIMIT $2
    """
    
    avg_row = await db.fetchrow(avg_query, formatted_date)
    top_rows = await db.fetch(top_query, formatted_date, top_n)
    
    if not avg_row:
        return {
            "error": f"未找到交易日 {trade_date} 的香港股票换手率数据"
        }
    
    # 构建结果
    result = {
        "trade_date": trade_date,
        "statistics": {
            "avg_turnover": round(float(avg_row["avg_turnover"]), 2) if avg_row["avg_turnover"] is not None else None,
            "median_turnover": round(float(avg_row["median_turnover"]), 2) if avg_row["median_turnover"] is not None else None,
            "min_turnover": round(float(avg_row["min_turnover"]), 2) if avg_row["min_turnover"] is not None else None,
            "max_turnover": round(float(avg_row["max_turnover"]), 2) if avg_row["max_turnover"] is not None else None,
            "std_turnover": round(float(avg_row["std_turnover"]), 2) if avg_row["std_turnover"] is not None else None,
            "total_stocks": avg_row["total_stocks"]
        },
        "high_turnover_stocks": [dict(row) for row in top_rows]
    }
    
    return result