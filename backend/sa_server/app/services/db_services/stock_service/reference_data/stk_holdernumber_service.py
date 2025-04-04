import pandas as pd
from typing import List, Optional, Dict, Any
from app.external.tushare_api.stock.reference_data_api import get_stk_holdernumber
from app.data.db_modules.stock_modules.reference_data.stk_holdernumber import StkHoldernumberData

class StkHoldernumberService:
    """股东户数数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_stk_holdernumber_data(self, ts_code: Optional[str] = None, 
                                        ann_date: Optional[str] = None,
                                        enddate: Optional[str] = None,
                                        start_date: Optional[str] = None, 
                                        end_date: Optional[str] = None,
                                        batch_size: int = 1000) -> int:
        """
        从Tushare获取股东户数数据并高效导入数据库
        
        参数:
            ts_code: 股票代码
            ann_date: 公告日期（YYYYMMDD格式）
            enddate: 截止日期（YYYYMMDD格式）
            start_date: 开始日期，格式YYYYMMDD
            end_date: 结束日期，格式YYYYMMDD
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_stk_holdernumber(ts_code=ts_code, ann_date=ann_date, enddate=enddate,
                                      start_date=start_date, end_date=end_date)
        
        if df_result is None or df_result.empty:
            print(f"未找到股东户数数据: ts_code={ts_code}, ann_date={ann_date}, enddate={enddate}")
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
                # 将批次数据转换为StkHoldernumberData对象
                holder_data_list = []
                for record in batch:
                    try:
                        holder_data = StkHoldernumberData(**record)
                        holder_data_list.append(holder_data)
                    except Exception as e:
                        print(f"创建StkHoldernumberData对象失败 {record.get('ts_code', '未知')}, {record.get('end_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if holder_data_list:
                    inserted = await self.batch_upsert_stk_holdernumber(holder_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条股东户数记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_stk_holdernumber(self, holders_list: List[StkHoldernumberData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            holders_list: 要插入或更新的股东户数数据列表
            
        返回:
            处理的记录数
        """
        if not holders_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = holders_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 使用字典来存储记录，如果有重复键，保留最新记录
        unique_records = {}
        
        for holder in holders_list:
            # 创建唯一键
            key = (holder.ts_code, str(holder.end_date))
            unique_records[key] = holder
        
        # 提取最终的唯一记录列表
        unique_holders_list = list(unique_records.values())
        
        # 准备数据
        records = []
        for holder in unique_holders_list:
            holder_dict = holder.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = holder_dict[col]
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
                    column_types = await self._get_column_type(conn, 'stk_holdernumber', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_stk_holdernumber (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_stk_holdernumber', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'end_date']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO stk_holdernumber ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_stk_holdernumber
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


# 快捷函数，用于导入特定股票的股东户数数据
async def import_stock_stk_holdernumber(db, ts_code: str, batch_size: int = 1000):
    """
    导入特定股票的股东户数数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StkHoldernumberService(db)
    count = await service.import_stk_holdernumber_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条股票 {ts_code} 的股东户数记录")
    return count


# 快捷函数，用于导入特定公告日期的股东户数数据
async def import_ann_date_stk_holdernumber(db, ann_date: str, batch_size: int = 1000):
    """
    导入特定公告日期的股东户数数据
    
    参数:
        db: 数据库连接对象
        ann_date: 公告日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StkHoldernumberService(db)
    count = await service.import_stk_holdernumber_data(ann_date=ann_date, batch_size=batch_size)
    print(f"成功导入 {count} 条公告日期为 {ann_date} 的股东户数记录")
    return count


# 快捷函数，用于导入特定截止日期的股东户数数据
async def import_enddate_stk_holdernumber(db, enddate: str, batch_size: int = 1000):
    """
    导入特定截止日期的股东户数数据
    
    参数:
        db: "数据库连接对象
        enddate: 截止日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StkHoldernumberService(db)
    count = await service.import_stk_holdernumber_data(enddate=enddate, batch_size=batch_size)
    print(f"成功导入 {count} 条截止日期为 {enddate} 的股东户数记录")
    return count


# 快捷函数，用于导入特定日期范围的股东户数数据
async def import_date_range_stk_holdernumber(db, start_date: str, end_date: str, batch_size: int = 1000):
    """
    导入特定日期范围的股东户数数据
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期（YYYYMMDD格式）
        end_date: 结束日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StkHoldernumberService(db)
    count = await service.import_stk_holdernumber_data(start_date=start_date, end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条日期范围为 {start_date} 至 {end_date} 的股东户数记录")
    return count


# 综合导入函数，支持多种参数组合
async def import_stk_holdernumber_with_params(db, **kwargs):
    """
    根据提供的参数导入股东户数数据
    
    参数:
        db: 数据库连接对象
        **kwargs: 可包含 ts_code, ann_date, enddate, start_date, end_date, batch_size 等参数
        
    返回:
        导入的记录数
    """
    service = StkHoldernumberService(db)
    batch_size = kwargs.pop('batch_size', 1000)  # 提取并移除batch_size参数
    
    # 构建参数描述
    param_desc = []
    for key, value in kwargs.items():
        if value:
            param_desc.append(f"{key}={value}")
    
    params_info = ", ".join(param_desc) if param_desc else "所有可用参数"
    
    # 导入数据
    count = await service.import_stk_holdernumber_data(batch_size=batch_size, **kwargs)
    print(f"成功导入 {count} 条股东户数记录 ({params_info})")
    return count


# 导入所有股东户数数据
async def import_all_stk_holdernumber(db, batch_size: int = 1000):
    """
    导入所有可获取的股东户数数据
    
    注意: 这可能会请求大量数据，请确保有足够的网络带宽和系统资源。
    根据数据量大小，此操作可能需要较长时间完成。
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小，默认1000条
        
    返回:
        导入的记录总数
    """
    service = StkHoldernumberService(db)
    
    print("开始导入所有股东户数数据，此操作可能需要较长时间...")
    count = await service.import_stk_holdernumber_data(batch_size=batch_size)
    
    print(f"成功导入所有股东户数数据，共 {count} 条记录")
    return count


# 动态查询股东户数数据
async def query_stk_holdernumber_data(db, 
                                   filters: Optional[Dict[str, Any]] = None, 
                                   order_by: Optional[List[str]] = None,
                                   limit: Optional[int] = None,
                                   offset: Optional[int] = None):
    """
    动态查询股东户数数据，支持任意字段过滤和自定义排序
    
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
                 例如: {'ts_code__like': '600%', 'holder_num__gt': 10000}
        order_by: 排序字段列表，字段前加"-"表示降序，例如['-end_date']
        limit: 最大返回记录数
        offset: 跳过前面的记录数（用于分页）
        
    返回:
        List[StkHoldernumberData]: 符合条件的股东户数数据列表
    
    示例:
        # 查询某股票最近一期的股东户数
        data = await query_stk_holdernumber_data(
            db,
            filters={'ts_code': '000001.SZ'},
            order_by=['-end_date'],
            limit=1
        )
        
        # 分页查询股东户数超过50000的所有股票
        data = await query_stk_holdernumber_data(
            db,
            filters={'holder_num__gt': 50000},
            order_by=['-holder_num', 'ts_code'],
            limit=20,
            offset=0
        )
    """
    from app.db.crud.stock_crud.reference_data.stk_holdernumber_crud import StkHoldernumberCRUD
    
    crud = StkHoldernumberCRUD(db)
    results = await crud.get_stk_holdernumber(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 分析股东户数变化趋势
async def analyze_holder_number_trend(db, ts_code: str, periods: int = 8):
    """
    分析特定股票股东户数的变化趋势
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        periods: 分析的报告期数量
        
    返回:
        Dict: 包含股东户数变化趋势的分析结果
    """
    # 获取指定股票的股东户数历史数据
    data = await query_stk_holdernumber_data(
        db,
        filters={'ts_code': ts_code},
        order_by=['-end_date'],
        limit=periods
    )
    
    if not data:
        return {"error": f"未找到股票 {ts_code} 的股东户数数据"}
    
    # 按时间升序排序，以便计算变化
    data.sort(key=lambda x: x.end_date if x.end_date else "")
    
    # 提取关键数据
    trend_data = []
    prev_number = None
    
    for item in data:
        current_number = item.holder_num
        
        change = None
        change_percent = None
        
        if prev_number is not None and current_number is not None:
            change = current_number - prev_number
            if prev_number > 0:
                change_percent = round(change / prev_number * 100, 2)
        
        trend_data.append({
            "end_date": item.end_date.strftime('%Y-%m-%d') if item.end_date else None,
            "ann_date": item.ann_date.strftime('%Y-%m-%d') if item.ann_date else None,
            "holder_num": current_number,
            "change": change,
            "change_percent": change_percent
        })
        
        prev_number = current_number
    
    # 计算整体变化趋势
    if len(trend_data) >= 2 and trend_data[0]["holder_num"] is not None and trend_data[-1]["holder_num"] is not None:
        first_number = trend_data[0]["holder_num"]
        last_number = trend_data[-1]["holder_num"]
        
        total_change = last_number - first_number
        total_change_percent = round(total_change / first_number * 100, 2) if first_number > 0 else None
        
        # 判断趋势
        if total_change > 0:
            trend = "上升"
        elif total_change < 0:
            trend = "下降"
        else:
            trend = "稳定"
    else:
        total_change = None
        total_change_percent = None
        trend = "数据不足"
    
    # 整理结果
    result = {
        "ts_code": ts_code,
        "data_points": len(trend_data),
        "period_start": trend_data[0]["end_date"] if trend_data else None,
        "period_end": trend_data[-1]["end_date"] if trend_data else None,
        "first_holder_num": trend_data[0]["holder_num"] if trend_data else None,
        "last_holder_num": trend_data[-1]["holder_num"] if trend_data else None,
        "total_change": total_change,
        "total_change_percent": total_change_percent,
        "trend": trend,
        "details": trend_data
    }
    
    return result