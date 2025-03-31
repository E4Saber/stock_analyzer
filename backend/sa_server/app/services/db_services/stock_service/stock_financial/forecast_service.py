import pandas as pd
from decimal import Decimal
from typing import List, Optional, Dict, Any
from app.external.tushare_api.financial_info_api import get_forecast
from app.data.db_modules.stock_modules.stock_financial.forecast import ForecastData

class ForecastService:
    """业绩预告数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_forecast_data(self, ts_code: Optional[str] = None, 
                              ann_date: Optional[str] = None,
                              start_date: Optional[str] = None, 
                              end_date: Optional[str] = None,
                              period: Optional[str] = None,
                              type: Optional[str] = None,
                              batch_size: int = 1000) -> int:
        """
        从Tushare获取业绩预告数据并高效导入数据库
        
        参数:
            ts_code: 股票代码
            ann_date: 公告日期（YYYYMMDD格式）
            start_date: 公告开始日期
            end_date: 公告结束日期
            period: 报告期(每个季度最后一天的日期，比如20171231表示年报，20170630半年报，20170930三季报)
            type: 预告类型(预增/预减/扭亏/首亏/续亏/续盈/略增/略减)
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_forecast(ts_code=ts_code, ann_date=ann_date,
                              start_date=start_date, end_date=end_date,
                              period=period, type=type)
        
        if df_result is None or df_result.empty:
            print(f"未找到业绩预告数据: ts_code={ts_code}, period={period}, type={type}")
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
            date_fields = ['ann_date', 'end_date', 'first_ann_date']
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
                # 将批次数据转换为ForecastData对象
                forecast_data_list = []
                for record in batch:
                    try:
                        # 处理数字字段，确保它们是Decimal类型
                        for key, value in record.items():
                            if isinstance(value, (float, int)) and key not in ['id']:
                                record[key] = Decimal(str(value))
                        
                        forecast_data = ForecastData(**record)
                        forecast_data_list.append(forecast_data)
                    except Exception as e:
                        print(f"创建ForecastData对象失败 {record.get('ts_code', '未知')}, {record.get('end_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if forecast_data_list:
                    inserted = await self.batch_upsert_forecast(forecast_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条业绩预告记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_forecast(self, forecast_list: List[ForecastData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            forecast_list: 要插入或更新的业绩预告数据列表
            
        返回:
            处理的记录数
        """
        if not forecast_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = forecast_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 确保唯一性（按ts_code和end_date）
        unique_records = {}
        
        for forecast in forecast_list:
            # 创建唯一键
            key = (forecast.ts_code, str(forecast.end_date))
            
            # 根据最新公告日期选择记录
            if key not in unique_records or (forecast.ann_date and unique_records[key][1] and forecast.ann_date > unique_records[key][1]):
                unique_records[key] = (forecast, forecast.ann_date)
                print(f"保留记录: {forecast.ts_code}, {forecast.end_date}, ann_date={forecast.ann_date}")
            else:
                existing_date = unique_records[key][1]
                print(f"跳过记录: {forecast.ts_code}, {forecast.end_date}, "
                    f"ann_date={forecast.ann_date}，已存在ann_date={existing_date}的记录")
        
        # 提取最终的唯一记录列表
        unique_forecast_list = [record[0] for record in unique_records.values()]
        
        # 准备数据
        records = []
        for forecast in unique_forecast_list:
            forecast_dict = forecast.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = forecast_dict[col]
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
                    # 获取原表的列信息
                    column_types = await self._get_column_type(conn, 'forecast', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_forecast (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_forecast', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'end_date']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO forecast ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_forecast
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


# 快捷函数，用于导入特定股票的业绩预告数据
async def import_stock_forecast(db, ts_code: str, batch_size: int = 1000):
    """
    导入特定股票的业绩预告数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = ForecastService(db)
    count = await service.import_forecast_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条股票 {ts_code} 的业绩预告记录")
    return count


# 快捷函数，用于导入特定公告日期的业绩预告数据
async def import_ann_date_forecast(db, ann_date: str, batch_size: int = 1000):
    """
    导入特定公告日期的业绩预告数据
    
    参数:
        db: 数据库连接对象
        ann_date: 公告日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = ForecastService(db)
    count = await service.import_forecast_data(ann_date=ann_date, batch_size=batch_size)
    print(f"成功导入 {count} 条公告日期为 {ann_date} 的业绩预告记录")
    return count


# 快捷函数，用于导入特定报告期的业绩预告数据
async def import_period_forecast(db, period: str, batch_size: int = 1000):
    """
    导入特定报告期的业绩预告数据
    
    参数:
        db: 数据库连接对象
        period: 报告期(每个季度最后一天的日期，比如20171231表示年报，20170630半年报，20170930三季报)
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = ForecastService(db)
    count = await service.import_forecast_data(period=period, batch_size=batch_size)
    
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
    print(f"成功导入 {count} 条报告期为 {period_info} 的业绩预告记录")
    return count


# 快捷函数，用于导入特定公告日期范围的业绩预告数据
async def import_ann_date_range_forecast(db, start_date: str, end_date: str, batch_size: int = 1000):
    """
    导入特定公告日期范围的业绩预告数据
    
    参数:
        db: 数据库连接对象
        start_date: 公告开始日期（YYYYMMDD格式）
        end_date: 公告结束日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = ForecastService(db)
    count = await service.import_forecast_data(start_date=start_date, end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条公告日期范围为 {start_date} 至 {end_date} 的业绩预告记录")
    return count


# 快捷函数，用于导入特定类型的业绩预告数据
async def import_type_forecast(db, type: str, batch_size: int = 1000):
    """
    导入特定类型的业绩预告数据
    
    参数:
        db: 数据库连接对象
        type: 预告类型(预增/预减/扭亏/首亏/续亏/续盈/略增/略减)
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = ForecastService(db)
    count = await service.import_forecast_data(type=type, batch_size=batch_size)
    print(f"成功导入 {count} 条类型为 {type} 的业绩预告记录")
    return count


# 综合导入函数，支持多种参数组合
async def import_forecast_with_params(db, **kwargs):
    """
    根据提供的参数导入业绩预告数据
    
    参数:
        db: 数据库连接对象
        **kwargs: 可包含 ts_code, ann_date, start_date, end_date, period, type, batch_size 等参数
        
    返回:
        导入的记录数
    """
    service = ForecastService(db)
    batch_size = kwargs.pop('batch_size', 1000)  # 提取并移除batch_size参数
    
    # 构建参数描述
    param_desc = []
    for key, value in kwargs.items():
        if value:
            param_desc.append(f"{key}={value}")
    
    params_info = ", ".join(param_desc) if param_desc else "所有可用参数"
    
    # 导入数据
    count = await service.import_forecast_data(batch_size=batch_size, **kwargs)
    print(f"成功导入 {count} 条业绩预告记录 ({params_info})")
    return count


# 导入所有业绩预告数据
async def import_all_forecast(db, batch_size: int = 1000):
    """
    导入所有可获取的业绩预告数据
    
    注意: 这可能会请求大量数据，请确保有足够的网络带宽和系统资源。
    根据数据量大小，此操作可能需要较长时间完成。
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小，默认1000条
        
    返回:
        导入的记录总数
    """
    service = ForecastService(db)
    
    print("开始导入所有业绩预告数据，此操作可能需要较长时间...")
    count = await service.import_forecast_data(batch_size=batch_size)
    
    print(f"成功导入所有业绩预告数据，共 {count} 条记录")
    return count


# 动态查询业绩预告数据
async def query_forecast_data(db, 
                          filters: Optional[Dict[str, Any]] = None, 
                          order_by: Optional[List[str]] = None,
                          limit: Optional[int] = None,
                          offset: Optional[int] = None):
    """
    动态查询业绩预告数据，支持任意字段过滤和自定义排序
    
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
        List[ForecastData]: 符合条件的业绩预告数据列表
    
    示例:
        # 查询某股票最近的业绩预告数据
        data = await query_forecast_data(
            db,
            filters={
                'ts_code': '000001.SZ',
                'end_date__ge': '20220101'
            },
            order_by=['-end_date']
        )
        
        # 分页查询某类型的业绩预告
        data = await query_forecast_data(
            db,
            filters={'type': '预增'},
            order_by=['-ann_date', 'ts_code'],
            limit=20,
            offset=0
        )
    """
    from app.db.crud.stock_crud.stock_financial.forecast_crud import ForecastCRUD
    
    crud = ForecastCRUD(db)
    results = await crud.get_forecasts(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 获取特定类型的业绩预告记录
async def get_forecast_by_type(db, forecast_type: str, limit: int = 100):
    """
    获取特定类型的业绩预告记录
    
    参数:
        db: 数据库连接对象
        forecast_type: 业绩预告类型(预增/预减/扭亏/首亏/续亏/续盈/略增/略减)
        limit: 最大返回记录数
        
    返回:
        List[ForecastData]: 特定类型的业绩预告记录列表
    """
    return await query_forecast_data(
        db,
        filters={'type': forecast_type},
        order_by=['-ann_date'],
        limit=limit
    )


# 获取特定股票的历史业绩预告
async def get_stock_historical_forecasts(db, ts_code: str, limit: int = 20):
    """
    获取特定股票的历史业绩预告记录
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        limit: 最大返回记录数
        
    返回:
        List[ForecastData]: 股票的历史业绩预告记录列表
    """
    return await query_forecast_data(
        db,
        filters={'ts_code': ts_code},
        order_by=['-end_date'],
        limit=limit
    )


# 获取预计业绩大幅增长的股票
async def get_high_growth_stocks(db, min_growth_rate: float = 50.0, limit: int = 100):
    """
    获取预计业绩大幅增长的股票
    
    参数:
        db: 数据库连接对象
        min_growth_rate: 最小增长率（%）
        limit: 最大返回记录数
        
    返回:
        List[ForecastData]: 预计业绩大幅增长的股票列表
    """
    return await query_forecast_data(
        db,
        filters={'p_change_min__ge': min_growth_rate},
        order_by=['-p_change_min'],
        limit=limit
    )


# 获取预计扭亏为盈的股票
async def get_turnaround_stocks(db, limit: int = 100):
    """
    获取预计扭亏为盈的股票
    
    参数:
        db: 数据库连接对象
        limit: 最大返回记录数
        
    返回:
        List[ForecastData]: 预计扭亏为盈的股票列表
    """
    return await query_forecast_data(
        db,
        filters={'type': '扭亏'},
        order_by=['-ann_date'],
        limit=limit
    )


# 获取特定报告期内预告利润增长最多的股票
async def get_top_profit_growth_stocks(db, period: str, top_n: int = 20):
    """
    获取特定报告期内预告利润增长最多的股票
    
    参数:
        db: 数据库连接对象
        period: 报告期，格式YYYYMMDD
        top_n: 返回前N只股票
        
    返回:
        List[ForecastData]: 利润增长最多的股票列表
    """
    # 处理期间格式
    formatted_period = period
    if period and len(period) == 8:
        formatted_period = f"{period[:4]}-{period[4:6]}-{period[6:8]}"
    
    return await query_forecast_data(
        db,
        filters={'end_date': formatted_period},
        order_by=['-p_change_max'],
        limit=top_n
    )


# 分析业绩预告变动原因
async def analyze_forecast_change_reasons(db, top_n: int = 100):
    """
    分析业绩预告变动原因，统计最常见的变动原因
    
    参数:
        db: 数据库连接对象
        top_n: 分析的记录数量
        
    返回:
        Dict: 变动原因统计结果
    """
    # 获取最新的业绩预告数据
    forecasts = await query_forecast_data(
        db,
        order_by=['-ann_date'],
        limit=top_n
    )
    
    # 统计变动原因
    reasons = {}
    for forecast in forecasts:
        if forecast.change_reason:
            # 简单处理，提取关键词
            keywords = [word.strip() for word in forecast.change_reason.split('、')]
            for keyword in keywords:
                if keyword in reasons:
                    reasons[keyword] += 1
                else:
                    reasons[keyword] = 1
    
    # 按出现频率排序
    sorted_reasons = {k: v for k, v in sorted(reasons.items(), key=lambda item: item[1], reverse=True)}
    
    return sorted_reasons