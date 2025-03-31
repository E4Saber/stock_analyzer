import pandas as pd
from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.external.tushare_api.financial_info_api import get_express
from app.data.db_modules.stock_modules.stock_financial.express import ExpressData

class ExpressService:
    """业绩快报数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_express_data(self, ts_code: Optional[str] = None, 
                              ann_date: Optional[str] = None,
                              start_date: Optional[str] = None, 
                              end_date: Optional[str] = None,
                              period: Optional[str] = None,
                              batch_size: int = 1000) -> int:
        """
        从Tushare获取业绩快报数据并高效导入数据库
        
        参数:
            ts_code: 股票代码
            ann_date: 公告日期（YYYYMMDD格式）
            start_date: 公告开始日期
            end_date: 公告结束日期
            period: 报告期(每个季度最后一天的日期，比如20171231表示年报，20170630半年报，20170930三季报)
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_express(ts_code=ts_code, ann_date=ann_date,
                             start_date=start_date, end_date=end_date,
                             period=period)
        
        if df_result is None or df_result.empty:
            print(f"未找到业绩快报数据: ts_code={ts_code}, period={period}")
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
                # 将批次数据转换为ExpressData对象
                express_data_list = []
                for record in batch:
                    try:
                        # 处理数字字段，确保它们是Decimal类型
                        for key, value in record.items():
                            if isinstance(value, (float, int)) and key not in ['id', 'is_audit']:
                                record[key] = Decimal(str(value))
                        
                        express_data = ExpressData(**record)
                        express_data_list.append(express_data)
                    except Exception as e:
                        print(f"创建ExpressData对象失败 {record.get('ts_code', '未知')}, {record.get('end_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if express_data_list:
                    inserted = await self.batch_upsert_express(express_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条业绩快报记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_express(self, express_list: List[ExpressData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            express_list: 要插入或更新的业绩快报数据列表
            
        返回:
            处理的记录数
        """
        if not express_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = express_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 确保唯一性（按ts_code和end_date）
        unique_records = {}
        
        for express in express_list:
            # 创建唯一键
            key = (express.ts_code, str(express.end_date))
            
            # 根据最新公告日期选择记录
            if key not in unique_records or (express.ann_date and unique_records[key][1] and express.ann_date > unique_records[key][1]):
                unique_records[key] = (express, express.ann_date)
                print(f"保留记录: {express.ts_code}, {express.end_date}, ann_date={express.ann_date}")
            else:
                existing_date = unique_records[key][1]
                print(f"跳过记录: {express.ts_code}, {express.end_date}, "
                    f"ann_date={express.ann_date}，已存在ann_date={existing_date}的记录")
        
        # 提取最终的唯一记录列表
        unique_express_list = [record[0] for record in unique_records.values()]
        
        # 准备数据
        records = []
        for express in unique_express_list:
            express_dict = express.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = express_dict[col]
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
                    column_types = await self._get_column_type(conn, 'express', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_express (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_express', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'end_date']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO express ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_express
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


# 快捷函数，用于导入特定股票的业绩快报数据
async def import_stock_express(db, ts_code: str, batch_size: int = 1000):
    """
    导入特定股票的业绩快报数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = ExpressService(db)
    count = await service.import_express_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条股票 {ts_code} 的业绩快报记录")
    return count


# 快捷函数，用于导入特定公告日期的业绩快报数据
async def import_ann_date_express(db, ann_date: str, batch_size: int = 1000):
    """
    导入特定公告日期的业绩快报数据
    
    参数:
        db: 数据库连接对象
        ann_date: 公告日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = ExpressService(db)
    count = await service.import_express_data(ann_date=ann_date, batch_size=batch_size)
    print(f"成功导入 {count} 条公告日期为 {ann_date} 的业绩快报记录")
    return count


# 快捷函数，用于导入特定报告期的业绩快报数据
async def import_period_express(db, period: str, batch_size: int = 1000):
    """
    导入特定报告期的业绩快报数据
    
    参数:
        db: 数据库连接对象
        period: 报告期(每个季度最后一天的日期，比如20171231表示年报，20170630半年报，20170930三季报)
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = ExpressService(db)
    count = await service.import_express_data(period=period, batch_size=batch_size)
    
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
    print(f"成功导入 {count} 条报告期为 {period_info} 的业绩快报记录")
    return count


# 快捷函数，用于导入特定公告日期范围的业绩快报数据
async def import_ann_date_range_express(db, start_date: str, end_date: str, batch_size: int = 1000):
    """
    导入特定公告日期范围的业绩快报数据
    
    参数:
        db: 数据库连接对象
        start_date: 公告开始日期（YYYYMMDD格式）
        end_date: 公告结束日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = ExpressService(db)
    count = await service.import_express_data(start_date=start_date, end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条公告日期范围为 {start_date} 至 {end_date} 的业绩快报记录")
    return count


# 综合导入函数，支持多种参数组合
async def import_express_with_params(db, **kwargs):
    """
    根据提供的参数导入业绩快报数据
    
    参数:
        db: 数据库连接对象
        **kwargs: 可包含 ts_code, ann_date, start_date, end_date, period, batch_size 等参数
        
    返回:
        导入的记录数
    """
    service = ExpressService(db)
    batch_size = kwargs.pop('batch_size', 1000)  # 提取并移除batch_size参数
    
    # 构建参数描述
    param_desc = []
    for key, value in kwargs.items():
        if value:
            param_desc.append(f"{key}={value}")
    
    params_info = ", ".join(param_desc) if param_desc else "所有可用参数"
    
    # 导入数据
    count = await service.import_express_data(batch_size=batch_size, **kwargs)
    print(f"成功导入 {count} 条业绩快报记录 ({params_info})")
    return count


# 导入所有业绩快报数据
async def import_all_express(db, batch_size: int = 1000):
    """
    导入所有可获取的业绩快报数据
    
    注意: 这可能会请求大量数据，请确保有足够的网络带宽和系统资源。
    根据数据量大小，此操作可能需要较长时间完成。
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小，默认1000条
        
    返回:
        导入的记录总数
    """
    service = ExpressService(db)
    
    print("开始导入所有业绩快报数据，此操作可能需要较长时间...")
    count = await service.import_express_data(batch_size=batch_size)
    
    print(f"成功导入所有业绩快报数据，共 {count} 条记录")
    return count


# 动态查询业绩快报数据
async def query_express_data(db, 
                          filters: Optional[Dict[str, Any]] = None, 
                          order_by: Optional[List[str]] = None,
                          limit: Optional[int] = None,
                          offset: Optional[int] = None):
    """
    动态查询业绩快报数据，支持任意字段过滤和自定义排序
    
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
        List[ExpressData]: 符合条件的业绩快报数据列表
    
    示例:
        # 查询某股票最近的业绩快报数据
        data = await query_express_data(
            db,
            filters={
                'ts_code': '000001.SZ',
                'end_date__ge': '20220101'
            },
            order_by=['-end_date']
        )
        
        # 分页查询营业收入同比增长超过50%的公司
        data = await query_express_data(
            db,
            filters={'yoy_sales__gt': 50},
            order_by=['-yoy_sales', 'ts_code'],
            limit=20,
            offset=0
        )
    """
    from app.db.crud.stock_crud.stock_financial.express_crud import ExpressCRUD
    
    crud = ExpressCRUD(db)
    results = await crud.get_express(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 获取特定股票的历史业绩快报
async def get_stock_historical_express(db, ts_code: str, limit: int = 20):
    """
    获取特定股票的历史业绩快报记录
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        limit: 最大返回记录数
        
    返回:
        List[ExpressData]: 股票的历史业绩快报记录列表
    """
    return await query_express_data(
        db,
        filters={'ts_code': ts_code},
        order_by=['-end_date'],
        limit=limit
    )


# 获取高增长公司
async def get_high_growth_companies(db, growth_field: str = 'yoy_sales', threshold: float = 30.0, limit: int = 100):
    """
    获取特定指标高增长的公司
    
    参数:
        db: 数据库连接对象
        growth_field: 增长指标字段名称 (yoy_sales, yoy_op, yoy_tp, yoy_dedu_np, yoy_eps 等)
        threshold: 增长率阈值（%）
        limit: 最大返回记录数
        
    返回:
        List[ExpressData]: 高增长公司列表
    """
    # 验证增长字段
    valid_growth_fields = ['yoy_sales', 'yoy_op', 'yoy_tp', 'yoy_dedu_np', 'yoy_eps', 'yoy_roe', 
                          'growth_assets', 'yoy_equity', 'growth_bps']
    
    if growth_field not in valid_growth_fields:
        raise ValueError(f"无效的增长字段: {growth_field}，有效字段: {', '.join(valid_growth_fields)}")
    
    return await query_express_data(
        db,
        filters={f'{growth_field}__ge': threshold},
        order_by=[f'-{growth_field}'],
        limit=limit
    )


# 获取特定报告期内盈利增长最多的公司
async def get_top_profit_growth_companies(db, period: str, top_n: int = 20):
    """
    获取特定报告期内盈利增长最多的公司
    
    参数:
        db: 数据库连接对象
        period: 报告期，格式YYYYMMDD
        top_n: 返回前N只股票
        
    返回:
        List[ExpressData]: 盈利增长最多的公司列表
    """
    # 处理期间格式
    formatted_period = period
    if period and len(period) == 8:
        formatted_period = f"{period[:4]}-{period[4:6]}-{period[6:8]}"
    
    return await query_express_data(
        db,
        filters={'end_date': formatted_period},
        order_by=['-yoy_dedu_np'],
        limit=top_n
    )


# 获取净资产收益率最高的公司
async def get_top_roe_companies(db, period: str = None, top_n: int = 20):
    """
    获取净资产收益率最高的公司
    
    参数:
        db: 数据库连接对象
        period: 报告期，格式YYYYMMDD，为None时查询最新报告期
        top_n: 返回前N只股票
        
    返回:
        List[ExpressData]: 净资产收益率最高的公司列表
    """
    filters = {}
    
    if period:
        # 处理期间格式
        formatted_period = period
        if len(period) == 8:
            formatted_period = f"{period[:4]}-{period[4:6]}-{period[6:8]}"
        filters['end_date'] = formatted_period
    
    return await query_express_data(
        db,
        filters=filters,
        order_by=['-diluted_roe'],
        limit=top_n
    )


# 获取最新的业绩快报
async def get_latest_express_reports(db, days: int = 30, limit: int = 100):
    """
    获取最近一段时间内发布的业绩快报
    
    参数:
        db: 数据库连接对象
        days: 最近的天数
        limit: 最大返回记录数
        
    返回:
        List[ExpressData]: 最新的业绩快报列表
    """
    # 计算最近days天的日期
    import datetime
    today = datetime.datetime.now().date()
    start_date = (today - datetime.timedelta(days=days)).strftime('%Y%m%d')
    
    return await query_express_data(
        db,
        filters={'ann_date__ge': start_date},
        order_by=['-ann_date'],
        limit=limit
    )


# 比较多家公司的业绩快报
async def compare_companies_express(db, ts_codes: List[str], end_date: str):
    """
    比较多家公司在特定报告期的业绩快报
    
    参数:
        db: 数据库连接对象
        ts_codes: 股票代码列表
        end_date: 报告期，格式YYYYMMDD
        
    返回:
        List[ExpressData]: 多家公司的业绩快报
    """
    # 处理期间格式
    formatted_end_date = end_date
    if end_date and len(end_date) == 8:
        formatted_end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
    
    return await query_express_data(
        db,
        filters={
            'ts_code__in': ts_codes,
            'end_date': formatted_end_date
        },
        order_by=['ts_code']
    )


# 分析特定公司的业绩趋势
async def analyze_company_express_trend(db, ts_code: str, metrics: List[str] = None):
    """
    分析特定公司的业绩趋势
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        metrics: 要分析的指标列表，默认为 ['revenue', 'operate_profit', 'n_income', 'diluted_roe']
        
    返回:
        Dict: 包含各指标历史趋势的字典
    """
    if metrics is None:
        metrics = ['revenue', 'operate_profit', 'n_income', 'diluted_roe']
    
    # 获取公司的历史数据
    express_data = await get_stock_historical_express(db, ts_code, limit=20)
    
    # 按报告期排序
    sorted_data = sorted(express_data, key=lambda x: x.end_date if x.end_date else datetime.date.min)
    
    # 按指标提取数据
    result = {metric: [] for metric in metrics}
    
    for data in sorted_data:
        for metric in metrics:
            value = getattr(data, metric, None)
            period = data.end_date.strftime('%Y-%m-%d') if data.end_date else 'Unknown'
            
            result[metric].append({
                'period': period,
                'value': float(value) if value is not None else None
            })
    
    return result