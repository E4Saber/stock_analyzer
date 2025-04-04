import pandas as pd
from typing import List, Optional, Dict, Any
from app.external.tushare_api.stock.hitting_limit_up_api import get_kpl_concept
from app.data.db_modules.stock_modules.hitting_limit_up.kpl_concept import KplConceptData

class KplConceptService:
    """题材概念数据导入服务，实现高效批量导入和数据管理"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_kpl_concept_data(self, 
                                    trade_date: Optional[str] = None, 
                                    ts_code: Optional[str] = None,
                                    name: Optional[str] = None,
                                    start_date: Optional[str] = None,
                                    end_date: Optional[str] = None,
                                    batch_size: int = 1000) -> int:
        """
        从Tushare获取题材概念数据并高效导入数据库
        
        参数:
            trade_date: 交易日期(YYYYMMDD格式)
            ts_code: 题材代码（xxxxxx.KP格式）
            name: 题材名称
            start_date: 开始日期（用于查询日期范围，YYYYMMDD格式）
            end_date: 结束日期（用于查询日期范围，YYYYMMDD格式）
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
        if name:
            params.append(f"name={name}")
        if start_date:
            params.append(f"start_date={start_date}")
        if end_date:
            params.append(f"end_date={end_date}")
        
        param_desc = ", ".join(params) if params else "所有"
        print(f"正在获取题材概念数据: {param_desc}")
        
        # 从Tushare获取数据
        try:
            df_result = get_kpl_concept(trade_date=trade_date, ts_code=ts_code, name=name)
            
            if df_result is None or df_result.empty:
                print(f"未找到题材概念数据: {param_desc}")
                return 0
                
            print(f"获取到 {len(df_result)} 条题材概念数据")
        except Exception as e:
            print(f"获取题材概念数据失败: {str(e)}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 数据预处理和验证
        valid_records = await self._preprocess_records(records)
        
        if not valid_records:
            print("没有有效的题材概念数据记录可导入")
            return 0
            
        # 分批处理
        batches = [valid_records[i:i + batch_size] for i in range(0, len(valid_records), batch_size)]
        total_count = 0
        
        for batch_idx, batch in enumerate(batches):
            try:
                # 将批次数据转换为KplConceptData对象
                concept_data_list = []
                for record in batch:
                    try:
                        # 为了确保数据类型正确，显式处理数值字段
                        for field in ['z_t_num', 'up_num']:
                            if field in record and record[field] is not None:
                                if isinstance(record[field], str) and record[field].strip() == '':
                                    record[field] = None
                                elif record[field] is not None:
                                    try:
                                        record[field] = int(float(record[field]))
                                    except (ValueError, TypeError):
                                        record[field] = None
                        
                        concept_data = KplConceptData(**record)
                        concept_data_list.append(concept_data)
                    except Exception as e:
                        print(f"创建KplConceptData对象失败 {record.get('ts_code', '未知')}, {record.get('trade_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if concept_data_list:
                    inserted = await self.batch_upsert_kpl_concepts(concept_data_list)
                    total_count += inserted
                    print(f"批次 {batch_idx + 1}/{len(batches)} 导入成功: {inserted} 条题材概念记录")
            except Exception as e:
                print(f"批次 {batch_idx + 1}/{len(batches)} 导入失败: {str(e)}")
        
        print(f"总共成功导入 {total_count} 条题材概念记录")
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
    
    async def batch_upsert_kpl_concepts(self, concepts_list: List[KplConceptData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            concepts_list: 要插入或更新的题材概念数据列表
            
        返回:
            处理的记录数
        """
        if not concepts_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = concepts_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 使用字典来存储记录，如果有重复键，保留最新记录
        unique_records = {}
        
        for concept in concepts_list:
            # 创建唯一键 (ts_code, trade_date)
            key = (concept.ts_code, str(concept.trade_date))
            unique_records[key] = concept
        
        # 提取最终的唯一记录列表
        unique_concepts_list = list(unique_records.values())
        
        # 准备数据
        records = []
        for concept in unique_concepts_list:
            concept_dict = concept.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = concept_dict[col]
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
                    column_types = await self._get_column_type(conn, 'kpl_concept', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_kpl_concept (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_kpl_concept', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'trade_date']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO kpl_concept ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_kpl_concept
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


# 快捷函数，用于导入特定交易日期的题材概念数据
async def import_date_kpl_concept(db, trade_date: str, batch_size: int = 1000) -> int:
    """
    导入特定交易日期的题材概念数据
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = KplConceptService(db)
    count = await service.import_kpl_concept_data(trade_date=trade_date, batch_size=batch_size)
    print(f"成功导入 {count} 条交易日期为 {trade_date} 的题材概念记录")
    return count


# 快捷函数，用于导入特定题材代码的数据
async def import_ts_code_kpl_concept(db, ts_code: str, batch_size: int = 1000) -> int:
    """
    导入特定题材代码的数据
    
    参数:
        db: 数据库连接对象
        ts_code: 题材代码（xxxxxx.KP格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = KplConceptService(db)
    count = await service.import_kpl_concept_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条题材代码为 {ts_code} 的概念记录")
    return count


# 快捷函数，用于导入特定题材名称的数据
async def import_name_kpl_concept(db, name: str, batch_size: int = 1000) -> int:
    """
    导入特定题材名称的数据
    
    参数:
        db: 数据库连接对象
        name: 题材名称
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = KplConceptService(db)
    count = await service.import_kpl_concept_data(name=name, batch_size=batch_size)
    print(f"成功导入 {count} 条题材名称为 '{name}' 的概念记录")
    return count


# 快捷函数，用于导入特定日期范围的题材概念数据
async def import_date_range_kpl_concept(db, start_date: str, end_date: str, batch_size: int = 1000) -> int:
    """
    导入特定日期范围的题材概念数据
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期（YYYYMMDD格式）
        end_date: 结束日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = KplConceptService(db)
    count = await service.import_kpl_concept_data(
        start_date=start_date, 
        end_date=end_date, 
        batch_size=batch_size
    )
    print(f"成功导入 {count} 条日期范围为 {start_date} 至 {end_date} 的题材概念记录")
    return count


# 综合导入函数，支持多种参数组合
async def import_kpl_concept_with_params(db, **kwargs) -> int:
    """
    根据提供的参数导入题材概念数据
    
    参数:
        db: 数据库连接对象
        **kwargs: 可包含 trade_date, ts_code, name, start_date, end_date, batch_size 等参数
        
    返回:
        导入的记录数
    """
    service = KplConceptService(db)
    batch_size = kwargs.pop('batch_size', 1000)  # 提取并移除batch_size参数
    
    # 构建参数描述
    param_desc = []
    for key, value in kwargs.items():
        if value:
            param_desc.append(f"{key}={value}")
    
    params_info = ", ".join(param_desc) if param_desc else "所有可用参数"
    
    # 导入数据
    count = await service.import_kpl_concept_data(batch_size=batch_size, **kwargs)
    print(f"成功导入 {count} 条题材概念记录 ({params_info})")
    return count


# 导入所有题材概念数据
async def import_all_kpl_concepts(db, batch_size: int = 1000) -> int:
    """
    导入所有可获取的题材概念数据
    
    注意: 这可能会请求大量数据，请确保有足够的网络带宽和系统资源。
    根据数据量大小，此操作可能需要较长时间完成。
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小，默认1000条
        
    返回:
        导入的记录总数
    """
    service = KplConceptService(db)
    
    print("开始导入所有题材概念数据，此操作可能需要较长时间...")
    count = await service.import_kpl_concept_data(batch_size=batch_size)
    
    print(f"成功导入所有题材概念数据，共 {count} 条记录")
    return count


# 从数据库中查询题材概念数据
async def query_kpl_concept_data(db, 
                            filters: Optional[Dict[str, Any]] = None, 
                            order_by: Optional[List[str]] = None,
                            limit: Optional[int] = None,
                            offset: Optional[int] = None) -> List[KplConceptData]:
    """
    动态查询题材概念数据，支持任意字段过滤和自定义排序
    
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
                 例如: {'ts_code__like': '%.KP', 'z_t_num__gt': 5}
        order_by: 排序字段列表，字段前加"-"表示降序，例如['-z_t_num', 'name']
        limit: 最大返回记录数
        offset: 跳过前面的记录数（用于分页）
        
    返回:
        List[KplConceptData]: 符合条件的题材概念数据列表
    
    示例:
        # 查询某个交易日的所有题材，按涨停数量降序排列
        data = await query_kpl_concept_data(
            db,
            filters={'trade_date': '20230101'},
            order_by=['-z_t_num'],
            limit=10
        )
        
        # 分页查询涨停数量超过5的所有题材概念
        data = await query_kpl_concept_data(
            db,
            filters={'z_t_num__gt': 5},
            order_by=['-trade_date', '-z_t_num'],
            limit=20,
            offset=0
        )
    """
    from app.db.crud.stock_crud.hitting_limit_up.kpl_concept_crud import KplConceptCRUD
    
    crud = KplConceptCRUD(db)
    results = await crud.get_kpl_concepts(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 获取题材概念热度排行
async def get_kpl_concept_ranking(db, trade_date: str, limit: int = 20) -> List[KplConceptData]:
    """
    获取指定交易日的题材概念热度排行
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期（YYYYMMDD格式）
        limit: 返回的记录数量
        
    返回:
        List[KplConceptData]: 按涨停数量降序排列的题材概念数据
    """
    from app.db.crud.stock_crud.hitting_limit_up.kpl_concept_crud import KplConceptCRUD
    
    crud = KplConceptCRUD(db)
    
    results = await crud.get_kpl_concepts(
        filters={'trade_date': trade_date},
        order_by=['-z_t_num', '-up_num'],
        limit=limit
    )
    
    return results


# 跟踪题材概念历史表现
async def track_kpl_concept_history(db, ts_code: str, limit: int = 30) -> List[KplConceptData]:
    """
    跟踪特定题材概念的历史表现
    
    参数:
        db: 数据库连接对象
        ts_code: 题材代码（xxxxxx.KP格式）
        limit: 最大返回记录数
        
    返回:
        List[KplConceptData]: 该题材概念的历史数据，按交易日期降序排列
    """
    from app.db.crud.stock_crud.hitting_limit_up.kpl_concept_crud import KplConceptCRUD
    
    crud = KplConceptCRUD(db)
    
    results = await crud.get_kpl_concepts(
        filters={'ts_code': ts_code},
        order_by=['-trade_date'],
        limit=limit
    )
    
    return results


# 查找涨停数量最多的题材概念
async def get_top_z_t_concepts(db, start_date: str, end_date: str, limit: int = 10) -> Dict[str, Any]:
    """
    查找指定日期范围内涨停数量最多的题材概念
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期（YYYYMMDD格式）
        end_date: 结束日期（YYYYMMDD格式）
        limit: 返回排名数量
        
    返回:
        Dict: 包含涨停数量最多的题材概念排名
    """
    # 处理日期格式
    formatted_start_date = start_date
    if start_date and isinstance(start_date, str) and start_date.isdigit() and len(start_date) == 8:
        formatted_start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
        
    formatted_end_date = end_date
    if end_date and isinstance(end_date, str) and end_date.isdigit() and len(end_date) == 8:
        formatted_end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
    
    # 使用窗口函数计算每个题材概念在日期范围内的涨停总数
    query = """
    SELECT 
        ts_code,
        name,
        SUM(z_t_num) AS total_z_t_num,
        AVG(z_t_num) AS avg_z_t_num,
        COUNT(trade_date) AS days_count,
        MAX(z_t_num) AS max_z_t_num,
        MIN(z_t_num) AS min_z_t_num,
        MAX(trade_date) AS latest_date
    FROM 
        kpl_concept
    WHERE 
        trade_date BETWEEN $1::date AND $2::date
        AND z_t_num IS NOT NULL
    GROUP BY 
        ts_code, name
    ORDER BY 
        total_z_t_num DESC, avg_z_t_num DESC
    LIMIT $3
    """
    
    rows = await db.fetch(query, formatted_start_date, formatted_end_date, limit)
    
    if not rows:
        return {
            "error": f"未找到 {start_date} 至 {end_date} 期间的题材概念数据"
        }
    
    # 构建结果
    result = {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "top_concepts": []
    }
    
    for row in rows:
        concept = {
            "ts_code": row["ts_code"],
            "name": row["name"],
            "total_z_t_num": row["total_z_t_num"],
            "avg_z_t_num": float(row["avg_z_t_num"]) if row["avg_z_t_num"] is not None else None,
            "days_count": row["days_count"],
            "max_z_t_num": row["max_z_t_num"],
            "min_z_t_num": row["min_z_t_num"],
            "latest_date": row["latest_date"].strftime("%Y%m%d") if row["latest_date"] else None
        }
        result["top_concepts"].append(concept)
    
    return result


# 分析题材概念排名变动
async def analyze_concept_ranking_changes(db, prev_date: str, curr_date: str, limit: int = 20) -> Dict[str, Any]:
    """
    分析两个交易日之间题材概念排名的变动情况
    
    参数:
        db: 数据库连接对象
        prev_date: 前一个交易日期（YYYYMMDD格式）
        curr_date: 当前交易日期（YYYYMMDD格式）
        limit: 返回的记录数量
        
    返回:
        Dict: 包含题材概念排名变动分析的结果
    """
    # 获取前一天的排名数据
    prev_concepts = await get_kpl_concept_ranking(db, prev_date, limit=100)
    # 获取当前日的排名数据
    curr_concepts = await get_kpl_concept_ranking(db, curr_date, limit=100)
    
    if not prev_concepts or not curr_concepts:
        missing = []
        if not prev_concepts:
            missing.append(f"前一日期 {prev_date}")
        if not curr_concepts:
            missing.append(f"当前日期 {curr_date}")
        return {"error": f"未找到 {', '.join(missing)} 的数据"}
    
    # 构建排名映射
    prev_map = {concept.ts_code: {"rank": idx + 1, "data": concept} for idx, concept in enumerate(prev_concepts)}
    curr_map = {concept.ts_code: {"rank": idx + 1, "data": concept} for idx, concept in enumerate(curr_concepts)}
    
    # 分析排名变动
    new_entries = []
    dropped_out = []
    rank_improved = []
    rank_declined = []
    rank_unchanged = []
    
    # 检查新进入和排名提升的题材
    for ts_code, curr_info in curr_map.items():
        if ts_code not in prev_map:
            new_entries.append({
                "ts_code": ts_code,
                "name": curr_info["data"].name,
                "current_rank": curr_info["rank"],
                "z_t_num": curr_info["data"].z_t_num,
                "up_num": curr_info["data"].up_num
            })
        else:
            prev_rank = prev_map[ts_code]["rank"]
            curr_rank = curr_info["rank"]
            rank_change = prev_rank - curr_rank  # 正值表示排名提升
            
            change_data = {
                "ts_code": ts_code,
                "name": curr_info["data"].name,
                "previous_rank": prev_rank,
                "current_rank": curr_rank,
                "rank_change": rank_change,
                "z_t_num": curr_info["data"].z_t_num,
                "previous_z_t_num": prev_map[ts_code]["data"].z_t_num,
                "z_t_num_change": (curr_info["data"].z_t_num or 0) - (prev_map[ts_code]["data"].z_t_num or 0)
            }
            
            if rank_change > 0:
                rank_improved.append(change_data)
            elif rank_change < 0:
                rank_declined.append(change_data)
            else:
                rank_unchanged.append(change_data)
    
    # 检查排名跌出的题材
    for ts_code, prev_info in prev_map.items():
        if ts_code not in curr_map:
            dropped_out.append({
                "ts_code": ts_code,
                "name": prev_info["data"].name,
                "previous_rank": prev_info["rank"],
                "z_t_num": prev_info["data"].z_t_num,
                "up_num": prev_info["data"].up_num
            })
    
    # 按排名变动幅度排序
    rank_improved.sort(key=lambda x: x["rank_change"], reverse=True)
    rank_declined.sort(key=lambda x: x["rank_change"])
    
    # 构建结果
    result = {
        "dates": {
            "previous_date": prev_date,
            "current_date": curr_date
        },
        "summary": {
            "new_entries": len(new_entries),
            "dropped_out": len(dropped_out),
            "rank_improved": len(rank_improved),
            "rank_declined": len(rank_declined),
            "rank_unchanged": len(rank_unchanged)
        },
        "details": {
            "new_entries": new_entries[:limit],
            "dropped_out": dropped_out[:limit],
            "rank_improved": rank_improved[:limit],
            "rank_declined": rank_declined[:limit],
            "rank_unchanged": rank_unchanged[:limit]
        }
    }
    
    return result


# 分析题材概念趋势
async def analyze_kpl_concept_trends(db, days: int = 7, min_z_t_num: int = 3) -> Dict[str, Any]:
    """
    分析最近几天涨停数量持续增加的题材概念
    
    参数:
        db: 数据库连接对象
        days: 分析的天数
        min_z_t_num: 最小涨停数量阈值
        
    返回:
        Dict: 包含题材概念趋势分析的结果
    """
    # 首先获取最近几天的交易日期
    query = """
        SELECT DISTINCT trade_date
        FROM kpl_concept
        ORDER BY trade_date DESC
        LIMIT $1
    """
    recent_dates = await db.fetch(query, days)
    
    if not recent_dates or len(recent_dates) < 2:
        return {"error": "数据不足，无法进行趋势分析"}
    
    # 获取这些日期的所有题材概念数据
    date_list = [row['trade_date'] for row in recent_dates]
    
    from app.db.crud.stock_crud.hitting_limit_up.kpl_concept_crud import KplConceptCRUD
    crud = KplConceptCRUD(db)
    
    all_concepts = await crud.get_kpl_concepts(
        filters={'trade_date__in': date_list, 'z_t_num__ge': min_z_t_num},
        order_by=['ts_code', '-trade_date']
    )
    
    if not all_concepts:
        return {"error": f"未找到涨停数量≥{min_z_t_num}的题材概念数据"}
    
    # 按题材代码分组
    grouped_concepts = {}
    for concept in all_concepts:
        if concept.ts_code not in grouped_concepts:
            grouped_concepts[concept.ts_code] = []
        grouped_concepts[concept.ts_code].append(concept)
    
    # 分析每个题材的趋势
    trending_up = []
    steady = []
    trending_down = []
    
    for ts_code, concepts in grouped_concepts.items():
        # 至少需要有2个数据点才能分析趋势
        if len(concepts) < 2:
            continue
        
        # 按日期排序（最新的在前）
        concepts.sort(key=lambda x: x.trade_date, reverse=True)
        
        # 检查涨停数量的趋势
        trend_data = {
            "ts_code": ts_code,
            "name": concepts[0].name,
            "latest_date": concepts[0].trade_date.strftime('%Y%m%d') if concepts[0].trade_date else None,
            "latest_z_t_num": concepts[0].z_t_num,
            "history": [(c.trade_date.strftime('%Y%m%d') if c.trade_date else None, c.z_t_num) for c in concepts]
        }
        
        # 计算趋势
        is_increasing = True
        is_decreasing = True
        
        for i in range(len(concepts) - 1):
            curr_num = concepts[i].z_t_num if concepts[i].z_t_num is not None else 0
            next_num = concepts[i+1].z_t_num if concepts[i+1].z_t_num is not None else 0
            
            if curr_num <= next_num:
                is_increasing = False
            if curr_num >= next_num:
                is_decreasing = False
        
        if is_increasing:
            trending_up.append(trend_data)
        elif is_decreasing:
            trending_down.append(trend_data)
        else:
            steady.append(trend_data)
    
    # 按最新涨停数量排序
    trending_up.sort(key=lambda x: x["latest_z_t_num"] or 0, reverse=True)
    steady.sort(key=lambda x: x["latest_z_t_num"] or 0, reverse=True)
    trending_down.sort(key=lambda x: x["latest_z_t_num"] or 0, reverse=True)
    
    # 构建结果
    result = {
        "analysis_period": {
            "days": days,
            "start_date": date_list[-1].strftime('%Y%m%d') if date_list else None,
            "end_date": date_list[0].strftime('%Y%m%d') if date_list else None
        },
        "min_z_t_num": min_z_t_num,
        "trends": {
            "up": trending_up,
            "steady": steady,
            "down": trending_down
        },
        "summary": {
            "total_concepts": len(grouped_concepts),
            "trending_up": len(trending_up),
            "steady": len(steady),
            "trending_down": len(trending_down)
        }
    }
    
    return result


# 获取上升位数最多的题材概念
async def get_top_up_num_concepts(db, trade_date: str, limit: int = 10) -> List[KplConceptData]:
    """
    获取特定交易日排名上升位数最多的题材概念
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期（YYYYMMDD格式）
        limit: 返回记录数量
        
    返回:
        List[KplConceptData]: 上升位数最多的题材概念列表
    """
    from app.db.crud.stock_crud.hitting_limit_up.kpl_concept_crud import KplConceptCRUD
    
    crud = KplConceptCRUD(db)
    
    results = await crud.get_kpl_concepts(
        filters={'trade_date': trade_date, 'up_num__gt': 0},
        order_by=['-up_num', '-z_t_num'],
        limit=limit
    )
    
    return results