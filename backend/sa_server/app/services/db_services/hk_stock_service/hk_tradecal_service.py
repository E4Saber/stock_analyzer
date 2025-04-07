import pandas as pd
from typing import List, Optional, Dict, Any
from app.external.tushare_api.hk_stock_api import get_hk_tradecal
from app.data.db_modules.hk_stock_modules.hk_tradecal import HkTradecalData

class HkTradecalService:
    """香港交易日历数据导入服务，实现高效批量导入和数据管理"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_hk_tradecal_data(self, 
                                    start_date: Optional[str] = None, 
                                    end_date: Optional[str] = None,
                                    is_open: Optional[str] = None,
                                    batch_size: int = 1000) -> int:
        """
        从Tushare获取香港交易日历并高效导入数据库
        
        参数:
            start_date: 开始日期 (YYYYMMDD格式)
            end_date: 结束日期 (YYYYMMDD格式)
            is_open: 是否交易 '0'休市 '1'交易
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 构建参数说明用于日志
        params = []
        if start_date:
            params.append(f"start_date={start_date}")
        if end_date:
            params.append(f"end_date={end_date}")
        if is_open:
            params.append(f"is_open={is_open}")
        
        param_desc = ", ".join(params) if params else "所有"
        print(f"正在获取香港交易日历: {param_desc}")
        
        # 从Tushare获取数据
        try:
            df_result = get_hk_tradecal(start_date=start_date, end_date=end_date, is_open=is_open)
            
            if df_result is None or df_result.empty:
                print(f"未找到香港交易日历: {param_desc}")
                return 0
                
            print(f"获取到 {len(df_result)} 条香港交易日历")
        except Exception as e:
            print(f"获取香港交易日历失败: {str(e)}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 数据预处理和验证
        valid_records = await self._preprocess_records(records)
        
        if not valid_records:
            print("没有有效的香港交易日历记录可导入")
            return 0
            
        # 分批处理
        batches = [valid_records[i:i + batch_size] for i in range(0, len(valid_records), batch_size)]
        total_count = 0
        
        for batch_idx, batch in enumerate(batches):
            try:
                # 将批次数据转换为HkTradecalData对象
                tradecal_data_list = []
                for record in batch:
                    try:
                        # 为了确保数据类型正确，显式处理数值字段
                        if 'is_open' in record and record['is_open'] is not None:
                            if isinstance(record['is_open'], str) and record['is_open'].strip() == '':
                                record['is_open'] = None
                            elif record['is_open'] is not None:
                                try:
                                    record['is_open'] = int(record['is_open'])
                                except (ValueError, TypeError):
                                    record['is_open'] = None
                        
                        tradecal_data = HkTradecalData(**record)
                        tradecal_data_list.append(tradecal_data)
                    except Exception as e:
                        print(f"创建HkTradecalData对象失败 {record.get('cal_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if tradecal_data_list:
                    inserted = await self.batch_upsert_hk_tradecal(tradecal_data_list)
                    total_count += inserted
                    print(f"批次 {batch_idx + 1}/{len(batches)} 导入成功: {inserted} 条香港交易日历")
            except Exception as e:
                print(f"批次 {batch_idx + 1}/{len(batches)} 导入失败: {str(e)}")
        
        print(f"总共成功导入 {total_count} 条香港交易日历")
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
            'cal_date': None,
            'is_open': None,
        }
        
        valid_records = []
        invalid_count = 0
        
        for record in records:
            # 确保必填字段存在且有值
            for field, default_value in required_fields.items():
                if field not in record or record[field] is None or (isinstance(record[field], str) and record[field].strip() == ''):
                    record[field] = default_value
            
            # 如果缺少关键字段，跳过该记录
            if record['cal_date'] is None or record['is_open'] is None:
                invalid_count += 1
                continue
            
            # 处理日期格式，确保是YYYYMMDD格式
            for date_field in ['cal_date', 'pretrade_date']:
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
        
        if invalid_count > 0:
            print(f"警告: 跳过了 {invalid_count} 条无效记录")
            
        return valid_records
    
    async def batch_upsert_hk_tradecal(self, tradecal_list: List[HkTradecalData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            tradecal_list: 要插入或更新的香港交易日历数据列表
            
        返回:
            处理的记录数
        """
        if not tradecal_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = tradecal_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 使用字典来存储记录，如果有重复键，保留最新记录
        unique_records = {}
        
        for tradecal in tradecal_list:
            # 创建唯一键 (cal_date)
            key = str(tradecal.cal_date)
            unique_records[key] = tradecal
        
        # 提取最终的唯一记录列表
        unique_tradecal_list = list(unique_records.values())
        
        # 准备数据
        records = []
        for tradecal in unique_tradecal_list:
            tradecal_dict = tradecal.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = tradecal_dict[col]
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
                    column_types = await self._get_column_type(conn, 'hk_tradecal', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_hk_tradecal (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_hk_tradecal', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col != 'cal_date']
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO hk_tradecal ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_hk_tradecal
                        ON CONFLICT (cal_date) DO UPDATE SET {update_clause}
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


# 快捷函数，用于导入指定日期范围的香港交易日历
async def import_hk_tradecal_date_range(db, start_date: str, end_date: str, batch_size: int = 1000) -> int:
    """
    导入指定日期范围的香港交易日历
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期 (YYYYMMDD格式)
        end_date: 结束日期 (YYYYMMDD格式)
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = HkTradecalService(db)
    count = await service.import_hk_tradecal_data(
        start_date=start_date, 
        end_date=end_date, 
        batch_size=batch_size
    )
    print(f"成功导入 {count} 条从 {start_date} 到 {end_date} 的香港交易日历")
    return count


# 快捷函数，用于导入交易日或非交易日香港交易日历
async def import_hk_tradecal_by_status(db, is_open: str, start_date: Optional[str] = None, end_date: Optional[str] = None, batch_size: int = 1000) -> int:
    """
    导入指定交易状态的香港交易日历
    
    参数:
        db: 数据库连接对象
        is_open: 是否交易 '0'休市 '1'交易
        start_date: 开始日期 (YYYYMMDD格式，可选)
        end_date: 结束日期 (YYYYMMDD格式，可选)
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = HkTradecalService(db)
    count = await service.import_hk_tradecal_data(
        start_date=start_date,
        end_date=end_date,
        is_open=is_open, 
        batch_size=batch_size
    )
    status_text = "交易日" if is_open == "1" else "休市日"
    date_range = ""
    if start_date and end_date:
        date_range = f"从 {start_date} 到 {end_date} 的"
    elif start_date:
        date_range = f"从 {start_date} 开始的"
    elif end_date:
        date_range = f"截止到 {end_date} 的"
    
    print(f"成功导入 {count} 条{date_range}香港{status_text}")
    return count


# 快捷函数，用于导入当年香港交易日历
async def import_current_year_hk_tradecal(db, batch_size: int = 1000) -> int:
    """
    导入当年的香港交易日历
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    import datetime
    
    current_year = datetime.datetime.now().year
    start_date = f"{current_year}0101"
    end_date = f"{current_year}1231"
    
    service = HkTradecalService(db)
    count = await service.import_hk_tradecal_data(
        start_date=start_date,
        end_date=end_date,
        batch_size=batch_size
    )
    print(f"成功导入 {count} 条 {current_year} 年的香港交易日历")
    return count


# 从数据库中查询香港交易日历
async def query_hk_tradecal_data(db, 
                               filters: Optional[Dict[str, Any]] = None, 
                               order_by: Optional[List[str]] = None,
                               limit: Optional[int] = None,
                               offset: Optional[int] = None) -> List[HkTradecalData]:
    """
    动态查询香港交易日历，支持任意字段过滤和自定义排序
    
    参数:
        db: 数据库连接对象
        filters: 过滤条件字典，支持操作符后缀
        order_by: 排序字段列表，字段前加"-"表示降序
        limit: 最大返回记录数
        offset: 跳过前面的记录数（用于分页）
        
    返回:
        List[HkTradecalData]: 符合条件的香港交易日历列表
    
    示例:
        # 查询2023年香港交易日
        data = await query_hk_tradecal_data(
            db,
            filters={'cal_date__ge': '20230101', 'cal_date__le': '20231231', 'is_open': 1},
            order_by=['cal_date']
        )
    """
    from app.db.crud.hk_stock_crud.hk_tradecal_crud import HkTradecalCRUD
    
    crud = HkTradecalCRUD(db)
    results = await crud.get_hk_tradecal(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 获取最近的交易日
async def get_latest_trade_day(db, reference_date: Optional[str] = None) -> Optional[str]:
    """
    获取参考日期前的最近交易日（包括当天，如果是交易日）
    
    参数:
        db: 数据库连接对象
        reference_date: 参考日期 (YYYYMMDD格式)，默认为当天
        
    返回:
        str: 最近交易日 (YYYYMMDD格式)，如果未找到则返回None
    """
    import datetime
    
    # 如果未提供参考日期，使用当天
    if not reference_date:
        reference_date = datetime.datetime.now().strftime('%Y%m%d')
    
    # 处理日期格式
    formatted_date = reference_date
    if isinstance(reference_date, str) and reference_date.isdigit() and len(reference_date) == 8:
        formatted_date = f"{reference_date[:4]}-{reference_date[4:6]}-{reference_date[6:8]}"
    
    query = """
    SELECT cal_date
    FROM hk_tradecal
    WHERE cal_date <= $1::date AND is_open = 1
    ORDER BY cal_date DESC
    LIMIT 1
    """
    
    result = await db.fetchval(query, formatted_date)
    
    if result:
        # 将日期转换为YYYYMMDD格式
        return result.strftime('%Y%m%d')
    
    return None


# 获取下一个交易日
async def get_next_trade_day(db, reference_date: Optional[str] = None) -> Optional[str]:
    """
    获取参考日期后的下一个交易日（不包括当天）
    
    参数:
        db: 数据库连接对象
        reference_date: 参考日期 (YYYYMMDD格式)，默认为当天
        
    返回:
        str: 下一个交易日 (YYYYMMDD格式)，如果未找到则返回None
    """
    import datetime
    
    # 如果未提供参考日期，使用当天
    if not reference_date:
        reference_date = datetime.datetime.now().strftime('%Y%m%d')
    
    # 处理日期格式
    formatted_date = reference_date
    if isinstance(reference_date, str) and reference_date.isdigit() and len(reference_date) == 8:
        formatted_date = f"{reference_date[:4]}-{reference_date[4:6]}-{reference_date[6:8]}"
    
    query = """
    SELECT cal_date
    FROM hk_tradecal
    WHERE cal_date > $1::date AND is_open = 1
    ORDER BY cal_date
    LIMIT 1
    """
    
    result = await db.fetchval(query, formatted_date)
    
    if result:
        # 将日期转换为YYYYMMDD格式
        return result.strftime('%Y%m%d')
    
    return None


# 获取日期范围内的交易日
async def get_trade_days_in_range(db, start_date: str, end_date: str) -> List[str]:
    """
    获取日期范围内的所有交易日
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期 (YYYYMMDD格式)
        end_date: 结束日期 (YYYYMMDD格式)
        
    返回:
        List[str]: 交易日列表 (YYYYMMDD格式)
    """
    # 处理日期格式
    formatted_start_date = start_date
    if isinstance(start_date, str) and start_date.isdigit() and len(start_date) == 8:
        formatted_start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
    
    formatted_end_date = end_date
    if isinstance(end_date, str) and end_date.isdigit() and len(end_date) == 8:
        formatted_end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
    
    query = """
    SELECT cal_date
    FROM hk_tradecal
    WHERE cal_date BETWEEN $1::date AND $2::date AND is_open = 1
    ORDER BY cal_date
    """
    
    rows = await db.fetch(query, formatted_start_date, formatted_end_date)
    
    # 将日期转换为YYYYMMDD格式
    return [row['cal_date'].strftime('%Y%m%d') for row in rows]


# 检查是否为交易日
async def is_trade_day(db, check_date: str) -> bool:
    """
    检查指定日期是否为香港交易日
    
    参数:
        db: 数据库连接对象
        check_date: 要检查的日期 (YYYYMMDD格式)
        
    返回:
        bool: 如果是交易日返回True，否则返回False
    """
    # 处理日期格式
    formatted_date = check_date
    if isinstance(check_date, str) and check_date.isdigit() and len(check_date) == 8:
        formatted_date = f"{check_date[:4]}-{check_date[4:6]}-{check_date[6:8]}"
    
    query = """
    SELECT is_open
    FROM hk_tradecal
    WHERE cal_date = $1::date
    """
    
    result = await db.fetchval(query, formatted_date)
    
    return result == 1


# 获取交易日统计信息
async def get_tradecal_statistics(db, year: Optional[int] = None) -> Dict[str, Any]:
    """
    获取香港交易日历统计信息
    
    参数:
        db: 数据库连接对象
        year: 年份，可选，如不提供则统计所有年份
        
    返回:
        Dict: 包含交易日统计信息的字典
    """
    params = []
    where_clause = ""
    
    if year:
        where_clause = "WHERE EXTRACT(YEAR FROM cal_date) = $1"
        params.append(year)
    
    query = f"""
    SELECT 
        EXTRACT(YEAR FROM cal_date) as year,
        COUNT(*) as total_days,
        COUNT(CASE WHEN is_open = 1 THEN 1 END) as trade_days,
        COUNT(CASE WHEN is_open = 0 THEN 1 END) as non_trade_days
    FROM 
        hk_tradecal
    {where_clause}
    GROUP BY 
        year
    ORDER BY 
        year
    """
    
    rows = await db.fetch(query, *params)
    
    if not rows:
        error_msg = f"未找到{'年份 ' + str(year) + ' 的' if year else ''}香港交易日历统计数据"
        return {"error": error_msg}
    
    # 构建结果
    result = {
        "years": [],
        "summary": {
            "total_years": len(rows),
            "total_days": 0,
            "total_trade_days": 0,
            "total_non_trade_days": 0,
            "avg_trade_days_per_year": 0
        }
    }
    
    for row in rows:
        year_data = {
            "year": int(row["year"]),
            "total_days": row["total_days"],
            "trade_days": row["trade_days"],
            "non_trade_days": row["non_trade_days"],
            "trade_day_percentage": round(row["trade_days"] / row["total_days"] * 100, 2) if row["total_days"] > 0 else 0
        }
        result["years"].append(year_data)
        
        # 更新总计
        result["summary"]["total_days"] += year_data["total_days"]
        result["summary"]["total_trade_days"] += year_data["trade_days"]
        result["summary"]["total_non_trade_days"] += year_data["non_trade_days"]
    
    # 计算平均每年交易日
    if result["summary"]["total_years"] > 0:
        result["summary"]["avg_trade_days_per_year"] = round(
            result["summary"]["total_trade_days"] / result["summary"]["total_years"], 
            2
        )
    
    return result


# 获取指定日期前后的N个交易日
async def get_n_trade_days(db, reference_date: str, n: int, direction: str = 'forward') -> List[str]:
    """
    获取指定日期前后的N个交易日
    
    参数:
        db: 数据库连接对象
        reference_date: 参考日期 (YYYYMMDD格式)
        n: 要获取的交易日数量
        direction: 方向，'forward'表示向后，'backward'表示向前
        
    返回:
        List[str]: 交易日列表 (YYYYMMDD格式)
    """
    # 处理日期格式
    formatted_date = reference_date
    if isinstance(reference_date, str) and reference_date.isdigit() and len(reference_date) == 8:
        formatted_date = f"{reference_date[:4]}-{reference_date[4:6]}-{reference_date[6:8]}"
    
    comparison = ">" if direction == 'forward' else "<"
    order = "ASC" if direction == 'forward' else "DESC"
    
    query = f"""
    SELECT cal_date
    FROM hk_tradecal
    WHERE cal_date {comparison} $1::date AND is_open = 1
    ORDER BY cal_date {order}
    LIMIT $2
    """
    
    rows = await db.fetch(query, formatted_date, n)
    
    # 将日期转换为YYYYMMDD格式
    date_list = [row['cal_date'].strftime('%Y%m%d') for row in rows]
    
    # 如果是向前方向，返回正序结果
    if direction == 'backward':
        date_list.reverse()
    
    return date_list