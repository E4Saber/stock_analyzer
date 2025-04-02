import pandas as pd
from decimal import Decimal
from typing import List, Optional, Dict, Any
from app.external.tushare_api.financial_info_api import get_fina_mainbz
from app.data.db_modules.stock_modules.stock_financial.fina_mainbz import FinaMainbzData
from app.db.crud.stock_crud.stock_financial.fina_mainbz_crud import FinaMainbzCRUD

class FinaMainbzService:
    """主营业务构成数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_fina_mainbz_data(self, ts_code: Optional[str] = None, 
                                   period: Optional[str] = None, 
                                   bz_type: Optional[str] = None,
                                   start_date: Optional[str] = None, 
                                   end_date: Optional[str] = None,
                                   batch_size: int = 1000) -> int:
        """
        从Tushare获取主营业务构成数据并高效导入数据库
        
        参数:
            ts_code: 股票代码
            period: 报告期(每个季度最后一天的日期,比如20171231表示年报)
            bz_type: 类型：P按产品 D按地区 I按行业（请输入大写字母P或者D或者I）
            start_date: 报告期开始日期
            end_date: 报告期结束日期
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_fina_mainbz(ts_code=ts_code, period=period, type=bz_type,
                                  start_date=start_date, end_date=end_date)
        
        if df_result is None or df_result.empty:
            print(f"未找到主营业务构成数据: ts_code={ts_code}, period={period}, type={bz_type}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 定义必填字段及默认值
        required_fields = {
            'ts_code': '',
            'end_date': None,
            'bz_item': None
        }
        
        # 处理数据并确保所有必填字段都有值
        valid_records = []
        for record in records:
            # 确保必填字段存在且有值
            for field, default_value in required_fields.items():
                if field not in record or record[field] is None or (isinstance(record[field], str) and record[field] == ''):
                    record[field] = default_value
            
            # 如果缺少关键字段，跳过该记录
            if record['ts_code'] == '' or record['end_date'] is None or record['bz_item'] is None:
                continue
            
            # 处理日期格式，确保是YYYYMMDD格式
            if 'end_date' in record and record['end_date'] is not None:
                # 如果是pandas Timestamp对象，转换为YYYYMMDD格式字符串
                if hasattr(record['end_date'], 'strftime'):
                    record['end_date'] = record['end_date'].strftime('%Y%m%d')
                # 如果已经是字符串但带有连字符（如"2023-12-31"），转换为YYYYMMDD
                elif isinstance(record['end_date'], str) and '-' in record['end_date']:
                    date_parts = record['end_date'].split('-')
                    if len(date_parts) == 3:
                        record['end_date'] = ''.join(date_parts)
            
            # 确保type字段存在
            if 'type' not in record and bz_type:
                record['type'] = bz_type
                
            valid_records.append(record)
        
        # 分批处理
        batches = [valid_records[i:i + batch_size] for i in range(0, len(valid_records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为FinaMainbzData对象
                fina_mainbz_data_list = []
                for record in batch:
                    try:
                        # 处理数字字段，确保它们是Decimal类型
                        for key in ['bz_sales', 'bz_profit', 'bz_cost']:
                            if key in record and record[key] is not None and isinstance(record[key], (float, int)):
                                record[key] = Decimal(str(record[key]))
                        
                        fina_mainbz_data = FinaMainbzData(**record)
                        fina_mainbz_data_list.append(fina_mainbz_data)
                    except Exception as e:
                        print(f"创建FinaMainbzData对象失败 {record.get('ts_code', '未知')}, {record.get('end_date', '未知')}, {record.get('bz_item', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if fina_mainbz_data_list:
                    inserted = await self.batch_upsert_fina_mainbz(fina_mainbz_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条主营业务构成记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_fina_mainbz(self, fina_mainbz_list: List[FinaMainbzData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            fina_mainbz_list: 要插入或更新的主营业务构成数据列表
            
        返回:
            处理的记录数
        """
        if not fina_mainbz_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = fina_mainbz_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 优先选择update_flag为1的记录
        # 使用字典来存储记录，如果有重复键，根据update_flag决定是否替换
        unique_records = {}
        
        for fina_mainbz in fina_mainbz_list:
            # 创建唯一键
            key = (fina_mainbz.ts_code, str(fina_mainbz.end_date), str(fina_mainbz.bz_item))
            
            # 获取update_flag，如果不存在则默认为0
            update_flag = getattr(fina_mainbz, 'update_flag', '0')
            
            # 如果键不存在，或者当前记录的update_flag为1且已存记录的update_flag不为1，则更新
            if key not in unique_records or (update_flag == '1' and unique_records[key][1] != '1'):
                unique_records[key] = (fina_mainbz, update_flag)
                print(f"保留记录: {fina_mainbz.ts_code}, {fina_mainbz.end_date}, {fina_mainbz.bz_item}, update_flag={update_flag}")
            else:
                existing_flag = unique_records[key][1]
                print(f"跳过记录: {fina_mainbz.ts_code}, {fina_mainbz.end_date}, {fina_mainbz.bz_item}, "
                    f"update_flag={update_flag}，已存在update_flag={existing_flag}的记录")
        
        # 提取最终的唯一记录列表
        unique_fina_mainbz_list = [record[0] for record in unique_records.values()]
        
        # 准备数据
        records = []
        for fina_mainbz in unique_fina_mainbz_list:
            fina_mainbz_dict = fina_mainbz.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = fina_mainbz_dict[col]
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
                    column_types = await self._get_column_type(conn, 'fina_mainbz', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_fina_mainbz (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_fina_mainbz', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'end_date', 'bz_item']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO fina_mainbz ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_fina_mainbz
                        ON CONFLICT (ts_code, end_date, bz_item) DO UPDATE SET {update_clause}
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


# 快捷函数，用于导入特定股票的主营业务构成数据
async def import_stock_fina_mainbz(db, ts_code: str, batch_size: int = 1000):
    """
    导入特定股票的主营业务构成数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = FinaMainbzService(db)
    count = await service.import_fina_mainbz_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条股票 {ts_code} 的主营业务构成记录")
    return count


# 快捷函数，用于导入特定报告期的主营业务构成数据
async def import_period_fina_mainbz(db, period: str, batch_size: int = 1000):
    """
    导入特定报告期的主营业务构成数据
    
    参数:
        db: 数据库连接对象
        period: 报告期(每个季度最后一天的日期，比如20171231表示年报)
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = FinaMainbzService(db)
    count = await service.import_fina_mainbz_data(period=period, batch_size=batch_size)
    
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
    print(f"成功导入 {count} 条报告期为 {period_info} 的主营业务构成记录")
    return count


# 快捷函数，用于导入特定类型的主营业务构成数据
async def import_type_fina_mainbz(db, bz_type: str, ts_code: Optional[str] = None, period: Optional[str] = None, batch_size: int = 1000):
    """
    导入特定类型的主营业务构成数据
    
    参数:
        db: 数据库连接对象
        bz_type: 类型：P按产品 D按地区 I按行业
        ts_code: 股票TS代码（可选）
        period: 报告期（可选）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = FinaMainbzService(db)
    count = await service.import_fina_mainbz_data(ts_code=ts_code, period=period, bz_type=bz_type, batch_size=batch_size)
    
    type_desc = {
        'P': '按产品',
        'D': '按地区',
        'I': '按行业'
    }.get(bz_type, bz_type)
    
    print(f"成功导入 {count} 条类型为 {type_desc} 的主营业务构成记录")
    return count


# 快捷函数，用于导入特定日期范围的主营业务构成数据
async def import_date_range_fina_mainbz(db, start_date: str, end_date: str, batch_size: int = 1000):
    """
    导入特定日期范围的主营业务构成数据
    
    参数:
        db: 数据库连接对象
        start_date: 报告期开始日期（YYYYMMDD格式）
        end_date: 报告期结束日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = FinaMainbzService(db)
    count = await service.import_fina_mainbz_data(start_date=start_date, end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条报告期在 {start_date} 至 {end_date} 之间的主营业务构成记录")
    return count


# 综合导入函数，支持多种参数组合
async def import_fina_mainbz_with_params(db, **kwargs):
    """
    根据提供的参数导入主营业务构成数据
    
    参数:
        db: 数据库连接对象
        **kwargs: 可包含 ts_code, period, type, start_date, end_date, batch_size 等参数
        
    返回:
        导入的记录数
    """
    service = FinaMainbzService(db)
    batch_size = kwargs.pop('batch_size', 1000)  # 提取并移除batch_size参数
    
    # 构建参数描述
    param_desc = []
    for key, value in kwargs.items():
        if value:
            param_desc.append(f"{key}={value}")
    
    params_info = ", ".join(param_desc) if param_desc else "所有可用参数"
    
    # 如果有type参数，将其转换为bz_type
    if 'type' in kwargs:
        kwargs['bz_type'] = kwargs.pop('type')
    
    # 导入数据
    count = await service.import_fina_mainbz_data(batch_size=batch_size, **kwargs)
    print(f"成功导入 {count} 条主营业务构成记录 ({params_info})")
    return count


# 导入所有主营业务构成数据
async def import_all_fina_mainbz(db, batch_size: int = 1000):
    """
    导入所有可获取的主营业务构成数据
    
    注意: 这可能会请求大量数据，请确保有足够的网络带宽和系统资源。
    根据数据量大小，此操作可能需要较长时间完成。
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小，默认1000条
        
    返回:
        导入的记录总数
    """
    service = FinaMainbzService(db)
    
    print("开始导入所有主营业务构成数据，此操作可能需要较长时间...")
    count = await service.import_fina_mainbz_data(batch_size=batch_size)
    
    print(f"成功导入所有主营业务构成数据，共 {count} 条记录")
    return count


# 动态查询主营业务构成数据
async def query_fina_mainbz_data(db, 
                              filters: Optional[Dict[str, Any]] = None, 
                              order_by: Optional[List[str]] = None,
                              limit: Optional[int] = None,
                              offset: Optional[int] = None):
    """
    动态查询主营业务构成数据，支持任意字段过滤和自定义排序
    
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
        List[FinaMainbzData]: 符合条件的主营业务构成数据列表
    
    示例:
        # 查询某股票最近的主营业务构成记录
        data = await query_fina_mainbz_data(
            db,
            filters={'ts_code': '000001.SZ', 'type': 'P'},
            order_by=['-end_date', '-bz_sales']
        )
        
        # 查询某公司按产品分类的收入构成，按收入降序排列
        data = await query_fina_mainbz_data(
            db,
            filters={'ts_code': '000001.SZ', 'end_date': '20221231', 'type': 'P'},
            order_by=['-bz_sales']
        )
    """
    crud = FinaMainbzCRUD(db)
    results = await crud.get_fina_mainbz(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 获取公司主营业务收入构成
async def get_company_business_breakdown(db, ts_code: str, end_date: str, bz_type: Optional[str] = None):
    """
    获取公司特定报告期的主营业务收入构成
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        end_date: 报告期，格式YYYYMMDD
        bz_type: 类型：P按产品 D按地区 I按行业，不指定则返回所有类型
        
    返回:
        Dict: 包含各类型主营业务构成的数据
    """
    filters = {'ts_code': ts_code, 'end_date': end_date}
    
    if bz_type:
        filters['type'] = bz_type
    
    # 获取数据
    data = await query_fina_mainbz_data(
        db,
        filters=filters,
        order_by=['-bz_sales']
    )
    
    if not data:
        return {
            'ts_code': ts_code,
            'end_date': end_date,
            'message': '未找到主营业务构成数据'
        }
    
    # 按类型分组
    result = {
        'ts_code': ts_code,
        'end_date': end_date,
        'types': {}
    }
    
    total_sales = {}
    
    # 计算各类型的总销售额
    for item in data:
        item_type = item.type if item.type else 'unknown'
        if item_type not in total_sales:
            total_sales[item_type] = Decimal('0')
        if item.bz_sales:
            total_sales[item_type] += item.bz_sales
    
    # 按类型分组构建结果
    for item in data:
        item_type = item.type if item.type else 'unknown'
        
        if item_type not in result['types']:
            result['types'][item_type] = {
                'items': [],
                'total_sales': float(total_sales.get(item_type, 0))
            }
        
        # 计算占比
        sales_pct = 0
        if item.bz_sales and total_sales.get(item_type, 0) > 0:
            sales_pct = float(item.bz_sales / total_sales[item_type] * 100)
        
        # 计算毛利率
        gross_margin = None
        if item.bz_sales and item.bz_cost and item.bz_sales > 0:
            gross_margin = float((item.bz_sales - item.bz_cost) / item.bz_sales * 100)
        
        result['types'][item_type]['items'].append({
            'bz_item': item.bz_item,
            'bz_sales': float(item.bz_sales) if item.bz_sales else 0,
            'bz_profit': float(item.bz_profit) if item.bz_profit else 0,
            'bz_cost': float(item.bz_cost) if item.bz_cost else 0,
            'sales_pct': sales_pct,
            'gross_margin': gross_margin
        })
    
    # 添加映射名称
    type_names = {
        'P': '按产品',
        'D': '按地区',
        'I': '按行业',
        'unknown': '未知类型'
    }
    
    for type_key in result['types']:
        result['types'][type_key]['name'] = type_names.get(type_key, type_key)
    
    return result


# 分析公司主营业务收入变化趋势
async def analyze_business_revenue_trend(db, ts_code: str, bz_type: str, periods: int = 4):
    """
    分析公司主营业务收入的历年变化趋势
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        bz_type: 类型：P按产品 D按地区 I按行业
        periods: 分析的报告期数量
        
    返回:
        Dict: 主营业务收入变化趋势分析结果
    """
    # 获取公司最近几期的年报数据
    data = await query_fina_mainbz_data(
        db,
        filters={'ts_code': ts_code, 'type': bz_type},
        order_by=['-end_date', '-bz_sales']
    )
    
    if not data:
        return {
            'ts_code': ts_code,
            'type': bz_type,
            'message': '未找到主营业务构成数据'
        }
    
    # 按年度和业务项目分组
    year_items = {}
    all_items = set()
    
    for item in data:
        if not item.end_date:
            continue
            
        year = item.end_date.year
        month = item.end_date.month
        
        # 只分析年报数据
        if month != 12:
            continue
            
        if year not in year_items:
            year_items[year] = {}
            
        if item.bz_item:
            year_items[year][item.bz_item] = {
                'bz_sales': item.bz_sales,
                'bz_profit': item.bz_profit,
                'bz_cost': item.bz_cost
            }
            all_items.add(item.bz_item)
    
    # 获取最近几年的数据
    years = sorted(year_items.keys(), reverse=True)[:periods]
    
    if not years:
        return {
            'ts_code': ts_code,
            'type': bz_type,
            'message': '未找到符合条件的年报数据'
        }
    
    # 计算各业务项目的同比变化
    result = {
        'ts_code': ts_code,
        'type': bz_type,
        'type_name': {'P': '按产品', 'D': '按地区', 'I': '按行业'}.get(bz_type, bz_type),
        'years': years,
        'items': {},
        'trend_analysis': {}
    }
    
    # 填充各业务项目数据
    for item in all_items:
        result['items'][item] = []
        
        for year in years:
            year_data = year_items.get(year, {}).get(item)
            
            if year_data:
                result['items'][item].append({
                    'year': year,
                    'bz_sales': float(year_data['bz_sales']) if year_data['bz_sales'] else 0,
                    'bz_profit': float(year_data['bz_profit']) if year_data['bz_profit'] else 0,
                    'bz_cost': float(year_data['bz_cost']) if year_data['bz_cost'] else 0
                })
            else:
                result['items'][item].append({
                    'year': year,
                    'bz_sales': 0,
                    'bz_profit': 0,
                    'bz_cost': 0
                })
        
        # 计算同比变化率
        sales_changes = []
        for i in range(1, len(result['items'][item])):
            curr = result['items'][item][i-1]
            prev = result['items'][item][i]
            
            if prev['bz_sales'] > 0:
                change_pct = (curr['bz_sales'] - prev['bz_sales']) / prev['bz_sales'] * 100
                sales_changes.append(change_pct)
        
        # 计算平均同比变化率
        avg_change = sum(sales_changes) / len(sales_changes) if sales_changes else None
        
        # 判断趋势
        trend = None
        if sales_changes:
            if all(change > 0 for change in sales_changes):
                trend = '持续增长'
            elif all(change < 0 for change in sales_changes):
                trend = '持续下降'
            elif sales_changes[-1] > 0:
                trend = '最近增长'
            elif sales_changes[-1] < 0:
                trend = '最近下降'
            else:
                trend = '波动'
        
        # 添加趋势分析
        result['trend_analysis'][item] = {
            'sales_changes': [{'years': f"{years[i]}-{years[i+1]}", 'change_pct': sales_changes[i]} for i in range(len(sales_changes))],
            'avg_change_pct': avg_change,
            'trend': trend
        }
    
    return result


# 对比多家公司的业务构成
async def compare_companies_business_structure(db, ts_codes: List[str], end_date: str, bz_type: str):
    """
    对比多家公司的主营业务构成
    
    参数:
        db: 数据库连接对象
        ts_codes: 股票代码列表
        end_date: 报告期，格式YYYYMMDD
        bz_type: 类型：P按产品 D按地区 I按行业
        
    返回:
        Dict: 多家公司主营业务构成对比结果
    """
    result = {
        'end_date': end_date,
        'type': bz_type,
        'type_name': {'P': '按产品', 'D': '按地区', 'I': '按行业'}.get(bz_type, bz_type),
        'companies': {}
    }
    
    for ts_code in ts_codes:
        company_data = await get_company_business_breakdown(db, ts_code, end_date, bz_type)
        
        if company_data and 'types' in company_data and bz_type in company_data['types']:
            result['companies'][ts_code] = {
                'total_sales': company_data['types'][bz_type]['total_sales'],
                'items': company_data['types'][bz_type]['items']
            }
    
    # 若没有找到任何数据，返回错误信息
    if not result['companies']:
        return {
            'end_date': end_date,
            'type': bz_type,
            'message': '未找到符合条件的主营业务构成数据'
        }
    
    return result


# 分析公司业务多元化程度
async def analyze_business_diversification(db, ts_code: str, end_date: str, bz_type: str = 'P'):
    """
    分析公司业务多元化程度
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        end_date: 报告期，格式YYYYMMDD
        bz_type: 类型：P按产品 D按地区 I按行业，默认按产品
        
    返回:
        Dict: 业务多元化分析结果
    """
    # 获取公司业务构成数据
    data = await query_fina_mainbz_data(
        db,
        filters={'ts_code': ts_code, 'end_date': end_date, 'type': bz_type},
        order_by=['-bz_sales']
    )
    
    if not data:
        return {
            'ts_code': ts_code,
            'end_date': end_date,
            'type': bz_type,
            'message': '未找到符合条件的主营业务构成数据'
        }
    
    # 计算业务多元化指标
    total_sales = sum(item.bz_sales for item in data if item.bz_sales is not None)
    
    if total_sales <= 0:
        return {
            'ts_code': ts_code,
            'end_date': end_date,
            'type': bz_type,
            'message': '销售额数据异常，无法计算多元化指标'
        }
    
    # 准备业务项目数据
    items = []
    for item in data:
        if item.bz_sales is not None:
            sales_pct = float(item.bz_sales / total_sales * 100)
            items.append({
                'bz_item': item.bz_item,
                'bz_sales': float(item.bz_sales),
                'sales_pct': sales_pct
            })
    
    # 排序
    items.sort(key=lambda x: x['sales_pct'], reverse=True)
    
    # 计算HHI指数（赫芬达尔-赫希曼指数），用于衡量集中度
    hhi = sum((item['sales_pct'] / 100) ** 2 for item in items) * 10000
    
    # 计算基尼系数，用于衡量不均匀程度
    gini = 0
    if len(items) > 1:
        # 计算基尼系数
        items_sorted = sorted(items, key=lambda x: x['bz_sales'])
        cum_sales = 0
        cum_pct = 0
        total_cum_pct = 0
        
        for i, item in enumerate(items_sorted):
            cum_sales += item['bz_sales']
            prev_cum_pct = cum_pct
            cum_pct = cum_sales / total_sales
            if i > 0:
                total_cum_pct += (cum_pct + prev_cum_pct) / 2 * (1 / len(items))
        
        gini = 1 - 2 * total_cum_pct
    
    # 计算CR指标（前N家集中度）
    cr2 = sum(item['sales_pct'] for item in items[:2]) if len(items) >= 2 else None
    cr3 = sum(item['sales_pct'] for item in items[:3]) if len(items) >= 3 else None
    cr4 = sum(item['sales_pct'] for item in items[:4]) if len(items) >= 4 else None
    
    # 业务项目数量
    item_count = len(items)
    
    # 多元化评估
    diversification_level = None
    if hhi >= 2500:
        diversification_level = '高度集中'
    elif hhi >= 1500:
        diversification_level = '中度集中'
    elif hhi >= 1000:
        diversification_level = '低度集中'
    else:
        diversification_level = '高度分散'
    
    return {
        'ts_code': ts_code,
        'end_date': end_date,
        'type': bz_type,
        'type_name': {'P': '按产品', 'D': '按地区', 'I': '按行业'}.get(bz_type, bz_type),
        'item_count': item_count,
        'total_sales': float(total_sales),
        'items': items,
        'metrics': {
            'hhi': hhi,
            'gini': gini,
            'cr2': cr2,
            'cr3': cr3,
            'cr4': cr4
        },
        'diversification_level': diversification_level
    }