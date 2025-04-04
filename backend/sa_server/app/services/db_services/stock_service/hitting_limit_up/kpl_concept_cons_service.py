import pandas as pd
from typing import List, Optional, Dict, Any
from app.external.tushare_api.stock.hitting_limit_up_api import get_kpl_concept_cons
from app.data.db_modules.stock_modules.hitting_limit_up.kpl_concept_cons import KplConceptConsData

class KplConceptConsService:
    """题材概念成分数据导入服务，实现高效批量导入和数据管理"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_kpl_concept_cons_data(self, 
                                        trade_date: Optional[str] = None, 
                                        ts_code: Optional[str] = None,
                                        con_code: Optional[str] = None,
                                        batch_size: int = 1000) -> int:
        """
        从Tushare获取题材概念成分数据并高效导入数据库
        
        参数:
            trade_date: 交易日期(YYYYMMDD格式)
            ts_code: 题材代码（xxxxxx.KP格式）
            con_code: 成分股票代码（xxxxxx.SH格式）
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
        if con_code:
            params.append(f"con_code={con_code}")
        
        param_desc = ", ".join(params) if params else "所有"
        print(f"正在获取题材概念成分数据: {param_desc}")
        
        # 从Tushare获取数据
        try:
            df_result = get_kpl_concept_cons(trade_date=trade_date, ts_code=ts_code, con_code=con_code)
            
            if df_result is None or df_result.empty:
                print(f"未找到题材概念成分数据: {param_desc}")
                return 0
                
            print(f"获取到 {len(df_result)} 条题材概念成分数据")
        except Exception as e:
            print(f"获取题材概念成分数据失败: {str(e)}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 数据预处理和验证
        valid_records = await self._preprocess_records(records)
        
        if not valid_records:
            print("没有有效的题材概念成分数据记录可导入")
            return 0
            
        # 分批处理
        batches = [valid_records[i:i + batch_size] for i in range(0, len(valid_records), batch_size)]
        total_count = 0
        
        for batch_idx, batch in enumerate(batches):
            try:
                # 将批次数据转换为KplConceptConsData对象
                concept_cons_data_list = []
                for record in batch:
                    try:
                        # 为了确保数据类型正确，显式处理数值字段
                        if 'hot_num' in record and record['hot_num'] is not None:
                            if isinstance(record['hot_num'], str) and record['hot_num'].strip() == '':
                                record['hot_num'] = None
                            elif record['hot_num'] is not None:
                                try:
                                    record['hot_num'] = int(float(record['hot_num']))
                                except (ValueError, TypeError):
                                    record['hot_num'] = None
                        
                        concept_cons_data = KplConceptConsData(**record)
                        concept_cons_data_list.append(concept_cons_data)
                    except Exception as e:
                        print(f"创建KplConceptConsData对象失败 {record.get('ts_code', '未知')}, {record.get('con_code', '未知')}, {record.get('trade_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if concept_cons_data_list:
                    inserted = await self.batch_upsert_kpl_concept_cons(concept_cons_data_list)
                    total_count += inserted
                    print(f"批次 {batch_idx + 1}/{len(batches)} 导入成功: {inserted} 条题材概念成分记录")
            except Exception as e:
                print(f"批次 {batch_idx + 1}/{len(batches)} 导入失败: {str(e)}")
        
        print(f"总共成功导入 {total_count} 条题材概念成分记录")
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
            'con_code': '',
            'con_name': '',
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
            if record['ts_code'] == '' or record['name'] == '' or record['con_code'] == '' or record['con_name'] == '' or record['trade_date'] is None:
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
    
    async def batch_upsert_kpl_concept_cons(self, concept_cons_list: List[KplConceptConsData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            concept_cons_list: 要插入或更新的题材概念成分数据列表
            
        返回:
            处理的记录数
        """
        if not concept_cons_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = concept_cons_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 使用字典来存储记录，如果有重复键，保留最新记录
        unique_records = {}
        
        for concept_cons in concept_cons_list:
            # 创建唯一键 (ts_code, con_code, trade_date)
            key = (concept_cons.ts_code, concept_cons.con_code, str(concept_cons.trade_date))
            unique_records[key] = concept_cons
        
        # 提取最终的唯一记录列表
        unique_concept_cons_list = list(unique_records.values())
        
        # 准备数据
        records = []
        for concept_cons in unique_concept_cons_list:
            concept_cons_dict = concept_cons.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = concept_cons_dict[col]
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
                    column_types = await self._get_column_type(conn, 'kpl_concept_cons', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_kpl_concept_cons (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_kpl_concept_cons', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'con_code', 'trade_date']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO kpl_concept_cons ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_kpl_concept_cons
                        ON CONFLICT (ts_code, con_code, trade_date) DO UPDATE SET {update_clause}
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


# 快捷函数，用于导入特定交易日期的题材概念成分数据
async def import_date_kpl_concept_cons(db, trade_date: str, batch_size: int = 1000) -> int:
    """
    导入特定交易日期的题材概念成分数据
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = KplConceptConsService(db)
    count = await service.import_kpl_concept_cons_data(trade_date=trade_date, batch_size=batch_size)
    print(f"成功导入 {count} 条交易日期为 {trade_date} 的题材概念成分记录")
    return count


# 快捷函数，用于导入特定题材代码的成分数据
async def import_ts_code_kpl_concept_cons(db, ts_code: str, batch_size: int = 1000) -> int:
    """
    导入特定题材代码的成分数据
    
    参数:
        db: 数据库连接对象
        ts_code: 题材代码（xxxxxx.KP格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = KplConceptConsService(db)
    count = await service.import_kpl_concept_cons_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条题材代码为 {ts_code} 的概念成分记录")
    return count


# 快捷函数，用于导入特定股票代码的概念成分数据
async def import_con_code_kpl_concept_cons(db, con_code: str, batch_size: int = 1000) -> int:
    """
    导入特定股票代码的概念成分数据
    
    参数:
        db: 数据库连接对象
        con_code: 股票代码（xxxxxx.SH格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = KplConceptConsService(db)
    count = await service.import_kpl_concept_cons_data(con_code=con_code, batch_size=batch_size)
    print(f"成功导入 {count} 条股票代码为 {con_code} 的概念成分记录")
    return count


# 综合导入函数，支持多种参数组合
async def import_kpl_concept_cons_with_params(db, **kwargs) -> int:
    """
    根据提供的参数导入题材概念成分数据
    
    参数:
        db: 数据库连接对象
        **kwargs: 可包含 trade_date, ts_code, con_code, batch_size 等参数
        
    返回:
        导入的记录数
    """
    service = KplConceptConsService(db)
    batch_size = kwargs.pop('batch_size', 1000)  # 提取并移除batch_size参数
    
    # 构建参数描述
    param_desc = []
    for key, value in kwargs.items():
        if value:
            param_desc.append(f"{key}={value}")
    
    params_info = ", ".join(param_desc) if param_desc else "所有可用参数"
    
    # 导入数据
    count = await service.import_kpl_concept_cons_data(batch_size=batch_size, **kwargs)
    print(f"成功导入 {count} 条题材概念成分记录 ({params_info})")
    return count


# 导入所有题材概念成分数据
async def import_all_kpl_concept_cons(db, batch_size: int = 1000) -> int:
    """
    导入所有可获取的题材概念成分数据
    
    注意: 这可能会请求大量数据，请确保有足够的网络带宽和系统资源。
    根据数据量大小，此操作可能需要较长时间完成。
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小，默认1000条
        
    返回:
        导入的记录总数
    """
    service = KplConceptConsService(db)
    
    print("开始导入所有题材概念成分数据，此操作可能需要较长时间...")
    count = await service.import_kpl_concept_cons_data(batch_size=batch_size)
    
    print(f"成功导入所有题材概念成分数据，共 {count} 条记录")
    return count


# 从数据库中查询题材概念成分数据
async def query_kpl_concept_cons_data(db, 
                                 filters: Optional[Dict[str, Any]] = None, 
                                 order_by: Optional[List[str]] = None,
                                 limit: Optional[int] = None,
                                 offset: Optional[int] = None) -> List[KplConceptConsData]:
    """
    动态查询题材概念成分数据，支持任意字段过滤和自定义排序
    
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
                 例如: {'ts_code__like': '%.KP', 'hot_num__gt': 5}
        order_by: 排序字段列表，字段前加"-"表示降序，例如['-hot_num', 'name']
        limit: 最大返回记录数
        offset: 跳过前面的记录数（用于分页）
        
    返回:
        List[KplConceptConsData]: 符合条件的题材概念成分数据列表
    
    示例:
        # 查询某个交易日的特定题材的所有成分股
        data = await query_kpl_concept_cons_data(
            db,
            filters={'trade_date': '20230101', 'ts_code': '123456.KP'},
            order_by=['con_name'],
            limit=50
        )
        
        # 分页查询人气值超过100的所有题材概念成分
        data = await query_kpl_concept_cons_data(
            db,
            filters={'hot_num__gt': 100},
            order_by=['-trade_date', '-hot_num'],
            limit=20,
            offset=0
        )
    """
    from app.db.crud.stock_crud.hitting_limit_up.kpl_concept_cons_crud import KplConceptConsCRUD
    
    crud = KplConceptConsCRUD(db)
    results = await crud.get_kpl_concept_cons(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 获取特定股票的所有题材概念
async def get_stock_concepts(db, con_code: str, trade_date: Optional[str] = None, limit: int = 50) -> List[KplConceptConsData]:
    """
    获取特定股票所属的所有题材概念
    
    参数:
        db: 数据库连接对象
        con_code: 股票代码（xxxxxx.SH格式）
        trade_date: 可选的交易日期过滤（YYYYMMDD格式）
        limit: 返回的最大记录数
        
    返回:
        List[KplConceptConsData]: 该股票所属的题材概念列表
    """
    from app.db.crud.stock_crud.hitting_limit_up.kpl_concept_cons_crud import KplConceptConsCRUD
    
    crud = KplConceptConsCRUD(db)
    
    if trade_date:
        results = await crud.get_kpl_concept_cons(
            filters={'con_code': con_code, 'trade_date': trade_date},
            order_by=['ts_code'],
            limit=limit
        )
    else:
        results = await crud.get_kpl_concept_cons(
            filters={'con_code': con_code},
            order_by=['-trade_date', 'ts_code'],
            limit=limit
        )
    
    return results


# 获取特定题材概念的所有成分股
async def get_concept_stocks(db, ts_code: str, trade_date: Optional[str] = None, limit: int = 100) -> List[KplConceptConsData]:
    """
    获取特定题材概念的所有成分股
    
    参数:
        db: 数据库连接对象
        ts_code: 题材代码（xxxxxx.KP格式）
        trade_date: 可选的交易日期过滤（YYYYMMDD格式）
        limit: 返回的最大记录数
        
    返回:
        List[KplConceptConsData]: 该题材概念的成分股列表
    """
    from app.db.crud.stock_crud.hitting_limit_up.kpl_concept_cons_crud import KplConceptConsCRUD
    
    crud = KplConceptConsCRUD(db)
    
    if trade_date:
        results = await crud.get_kpl_concept_cons(
            filters={'ts_code': ts_code, 'trade_date': trade_date},
            order_by=['con_name'],
            limit=limit
        )
    else:
        results = await crud.get_kpl_concept_cons(
            filters={'ts_code': ts_code},
            order_by=['-trade_date', 'con_name'],
            limit=limit
        )
    
    return results


# 获取人气最高的题材概念成分
async def get_hottest_concept_stocks(db, trade_date: str, limit: int = 50) -> Dict[str, Any]:
    """
    获取指定交易日人气值最高的题材概念成分
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期（YYYYMMDD格式）
        limit: 返回的记录数量
        
    返回:
        Dict: 人气最高的题材概念成分信息
    """
    # 处理日期格式
    formatted_trade_date = trade_date
    if trade_date and isinstance(trade_date, str) and trade_date.isdigit() and len(trade_date) == 8:
        formatted_trade_date = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:8]}"
    
    # 查询人气值最高的题材概念成分
    query = """
    SELECT 
        kcc.ts_code,
        kcc.name,
        kcc.con_code,
        kcc.con_name,
        kcc.hot_num,
        kcc.desc
    FROM 
        kpl_concept_cons kcc
    WHERE 
        kcc.trade_date = $1::date
        AND kcc.hot_num IS NOT NULL
    ORDER BY 
        kcc.hot_num DESC
    LIMIT $2
    """
    
    rows = await db.fetch(query, formatted_trade_date, limit)
    
    if not rows:
        return {
            "error": f"未找到 {trade_date} 的题材概念成分数据"
        }
    
    # 构建结果
    result = {
        "trade_date": trade_date,
        "hot_stocks": []
    }
    
    for row in rows:
        stock = {
            "ts_code": row["ts_code"],
            "name": row["name"],
            "con_code": row["con_code"],
            "con_name": row["con_name"],
            "hot_num": row["hot_num"],
            "desc": row["desc"]
        }
        result["hot_stocks"].append(stock)
    
    return result


# 分析特定股票的题材变化
async def analyze_stock_concept_changes(db, con_code: str, prev_date: str, curr_date: str) -> Dict[str, Any]:
    """
    分析特定股票在两个交易日之间题材概念的变化情况
    
    参数:
        db: 数据库连接对象
        con_code: 股票代码（xxxxxx.SH格式）
        prev_date: 前一个交易日期（YYYYMMDD格式）
        curr_date: 当前交易日期（YYYYMMDD格式）
        
    返回:
        Dict: 包含股票题材概念变化分析的结果
    """
    # 获取前一天的题材数据
    prev_concepts = await get_stock_concepts(db, con_code, prev_date, limit=100)
    # 获取当前日的题材数据
    curr_concepts = await get_stock_concepts(db, con_code, curr_date, limit=100)
    
    if not prev_concepts and not curr_concepts:
        return {"error": f"未找到股票 {con_code} 在 {prev_date} 和 {curr_date} 的题材概念数据"}
    
    # 构建题材映射
    prev_map = {concept.ts_code: concept for concept in prev_concepts}
    curr_map = {concept.ts_code: concept for concept in curr_concepts}
    
    # 分析变化
    new_concepts = []
    removed_concepts = []
    hot_changed = []
    
    # 检查新增的题材
    for ts_code, curr_concept in curr_map.items():
        if ts_code not in prev_map:
            new_concepts.append({
                "ts_code": ts_code,
                "name": curr_concept.name,
                "hot_num": curr_concept.hot_num,
                "desc": curr_concept.desc
            })
        else:
            # 检查人气值变化
            prev_hot = prev_map[ts_code].hot_num or 0
            curr_hot = curr_concept.hot_num or 0
            
            if prev_hot != curr_hot:
                hot_changed.append({
                    "ts_code": ts_code,
                    "name": curr_concept.name,
                    "previous_hot_num": prev_hot,
                    "current_hot_num": curr_hot,
                    "change": curr_hot - prev_hot
                })
    
    # 检查移除的题材
    for ts_code, prev_concept in prev_map.items():
        if ts_code not in curr_map:
            removed_concepts.append({
                "ts_code": ts_code,
                "name": prev_concept.name,
                "hot_num": prev_concept.hot_num,
                "desc": prev_concept.desc
            })
    
    # 对人气变化排序，变化最大的在前
    hot_changed.sort(key=lambda x: abs(x["change"]), reverse=True)
    
    # 获取股票名称
    stock_name = ""
    if curr_concepts:
        stock_name = curr_concepts[0].con_name
    elif prev_concepts:
        stock_name = prev_concepts[0].con_name
    
    # 构建结果
    result = {
        "stock": {
            "con_code": con_code,
            "con_name": stock_name
        },
        "dates": {
            "previous_date": prev_date,
            "current_date": curr_date
        },
        "summary": {
            "new_concepts": len(new_concepts),
            "removed_concepts": len(removed_concepts),
            "hot_changed": len(hot_changed),
            "total_previous": len(prev_concepts),
            "total_current": len(curr_concepts)
        },
        "details": {
            "new_concepts": new_concepts,
            "removed_concepts": removed_concepts,
            "hot_changed": hot_changed
        }
    }
    
    return result