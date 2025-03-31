import pandas as pd
from decimal import Decimal
from typing import List, Optional, Dict, Any
from app.external.tushare_api.financial_info_api import get_balancesheet
from app.data.db_modules.stock_modules.stock_financial.balancesheet import BalancesheetData

class BalancesheetService:
    """资产负债表数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_balancesheet_data(self, ts_code: Optional[str] = None, 
                              ann_date: Optional[str] = None,
                              start_date: Optional[str] = None, 
                              end_date: Optional[str] = None,
                              period: Optional[str] = None,
                              report_type: Optional[str] = None,
                              comp_type: Optional[str] = None,
                              batch_size: int = 1000) -> int:
        """
        从Tushare获取资产负债表数据并高效导入数据库
        
        参数:
            ts_code: 股票代码
            ann_date: 公告日期（YYYYMMDD格式）
            start_date: 公告开始日期
            end_date: 公告结束日期
            period: 报告期(每个季度最后一天的日期，比如20171231表示年报，20170630半年报，20170930三季报)
            report_type: 报告类型，参考文档最下方说明
            comp_type: 公司类型（1一般工商业2银行3保险4证券）
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_balancesheet(ts_code=ts_code, ann_date=ann_date,
                            start_date=start_date, end_date=end_date, period=period,
                            report_type=report_type, comp_type=comp_type)
        
        if df_result is None or df_result.empty:
            print(f"未找到资产负债表数据: ts_code={ts_code}, period={period}, report_type={report_type}")
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
                # 将批次数据转换为BalancesheetData对象
                balancesheet_data_list = []
                for record in batch:
                    try:
                        # 处理数字字段，确保它们是Decimal类型
                        for key, value in record.items():
                            if isinstance(value, (float, int)) and key not in ['id']:
                                record[key] = Decimal(str(value))
                        
                        balancesheet_data = BalancesheetData(**record)
                        balancesheet_data_list.append(balancesheet_data)
                    except Exception as e:
                        print(f"创建BalancesheetData对象失败 {record.get('ts_code', '未知')}, {record.get('end_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if balancesheet_data_list:
                    inserted = await self.batch_upsert_balancesheet(balancesheet_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条资产负债表记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_balancesheet(self, balancesheet_list: List[BalancesheetData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            balancesheet_list: 要插入或更新的资产负债表数据列表
            
        返回:
            处理的记录数
        """
        if not balancesheet_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = balancesheet_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 优先选择update_flag为1的记录
        # 使用字典来存储记录，如果有重复键，根据update_flag决定是否替换
        unique_records = {}
        
        for balancesheet in balancesheet_list:
            # 创建唯一键
            key = (balancesheet.ts_code, str(balancesheet.end_date), str(balancesheet.report_type))
            
            # 获取update_flag，如果不存在则默认为0
            update_flag = getattr(balancesheet, 'update_flag', '0')
            
            # 如果键不存在，或者当前记录的update_flag为1且已存记录的update_flag不为1，则更新
            if key not in unique_records or (update_flag == '1' and unique_records[key][1] != '1'):
                unique_records[key] = (balancesheet, update_flag)
                print(f"保留记录: {balancesheet.ts_code}, {balancesheet.end_date}, {balancesheet.report_type}, update_flag={update_flag}")
            else:
                existing_flag = unique_records[key][1]
                print(f"跳过记录: {balancesheet.ts_code}, {balancesheet.end_date}, {balancesheet.report_type}, "
                    f"update_flag={update_flag}，已存在update_flag={existing_flag}的记录")
        
        # 提取最终的唯一记录列表
        unique_balancesheet_list = [record[0] for record in unique_records.values()]
        
        # 准备数据
        records = []
        for balancesheet in unique_balancesheet_list:
            balancesheet_dict = balancesheet.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = balancesheet_dict[col]
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
                    column_types = await self._get_column_type(conn, 'balancesheet', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_balancesheet (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_balancesheet', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'end_date', 'report_type']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO balancesheet ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_balancesheet
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


# 快捷函数，用于导入特定股票的资产负债表数据
async def import_stock_balancesheet(db, ts_code: str, batch_size: int = 1000):
    """
    导入特定股票的资产负债表数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = BalancesheetService(db)
    count = await service.import_balancesheet_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条股票 {ts_code} 的资产负债表记录")
    return count


# 快捷函数，用于导入特定公告日期的资产负债表数据
async def import_ann_date_balancesheet(db, ann_date: str, batch_size: int = 1000):
    """
    导入特定公告日期的资产负债表数据
    
    参数:
        db: 数据库连接对象
        ann_date: 公告日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = BalancesheetService(db)
    count = await service.import_balancesheet_data(ann_date=ann_date, batch_size=batch_size)
    print(f"成功导入 {count} 条公告日期为 {ann_date} 的资产负债表记录")
    return count


# 快捷函数，用于导入特定报告期的资产负债表数据
async def import_period_balancesheet(db, period: str, batch_size: int = 1000):
    """
    导入特定报告期的资产负债表数据
    
    参数:
        db: 数据库连接对象
        period: 报告期(每个季度最后一天的日期，比如20171231表示年报，20170630半年报，20170930三季报)
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = BalancesheetService(db)
    count = await service.import_balancesheet_data(period=period, batch_size=batch_size)
    
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
    print(f"成功导入 {count} 条报告期为 {period_info} 的资产负债表记录")
    return count


# 快捷函数，用于导入特定公告日期范围的资产负债表数据
async def import_ann_date_range_balancesheet(db, start_date: str, end_date: str, batch_size: int = 1000):
    """
    导入特定公告日期范围的资产负债表数据
    
    参数:
        db: 数据库连接对象
        start_date: 公告开始日期（YYYYMMDD格式）
        end_date: 公告结束日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = BalancesheetService(db)
    count = await service.import_balancesheet_data(start_date=start_date, end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条公告日期范围为 {start_date} 至 {end_date} 的资产负债表记录")
    return count


# 快捷函数，用于导入特定类型公司的资产负债表数据
async def import_company_type_balancesheet(db, comp_type: str, batch_size: int = 1000):
    """
    导入特定类型公司的资产负债表数据
    
    参数:
        db: 数据库连接对象
        comp_type: 公司类型（1一般工商业2银行3保险4证券）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = BalancesheetService(db)
    count = await service.import_balancesheet_data(comp_type=comp_type, batch_size=batch_size)
    
    comp_type_desc = {
        '1': '一般工商业',
        '2': '银行',
        '3': '保险',
        '4': '证券'
    }.get(comp_type, comp_type)
    
    print(f"成功导入 {count} 条 {comp_type_desc} 类型公司的资产负债表记录")
    return count


# 快捷函数，用于导入特定报告类型的资产负债表数据
async def import_report_type_balancesheet(db, report_type: str, batch_size: int = 1000):
    """
    导入特定报告类型的资产负债表数据
    
    参数:
        db: 数据库连接对象
        report_type: 报告类型
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = BalancesheetService(db)
    count = await service.import_balancesheet_data(report_type=report_type, batch_size=batch_size)
    
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
    
    print(f"成功导入 {count} 条报告类型为 {report_type_desc} 的资产负债表记录")
    return count


# 综合导入函数，支持多种参数组合
async def import_balancesheet_with_params(db, **kwargs):
    """
    根据提供的参数导入资产负债表数据
    
    参数:
        db: 数据库连接对象
        **kwargs: 可包含 ts_code, ann_date, start_date, end_date, period, report_type, comp_type, batch_size 等参数
        
    返回:
        导入的记录数
    """
    service = BalancesheetService(db)
    batch_size = kwargs.pop('batch_size', 1000)  # 提取并移除batch_size参数
    
    # 构建参数描述
    param_desc = []
    for key, value in kwargs.items():
        if value:
            param_desc.append(f"{key}={value}")
    
    params_info = ", ".join(param_desc) if param_desc else "所有可用参数"
    
    # 导入数据
    count = await service.import_balancesheet_data(batch_size=batch_size, **kwargs)
    print(f"成功导入 {count} 条资产负债表记录 ({params_info})")
    return count


# 导入所有资产负债表数据
async def import_all_balancesheet(db, batch_size: int = 1000):
    """
    导入所有可获取的资产负债表数据
    
    注意: 这可能会请求大量数据，请确保有足够的网络带宽和系统资源。
    根据数据量大小，此操作可能需要较长时间完成。
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小，默认1000条
        
    返回:
        导入的记录总数
    """
    service = BalancesheetService(db)
    
    print("开始导入所有资产负债表数据，此操作可能需要较长时间...")
    count = await service.import_balancesheet_data(batch_size=batch_size)
    
    print(f"成功导入所有资产负债表数据，共 {count} 条记录")
    return count


# 动态查询资产负债表数据
async def query_balancesheet_data(db, 
                          filters: Optional[Dict[str, Any]] = None, 
                          order_by: Optional[List[str]] = None,
                          limit: Optional[int] = None,
                          offset: Optional[int] = None):
    """
    动态查询资产负债表数据，支持任意字段过滤和自定义排序
    
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
        List[BalancesheetData]: 符合条件的资产负债表数据列表
    
    示例:
        # 查询某股票最近两年的年报数据，按报告期降序排列
        data = await query_balancesheet_data(
            db,
            filters={
                'ts_code': '000001.SZ',
                'end_date__ge': '20220101',
                'report_type': '1'  # 年报
            },
            order_by=['-end_date']
        )
        
        # 分页查询某行业所有资产总额超过一定值的公司
        data = await query_balancesheet_data(
            db,
            filters={'total_assets__gt': 100000000000},
            order_by=['-total_assets', 'ts_code'],
            limit=20,
            offset=0
        )
    """
    from app.db.crud.stock_crud.stock_financial.balancesheet_crud import BalancesheetCRUD
    
    crud = BalancesheetCRUD(db)
    results = await crud.get_balancesheet(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 查询特定公司多个报告期的资产负债表数据
async def get_company_balancesheet_trend(db, ts_code: str, start_date: str = None, end_date: str = None, 
                                   report_type: str = None, limit: int = 20):
    """
    查询特定公司在时间段内的资产负债表趋势数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        start_date: 开始日期，格式YYYYMMDD
        end_date: 结束日期，格式YYYYMMDD
        report_type: 报告类型（如年报、季报等）
        limit: 最大返回记录数
        
    返回:
        List[BalancesheetData]: 该公司的资产负债表趋势数据，按报告期降序排列
    """
    filters = {'ts_code': ts_code}
    
    if start_date:
        filters['end_date__ge'] = start_date
    
    if end_date:
        filters['end_date__le'] = end_date
    
    if report_type:
        filters['report_type'] = report_type
    
    return await query_balancesheet_data(
        db,
        filters=filters,
        order_by=['-end_date'],
        limit=limit
    )


# 对比多家公司同期资产负债表数据
async def compare_companies_balancesheet(db, ts_codes: List[str], end_date: str, report_type: str = '1'):
    """
    对比多家公司在同一报告期的资产负债表数据
    
    参数:
        db: 数据库连接对象
        ts_codes: 股票代码列表
        end_date: 报告期，格式YYYYMMDD
        report_type: 报告类型，默认为1（年报）
        
    返回:
        List[BalancesheetData]: 多家公司在指定报告期的资产负债表数据
    """
    return await query_balancesheet_data(
        db,
        filters={
            'ts_code__in': ts_codes,
            'end_date': end_date,
            'report_type': report_type
        }
    )


# 查询资产规模最大的公司
async def get_top_asset_companies(db, industry_codes: List[str] = None, 
                                  end_date: str = None, report_type: str = '1',
                                  top_n: int = 10):
    """
    查询特定行业或全市场资产规模最大的公司
    
    参数:
        db: 数据库连接对象
        industry_codes: 行业代码列表，为None时查询全市场
        end_date: 报告期，格式YYYYMMDD，为None时查询最新报告期
        report_type: 报告类型，默认为1（年报）
        top_n: 返回前N家公司
        
    返回:
        List[BalancesheetData]: 资产规模最大的公司数据
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
    
    return await query_balancesheet_data(
        db,
        filters=filters,
        order_by=['-total_assets'],
        limit=top_n
    )


# 分析公司资产负债结构
async def analyze_asset_liability_structure(db, ts_code: str, end_date: str, report_type: str = '1'):
    """
    分析公司在特定报告期的资产负债结构
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        end_date: 报告期，格式YYYYMMDD
        report_type: 报告类型，默认为1（年报）
        
    返回:
        Dict: 包含资产负债分析的字典
    """
    # 查询指定公司和报告期的资产负债表
    balancesheet_data = await query_balancesheet_data(
        db,
        filters={
            'ts_code': ts_code,
            'end_date': end_date,
            'report_type': report_type
        }
    )
    
    if not balancesheet_data or len(balancesheet_data) == 0:
        return None
    
    data = balancesheet_data[0]
    
    # 计算资产负债结构比例
    analysis = {}
    
    # 确保总资产不为零，避免除数为零的错误
    if data.total_assets and data.total_assets > 0:
        # 资产结构分析
        analysis['asset_structure'] = {
            'current_assets_ratio': float(data.total_cur_assets / data.total_assets * 100) if data.total_cur_assets else None,
            'non_current_assets_ratio': float(data.total_nca / data.total_assets * 100) if data.total_nca else None,
            'cash_ratio': float(data.money_cap / data.total_assets * 100) if data.money_cap else None,
            'inventory_ratio': float(data.inventories / data.total_assets * 100) if data.inventories else None,
            'accounts_receivable_ratio': float(data.accounts_receiv / data.total_assets * 100) if data.accounts_receiv else None,
            'fixed_assets_ratio': float(data.fix_assets / data.total_assets * 100) if data.fix_assets else None,
            'intangible_assets_ratio': float(data.intan_assets / data.total_assets * 100) if data.intan_assets else None
        }
    
    # 确保总负债不为零，避免除数为零的错误
    if data.total_liab and data.total_liab > 0:
        # 负债结构分析
        analysis['liability_structure'] = {
            'current_liab_ratio': float(data.total_cur_liab / data.total_liab * 100) if data.total_cur_liab else None,
            'non_current_liab_ratio': float(data.total_ncl / data.total_liab * 100) if data.total_ncl else None,
            'short_term_loan_ratio': float(data.st_borr / data.total_liab * 100) if data.st_borr else None,
            'long_term_loan_ratio': float(data.lt_borr / data.total_liab * 100) if data.lt_borr else None,
            'accounts_payable_ratio': float(data.acct_payable / data.total_liab * 100) if data.acct_payable else None
        }
    
    # 财务指标分析
    analysis['financial_indicators'] = {
        'assets_liab_ratio': float(data.total_liab / data.total_assets * 100) if (data.total_liab and data.total_assets) else None,
        'current_ratio': float(data.total_cur_assets / data.total_cur_liab) if (data.total_cur_assets and data.total_cur_liab) else None,
        'quick_ratio': float((data.total_cur_assets - data.inventories) / data.total_cur_liab) 
                       if (data.total_cur_assets and data.total_cur_liab and data.inventories) else None,
        'equity_ratio': float(data.total_hldr_eqy_inc_min_int / data.total_assets * 100) 
                       if (data.total_hldr_eqy_inc_min_int and data.total_assets) else None
    }
    
    # 股东权益结构
    if data.total_hldr_eqy_inc_min_int and data.total_hldr_eqy_inc_min_int > 0:
        analysis['equity_structure'] = {
            'share_capital_ratio': float(data.total_share / data.total_hldr_eqy_inc_min_int * 100) 
                                  if data.total_share else None,
            'capital_reserve_ratio': float(data.cap_rese / data.total_hldr_eqy_inc_min_int * 100) 
                                   if data.cap_rese else None,
            'undistributed_profit_ratio': float(data.undistr_porfit / data.total_hldr_eqy_inc_min_int * 100) 
                                       if data.undistr_porfit else None,
            'surplus_reserve_ratio': float(data.surplus_rese / data.total_hldr_eqy_inc_min_int * 100) 
                                  if data.surplus_rese else None
        }
    
    return analysis