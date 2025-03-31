import pandas as pd
from decimal import Decimal
from typing import List, Optional, Dict, Any
from app.external.tushare_api.financial_info_api import get_cashflow
from app.data.db_modules.stock_modules.stock_financial.cashflow import CashflowData


class CashflowService:
    """现金流量表数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_cashflow_data(self, ts_code: Optional[str] = None, 
                              ann_date: Optional[str] = None,
                              f_ann_date: Optional[str] = None,
                              start_date: Optional[str] = None, 
                              end_date: Optional[str] = None,
                              period: Optional[str] = None,
                              report_type: Optional[str] = None,
                              comp_type: Optional[str] = None,
                              is_calc: Optional[int] = None,
                              batch_size: int = 1000) -> int:
        """
        从Tushare获取现金流量表数据并高效导入数据库
        
        参数:
            ts_code: 股票代码
            ann_date: 公告日期（YYYYMMDD格式）
            f_ann_date: 实际公告日期
            start_date: 公告开始日期
            end_date: 公告结束日期
            period: 报告期(每个季度最后一天的日期，比如20171231表示年报，20170630半年报，20170930三季报)
            report_type: 报告类型，参考文档最下方说明
            comp_type: 公司类型（1一般工商业2银行3保险4证券）
            is_calc: 是否计算报表
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_cashflow(ts_code=ts_code, ann_date=ann_date, f_ann_date=f_ann_date,
                             start_date=start_date, end_date=end_date, period=period,
                             report_type=report_type, comp_type=comp_type, is_calc=is_calc)
        
        if df_result is None or df_result.empty:
            print(f"未找到现金流量表数据: ts_code={ts_code}, period={period}, report_type={report_type}")
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
            date_fields = ['ann_date', 'f_ann_date', 'end_date']
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
                # 将批次数据转换为CashflowData对象
                cashflow_data_list = []
                for record in batch:
                    try:
                        # 处理数字字段，确保它们是Decimal类型
                        for key, value in record.items():
                            if isinstance(value, (float, int)) and key not in ['id']:
                                record[key] = Decimal(str(value))
                        
                        cashflow_data = CashflowData(**record)
                        cashflow_data_list.append(cashflow_data)
                    except Exception as e:
                        print(f"创建CashflowData对象失败 {record.get('ts_code', '未知')}, {record.get('end_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if cashflow_data_list:
                    inserted = await self.batch_upsert_cashflow(cashflow_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条现金流量表记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_cashflow(self, cashflow_list: List[CashflowData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            cashflow_list: 要插入或更新的现金流量表数据列表
            
        返回:
            处理的记录数
        """
        if not cashflow_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = cashflow_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 优先选择update_flag为1的记录
        # 使用字典来存储记录，如果有重复键，根据update_flag决定是否替换
        unique_records = {}
        
        for cashflow in cashflow_list:
            # 创建唯一键
            key = (cashflow.ts_code, str(cashflow.end_date), str(cashflow.report_type))
            
            # 获取update_flag，如果不存在则默认为0
            update_flag = getattr(cashflow, 'update_flag', '0')
            
            # 如果键不存在，或者当前记录的update_flag为1且已存记录的update_flag不为1，则更新
            if key not in unique_records or (update_flag == '1' and unique_records[key][1] != '1'):
                unique_records[key] = (cashflow, update_flag)
                print(f"保留记录: {cashflow.ts_code}, {cashflow.end_date}, {cashflow.report_type}, update_flag={update_flag}")
            else:
                existing_flag = unique_records[key][1]
                print(f"跳过记录: {cashflow.ts_code}, {cashflow.end_date}, {cashflow.report_type}, "
                    f"update_flag={update_flag}，已存在update_flag={existing_flag}的记录")
        
        # 提取最终的唯一记录列表
        unique_cashflow_list = [record[0] for record in unique_records.values()]
        
        # 准备数据
        records = []
        for cashflow in unique_cashflow_list:
            cashflow_dict = cashflow.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = cashflow_dict[col]
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
                    column_types = await self._get_column_type(conn, 'cashflow', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_cashflow (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_cashflow', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'end_date', 'report_type']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO cashflow ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_cashflow
                        ON CONFLICT (ts_code, end_date, report_type) DO UPDATE SET {update_clause}
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


# 快捷函数，用于导入特定股票的现金流量表数据
async def import_stock_cashflow(db, ts_code: str, batch_size: int = 1000):
    """
    导入特定股票的现金流量表数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = CashflowService(db)
    count = await service.import_cashflow_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条股票 {ts_code} 的现金流量表记录")
    return count


# 快捷函数，用于导入特定公告日期的现金流量表数据
async def import_ann_date_cashflow(db, ann_date: str, batch_size: int = 1000):
    """
    导入特定公告日期的现金流量表数据
    
    参数:
        db: 数据库连接对象
        ann_date: 公告日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = CashflowService(db)
    count = await service.import_cashflow_data(ann_date=ann_date, batch_size=batch_size)
    print(f"成功导入 {count} 条公告日期为 {ann_date} 的现金流量表记录")
    return count


# 快捷函数，用于导入特定实际公告日期的现金流量表数据
async def import_f_ann_date_cashflow(db, f_ann_date: str, batch_size: int = 1000):
    """
    导入特定实际公告日期的现金流量表数据
    
    参数:
        db: 数据库连接对象
        f_ann_date: 实际公告日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = CashflowService(db)
    count = await service.import_cashflow_data(f_ann_date=f_ann_date, batch_size=batch_size)
    print(f"成功导入 {count} 条实际公告日期为 {f_ann_date} 的现金流量表记录")
    return count


# 快捷函数，用于导入特定报告期的现金流量表数据
async def import_period_cashflow(db, period: str, batch_size: int = 1000):
    """
    导入特定报告期的现金流量表数据
    
    参数:
        db: 数据库连接对象
        period: 报告期(每个季度最后一天的日期，比如20171231表示年报，20170630半年报，20170930三季报)
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = CashflowService(db)
    count = await service.import_cashflow_data(period=period, batch_size=batch_size)
    
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
    print(f"成功导入 {count} 条报告期为 {period_info} 的现金流量表记录")
    return count


# 快捷函数，用于导入特定公告日期范围的现金流量表数据
async def import_ann_date_range_cashflow(db, start_date: str, end_date: str, batch_size: int = 1000):
    """
    导入特定公告日期范围的现金流量表数据
    
    参数:
        db: 数据库连接对象
        start_date: 公告开始日期（YYYYMMDD格式）
        end_date: 公告结束日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = CashflowService(db)
    count = await service.import_cashflow_data(start_date=start_date, end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条公告日期范围为 {start_date} 至 {end_date} 的现金流量表记录")
    return count


# 快捷函数，用于导入特定类型公司的现金流量表数据
async def import_company_type_cashflow(db, comp_type: str, batch_size: int = 1000):
    """
    导入特定类型公司的现金流量表数据
    
    参数:
        db: 数据库连接对象
        comp_type: 公司类型（1一般工商业2银行3保险4证券）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = CashflowService(db)
    count = await service.import_cashflow_data(comp_type=comp_type, batch_size=batch_size)
    
    comp_type_desc = {
        '1': '一般工商业',
        '2': '银行',
        '3': '保险',
        '4': '证券'
    }.get(comp_type, comp_type)
    
    print(f"成功导入 {count} 条 {comp_type_desc} 类型公司的现金流量表记录")
    return count


# 快捷函数，用于导入特定报告类型的现金流量表数据
async def import_report_type_cashflow(db, report_type: str, batch_size: int = 1000):
    """
    导入特定报告类型的现金流量表数据
    
    参数:
        db: 数据库连接对象
        report_type: 报告类型
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = CashflowService(db)
    count = await service.import_cashflow_data(report_type=report_type, batch_size=batch_size)
    
    report_type_desc = {
        '1': '合并报表',
        '2': '单季合并',
        '3': '调整单季合并表',
        '4': '调整合并报表',
        '5': '调整前合并报表',
        '6': '母公司报表',
        '7': '母公司单季表',
        '8': '母公司调整单季表',
        '9': '母公司调整表',
        '10': '母公司调整前报表',
        '11': '调整前合并报表',
        '12': '母公司调整前报表'
    }.get(report_type, f'类型{report_type}')
    
    print(f"成功导入 {count} 条报告类型为 {report_type_desc} 的现金流量表记录")
    return count


# 综合导入函数，支持多种参数组合
async def import_cashflow_with_params(db, **kwargs):
    """
    根据提供的参数导入现金流量表数据
    
    参数:
        db: 数据库连接对象
        **kwargs: 可包含 ts_code, ann_date, f_ann_date, start_date, end_date, period, report_type, comp_type, is_calc, batch_size 等参数
        
    返回:
        导入的记录数
    """
    service = CashflowService(db)
    batch_size = kwargs.pop('batch_size', 1000)  # 提取并移除batch_size参数
    
    # 构建参数描述
    param_desc = []
    for key, value in kwargs.items():
        if value:
            param_desc.append(f"{key}={value}")
    
    params_info = ", ".join(param_desc) if param_desc else "所有可用参数"
    
    # 导入数据
    count = await service.import_cashflow_data(batch_size=batch_size, **kwargs)
    print(f"成功导入 {count} 条现金流量表记录 ({params_info})")
    return count


# 导入所有现金流量表数据
async def import_all_cashflow(db, batch_size: int = 1000):
    """
    导入所有可获取的现金流量表数据
    
    注意: 这可能会请求大量数据，请确保有足够的网络带宽和系统资源。
    根据数据量大小，此操作可能需要较长时间完成。
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小，默认1000条
        
    返回:
        导入的记录总数
    """
    service = CashflowService(db)
    
    print("开始导入所有现金流量表数据，此操作可能需要较长时间...")
    count = await service.import_cashflow_data(batch_size=batch_size)
    
    print(f"成功导入所有现金流量表数据，共 {count} 条记录")
    return count

# 动态查询现金流量表数据
async def query_cashflow_data(db, 
                        filters: Optional[Dict[str, Any]] = None, 
                        order_by: Optional[List[str]] = None,
                        limit: Optional[int] = None,
                        offset: Optional[int] = None):
    """
    动态查询现金流量表数据，支持任意字段过滤和自定义排序
    
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
        List[CashflowData]: 符合条件的现金流量表数据列表
    
    示例:
        # 查询某股票最近两年的年报数据，按报告期降序排列
        data = await query_cashflow_data(
            db,
            filters={
                'ts_code': '000001.SZ',
                'end_date__ge': '20220101',
                'report_type': '1'  # 年报
            },
            order_by=['-end_date']
        )
        
        # 分页查询某行业所有经营活动现金流量净额超过一定值的公司
        data = await query_cashflow_data(
            db,
            filters={'n_cashflow_act__gt': 1000000000},
            order_by=['-n_cashflow_act', 'ts_code'],
            limit=20,
            offset=0
        )
    """
    from app.db.crud.stock_crud.stock_financial.cashflow_crud import CashflowCRUD
    
    crud = CashflowCRUD(db)
    results = await crud.get_cashflow(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results

# 查询特定公司多个报告期的现金流量表数据
async def get_company_cashflow_trend(db, ts_code: str, start_date: str = None, end_date: str = None, 
                                report_type: str = None, limit: int = 20):
    """
    查询特定公司在时间段内的现金流量表趋势数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        start_date: 开始日期，格式YYYYMMDD
        end_date: 结束日期，格式YYYYMMDD
        report_type: 报告类型（如年报、季报等）
        limit: 最大返回记录数
        
    返回:
        List[CashflowData]: 该公司的现金流量表趋势数据，按报告期降序排列
    """
    filters = {'ts_code': ts_code}
    
    if start_date:
        filters['end_date__ge'] = start_date
    
    if end_date:
        filters['end_date__le'] = end_date
    
    if report_type:
        filters['report_type'] = report_type
    
    return await query_cashflow_data(
        db,
        filters=filters,
        order_by=['-end_date'],
        limit=limit
    )


# 对比多家公司同期现金流量表数据
async def compare_companies_cashflow(db, ts_codes: List[str], end_date: str, report_type: str = '1'):
    """
    对比多家公司在同一报告期的现金流量表数据
    
    参数:
        db: 数据库连接对象
        ts_codes: 股票代码列表
        end_date: 报告期，格式YYYYMMDD
        report_type: 报告类型，默认为1（年报）
        
    返回:
        List[CashflowData]: 多家公司在指定报告期的现金流量表数据
    """
    return await query_cashflow_data(
        db,
        filters={
            'ts_code__in': ts_codes,
            'end_date': end_date,
            'report_type': report_type
        }
    )


# 查询经营活动现金流量净额最高的公司
async def get_top_operating_cashflow_companies(db, industry_codes: List[str] = None, 
                                        end_date: str = None, report_type: str = '1',
                                        top_n: int = 10):
    """
    查询特定行业或全市场经营活动现金流量净额最高的公司
    
    参数:
        db: 数据库连接对象
        industry_codes: 行业代码列表，为None时查询全市场
        end_date: 报告期，格式YYYYMMDD，为None时查询最新报告期
        report_type: 报告类型，默认为1（年报）
        top_n: 返回前N家公司
        
    返回:
        List[CashflowData]: 经营活动现金流量净额最高的公司数据
    """
    filters = {}
    
    if end_date:
        filters['end_date'] = end_date
    
    if report_type:
        filters['report_type'] = report_type
    
    # 如果提供了行业代码，需要先查询该行业的所有股票
    if industry_codes and len(industry_codes) > 0:
        # 假设有一个函数可以获取行业内的股票代码
        # industry_stocks = await get_industry_stocks(db, industry_codes)
        # filters['ts_code__in'] = industry_stocks
        
        # 如果没有这样的函数，这里暂时跳过行业筛选
        pass
    
    return await query_cashflow_data(
        db,
        filters=filters,
        order_by=['-n_cashflow_act'],
        limit=top_n
    )

# 分析公司现金流量结构
async def analyze_cashflow_structure(db, ts_code: str, end_date: str, report_type: str = '1'):
    """
    分析公司在特定报告期的现金流量结构
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        end_date: 报告期，格式YYYYMMDD
        report_type: 报告类型，默认为1（年报）
        
    返回:
        Dict: 包含现金流量分析的字典
    """
    # 查询指定公司和报告期的现金流量表
    cashflow_data = await query_cashflow_data(
        db,
        filters={
            'ts_code': ts_code,
            'end_date': end_date,
            'report_type': report_type
        }
    )
    
    if not cashflow_data or len(cashflow_data) == 0:
        return None
    
    data = cashflow_data[0]
    
    # 计算现金流量结构比例和分析
    analysis = {}
    
    # 计算各类现金流量净额在营业收入中的占比
    # 需要获取对应期间的收入数据（假设有可用的接口）
    # 这里示例计算不同现金流量之间的比例和结构
    
    # 添加现金流量净额
    analysis['cashflow_net_amount'] = {
        'operating_cashflow': float(data.n_cashflow_act) if data.n_cashflow_act else 0,
        'investing_cashflow': float(data.n_cashflow_inv_act) if data.n_cashflow_inv_act else 0,
        'financing_cashflow': float(data.n_cash_flows_fnc_act) if data.n_cash_flows_fnc_act else 0,
        'net_increase_in_cash': float(data.n_incr_cash_cash_equ) if data.n_incr_cash_cash_equ else 0
    }
    
    # 现金流入构成分析
    total_operating_inflow = float(data.c_inf_fr_operate_a) if data.c_inf_fr_operate_a else 0
    total_investing_inflow = float(data.stot_inflows_inv_act) if data.stot_inflows_inv_act else 0
    total_financing_inflow = float(data.stot_cash_in_fnc_act) if data.stot_cash_in_fnc_act else 0
    
    total_inflow = total_operating_inflow + total_investing_inflow + total_financing_inflow
    
    if total_inflow > 0:
        analysis['cashflow_inflow_structure'] = {
            'operating_inflow_ratio': total_operating_inflow / total_inflow * 100,
            'investing_inflow_ratio': total_investing_inflow / total_inflow * 100,
            'financing_inflow_ratio': total_financing_inflow / total_inflow * 100
        }
    
    # 现金流出构成分析
    total_operating_outflow = float(data.st_cash_out_act) if data.st_cash_out_act else 0
    total_investing_outflow = float(data.stot_out_inv_act) if data.stot_out_inv_act else 0
    total_financing_outflow = float(data.stot_cashout_fnc_act) if data.stot_cashout_fnc_act else 0
    
    total_outflow = total_operating_outflow + total_investing_outflow + total_financing_outflow
    
    if total_outflow > 0:
        analysis['cashflow_outflow_structure'] = {
            'operating_outflow_ratio': total_operating_outflow / total_outflow * 100,
            'investing_outflow_ratio': total_investing_outflow / total_outflow * 100,
            'financing_outflow_ratio': total_financing_outflow / total_outflow * 100
        }
    
    # 经营活动现金流量结构
    if total_operating_inflow > 0:
        analysis['operating_cashflow_inflow_structure'] = {
            'sales_goods_ratio': float(data.c_fr_sale_sg) / total_operating_inflow * 100 if data.c_fr_sale_sg else 0,
            'tax_refund_ratio': float(data.recp_tax_rends) / total_operating_inflow * 100 if data.recp_tax_rends else 0,
            'other_operating_ratio': float(data.c_fr_oth_operate_a) / total_operating_inflow * 100 if data.c_fr_oth_operate_a else 0
        }
    
    if total_operating_outflow > 0:
        analysis['operating_cashflow_outflow_structure'] = {
            'goods_purchase_ratio': float(data.c_paid_goods_s) / total_operating_outflow * 100 if data.c_paid_goods_s else 0,
            'employee_payment_ratio': float(data.c_paid_to_for_empl) / total_operating_outflow * 100 if data.c_paid_to_for_empl else 0,
            'tax_payment_ratio': float(data.c_paid_for_taxes) / total_operating_outflow * 100 if data.c_paid_for_taxes else 0,
            'other_operating_payment_ratio': float(data.oth_cash_pay_oper_act) / total_operating_outflow * 100 if data.oth_cash_pay_oper_act else 0
        }
    
    # 投资活动现金流量结构
    if total_investing_inflow > 0:
        analysis['investing_cashflow_inflow_structure'] = {
            'investment_recovery_ratio': float(data.c_disp_withdrwl_invest) / total_investing_inflow * 100 if data.c_disp_withdrwl_invest else 0,
            'investment_income_ratio': float(data.c_recp_return_invest) / total_investing_inflow * 100 if data.c_recp_return_invest else 0,
            'fixed_assets_disposal_ratio': float(data.n_recp_disp_fiolta) / total_investing_inflow * 100 if data.n_recp_disp_fiolta else 0,
            'subsidiary_disposal_ratio': float(data.n_recp_disp_sobu) / total_investing_inflow * 100 if data.n_recp_disp_sobu else 0,
            'other_investing_ratio': float(data.oth_recp_ral_inv_act) / total_investing_inflow * 100 if data.oth_recp_ral_inv_act else 0
        }
    
    if total_investing_outflow > 0:
        analysis['investing_cashflow_outflow_structure'] = {
            'fixed_assets_purchase_ratio': float(data.c_pay_acq_const_fiolta) / total_investing_outflow * 100 if data.c_pay_acq_const_fiolta else 0,
            'investment_payment_ratio': float(data.c_paid_invest) / total_investing_outflow * 100 if data.c_paid_invest else 0,
            'subsidiary_acquisition_ratio': float(data.n_disp_subs_oth_biz) / total_investing_outflow * 100 if data.n_disp_subs_oth_biz else 0,
            'other_investing_payment_ratio': float(data.oth_pay_ral_inv_act) / total_investing_outflow * 100 if data.oth_pay_ral_inv_act else 0
        }
    
    # 筹资活动现金流量结构
    if total_financing_inflow > 0:
        analysis['financing_cashflow_inflow_structure'] = {
            'borrowing_ratio': float(data.c_recp_borrow) / total_financing_inflow * 100 if data.c_recp_borrow else 0,
            'bond_issuance_ratio': float(data.proc_issue_bonds) / total_financing_inflow * 100 if data.proc_issue_bonds else 0,
            'capital_contribution_ratio': float(data.c_recp_cap_contrib) / total_financing_inflow * 100 if data.c_recp_cap_contrib else 0,
            'other_financing_ratio': float(data.oth_cash_recp_ral_fnc_act) / total_financing_inflow * 100 if data.oth_cash_recp_ral_fnc_act else 0
        }
    
    if total_financing_outflow > 0:
        analysis['financing_cashflow_outflow_structure'] = {
            'debt_repayment_ratio': float(data.c_prepay_amt_borr) / total_financing_outflow * 100 if data.c_prepay_amt_borr else 0,
            'dividend_interest_ratio': float(data.c_pay_dist_dpcp_int_exp) / total_financing_outflow * 100 if data.c_pay_dist_dpcp_int_exp else 0,
            'other_financing_payment_ratio': float(data.oth_cashpay_ral_fnc_act) / total_financing_outflow * 100 if data.oth_cashpay_ral_fnc_act else 0
        }
    
    # 计算现金流量比率指标
    # 这些指标需要结合资产负债表、利润表数据计算
    # 这里列出一些常见的现金流量比率指标的计算公式
    
    # 计算经营活动现金流量与净利润的比率
    if data.net_profit and data.net_profit != 0:
        analysis['cashflow_ratios'] = {
            'operating_cashflow_to_net_profit': float(data.n_cashflow_act) / float(data.net_profit) if data.n_cashflow_act else 0
        }
    
    # 整体现金流量质量分析
    # 计算经营、投资、筹资活动现金流量净额之和应等于现金净增加额
    # 检查是否存在较大差异
    calculated_cash_increase = float(data.n_cashflow_act or 0) + float(data.n_cashflow_inv_act or 0) + float(data.n_cash_flows_fnc_act or 0) + float(data.eff_fx_flu_cash or 0)
    actual_cash_increase = float(data.n_incr_cash_cash_equ or 0)
    
    if actual_cash_increase != 0:
        difference_ratio = abs(calculated_cash_increase - actual_cash_increase) / abs(actual_cash_increase) * 100
        analysis['cash_increase_check'] = {
            'calculated_value': calculated_cash_increase,
            'reported_value': actual_cash_increase,
            'difference_ratio': difference_ratio,
            'is_consistent': difference_ratio < 1  # 1% 以内的差异视为正常
        }
    
    return analysis


# 计算和分析现金流量趋势
async def analyze_cashflow_trend(db, ts_code: str, report_type: str = '1', periods: int = 5):
    """
    分析公司最近几个报告期的现金流量趋势
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        report_type: 报告类型，默认为1（年报）
        periods: 分析的报告期数量
        
    返回:
        List[Dict]: 包含原始数据和同比变化的列表
    """
    # 获取公司的现金流量数据，按报告期降序排序
    cashflow_data = await query_cashflow_data(
        db,
        filters={'ts_code': ts_code, 'report_type': report_type},
        order_by=['-end_date'],
        limit=periods * 2  # 获取更多数据以计算同比
    )
    
    if not cashflow_data or len(cashflow_data) < 2:
        return cashflow_data  # 数据不足，无法计算同比
    
    # 按年度分组
    year_data = {}
    for item in cashflow_data:
        if item.end_date:
            year = item.end_date.year
            if year not in year_data:
                year_data[year] = item
    
    # 计算同比变化
    result = []
    years = sorted(year_data.keys(), reverse=True)
    
    for i, year in enumerate(years):
        if i >= periods:
            break
            
        current_data = year_data[year]
        current_dict = current_data.model_dump()
        
        # 如果有上一年数据，计算同比变化
        if i < len(years) - 1:
            prev_year = years[i + 1]
            prev_data = year_data[prev_year]
            
            # 计算关键现金流指标的同比变化
            yoy_changes = {}
            for key in ['n_cashflow_act', 'n_cashflow_inv_act', 'n_cash_flows_fnc_act', 'free_cashflow', 'n_incr_cash_cash_equ']:
                curr_val = getattr(current_data, key, None)
                prev_val = getattr(prev_data, key, None)
                
                if curr_val is not None and prev_val is not None and prev_val != 0:
                    yoy_changes[f"{key}_yoy"] = float((curr_val - prev_val) / abs(prev_val) * 100)
                else:
                    yoy_changes[f"{key}_yoy"] = None
            
            current_dict.update(yoy_changes)
        
        result.append(current_dict)
    
    return result


# 对比企业自由现金流与净利润
async def compare_free_cashflow_to_profit(db, ts_code: str, start_date: str = None, end_date: str = None, 
                                        report_type: str = '1', limit: int = 10):
    """
    对比公司在各报告期的自由现金流与净利润
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        start_date: 开始日期，格式YYYYMMDD
        end_date: 结束日期，格式YYYYMMDD
        report_type: 报告类型，默认为1（年报）
        limit: 最大返回记录数
        
    返回:
        List[Dict]: 包含报告期、自由现金流、净利润及比率的列表
    """
    # 获取公司的现金流量数据
    cashflow_data = await query_cashflow_data(
        db,
        filters={
            'ts_code': ts_code,
            'end_date__ge': start_date if start_date else None,
            'end_date__le': end_date if end_date else None,
            'report_type': report_type
        },
        order_by=['-end_date'],
        limit=limit
    )
    
    if not cashflow_data:
        return []
    
    result = []
    for data in cashflow_data:
        free_cashflow = float(data.free_cashflow) if data.free_cashflow else 0
        net_profit = float(data.net_profit) if data.net_profit else 0
        
        ratio = None
        if net_profit != 0:
            ratio = free_cashflow / net_profit
        
        result.append({
            'end_date': data.end_date,
            'free_cashflow': free_cashflow,
            'net_profit': net_profit,
            'free_cashflow_to_profit_ratio': ratio,
            'is_higher_than_profit': free_cashflow > net_profit if net_profit != 0 else None
        })
    
    return result

