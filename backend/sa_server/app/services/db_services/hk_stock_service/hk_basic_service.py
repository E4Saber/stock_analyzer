import pandas as pd
from typing import List, Optional, Dict, Any
from app.external.tushare_api.hk_stock_api import get_hk_basic
from app.data.db_modules.hk_stock_modules.hk_basic import HkBasicData

class HkBasicService:
    """香港股票基本信息数据导入服务，实现高效批量导入和数据管理"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_hk_basic_data(self, 
                                  ts_code: Optional[str] = None, 
                                  list_status: Optional[str] = None,
                                  batch_size: int = 1000) -> int:
        """
        从Tushare获取香港股票基本信息并高效导入数据库
        
        参数:
            ts_code: TS代码
            list_status: 上市状态 L上市 D退市 P暂停上市，默认L
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 构建参数说明用于日志
        params = []
        if ts_code:
            params.append(f"ts_code={ts_code}")
        if list_status:
            params.append(f"list_status={list_status}")
        
        param_desc = ", ".join(params) if params else "所有"
        print(f"正在获取香港股票基本信息: {param_desc}")
        
        # 从Tushare获取数据
        try:
            df_result = get_hk_basic(ts_code=ts_code, list_status=list_status)
            
            if df_result is None or df_result.empty:
                print(f"未找到香港股票基本信息: {param_desc}")
                return 0
                
            print(f"获取到 {len(df_result)} 条香港股票基本信息")
        except Exception as e:
            print(f"获取香港股票基本信息失败: {str(e)}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 数据预处理和验证
        valid_records = await self._preprocess_records(records)
        
        if not valid_records:
            print("没有有效的香港股票基本信息记录可导入")
            return 0
            
        # 分批处理
        batches = [valid_records[i:i + batch_size] for i in range(0, len(valid_records), batch_size)]
        total_count = 0
        
        for batch_idx, batch in enumerate(batches):
            try:
                # 将批次数据转换为HkBasicData对象
                hk_basic_data_list = []
                for record in batch:
                    try:
                        # 为了确保数据类型正确，显式处理数值字段
                        if 'trade_unit' in record and record['trade_unit'] is not None:
                            if isinstance(record['trade_unit'], str) and record['trade_unit'].strip() == '':
                                record['trade_unit'] = None
                            elif record['trade_unit'] is not None:
                                try:
                                    record['trade_unit'] = float(record['trade_unit'])
                                except (ValueError, TypeError):
                                    record['trade_unit'] = None
                        
                        hk_basic_data = HkBasicData(**record)
                        hk_basic_data_list.append(hk_basic_data)
                    except Exception as e:
                        print(f"创建HkBasicData对象失败 {record.get('ts_code', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if hk_basic_data_list:
                    inserted = await self.batch_upsert_hk_basic(hk_basic_data_list)
                    total_count += inserted
                    print(f"批次 {batch_idx + 1}/{len(batches)} 导入成功: {inserted} 条香港股票基本信息")
            except Exception as e:
                print(f"批次 {batch_idx + 1}/{len(batches)} 导入失败: {str(e)}")
        
        print(f"总共成功导入 {total_count} 条香港股票基本信息")
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
        }
        
        valid_records = []
        invalid_count = 0
        
        for record in records:
            # 确保必填字段存在且有值
            for field, default_value in required_fields.items():
                if field not in record or record[field] is None or (isinstance(record[field], str) and record[field].strip() == ''):
                    record[field] = default_value
            
            # 如果缺少关键字段，跳过该记录
            if record['ts_code'] == '':
                invalid_count += 1
                continue
            
            # 处理日期格式，确保是YYYYMMDD格式
            for date_field in ['list_date', 'delist_date']:
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
    
    async def batch_upsert_hk_basic(self, hk_basic_list: List[HkBasicData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            hk_basic_list: 要插入或更新的香港股票基本信息列表
            
        返回:
            处理的记录数
        """
        if not hk_basic_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = hk_basic_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 使用字典来存储记录，如果有重复键，保留最新记录
        unique_records = {}
        
        for hk_basic in hk_basic_list:
            # 创建唯一键 (ts_code)
            key = hk_basic.ts_code
            unique_records[key] = hk_basic
        
        # 提取最终的唯一记录列表
        unique_hk_basic_list = list(unique_records.values())
        
        # 准备数据
        records = []
        for hk_basic in unique_hk_basic_list:
            hk_basic_dict = hk_basic.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = hk_basic_dict[col]
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
                    column_types = await self._get_column_type(conn, 'hk_basic', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_hk_basic (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_hk_basic', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO hk_basic ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_hk_basic
                        ON CONFLICT (ts_code) DO UPDATE SET {update_clause}
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


# 快捷函数，用于导入所有香港股票基本信息
async def import_all_hk_basic(db, batch_size: int = 1000) -> int:
    """
    导入所有香港股票基本信息
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = HkBasicService(db)
    count = await service.import_hk_basic_data(batch_size=batch_size)
    print(f"成功导入 {count} 条香港股票基本信息")
    return count


# 快捷函数，用于导入特定上市状态的香港股票基本信息
async def import_hk_basic_by_status(db, list_status: str, batch_size: int = 1000) -> int:
    """
    导入特定上市状态的香港股票基本信息
    
    参数:
        db: 数据库连接对象
        list_status: 上市状态 (L上市，D退市，P暂停上市)
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = HkBasicService(db)
    count = await service.import_hk_basic_data(list_status=list_status, batch_size=batch_size)
    print(f"成功导入 {count} 条上市状态为 {list_status} 的香港股票基本信息")
    return count


# 快捷函数，用于导入特定TS代码的香港股票基本信息
async def import_hk_basic_by_ts_code(db, ts_code: str, batch_size: int = 1000) -> int:
    """
    导入特定TS代码的香港股票基本信息
    
    参数:
        db: 数据库连接对象
        ts_code: TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = HkBasicService(db)
    count = await service.import_hk_basic_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条TS代码为 {ts_code} 的香港股票基本信息")
    return count


# 从数据库中查询香港股票基本信息
async def query_hk_basic_data(db, 
                             filters: Optional[Dict[str, Any]] = None, 
                             order_by: Optional[List[str]] = None,
                             limit: Optional[int] = None,
                             offset: Optional[int] = None) -> List[HkBasicData]:
    """
    动态查询香港股票基本信息，支持任意字段过滤和自定义排序
    
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
                 例如: {'list_status': 'L', 'name__ilike': '%银行%'}
        order_by: 排序字段列表，字段前加"-"表示降序，例如['-list_date', 'name']
        limit: 最大返回记录数
        offset: 跳过前面的记录数（用于分页）
        
    返回:
        List[HkBasicData]: 符合条件的香港股票基本信息列表
    
    示例:
        # 查询上市状态为"L"的所有香港股票，按上市日期降序排列
        data = await query_hk_basic_data(
            db,
            filters={'list_status': 'L'},
            order_by=['-list_date'],
            limit=10
        )
        
        # 分页查询名称中包含"银行"的香港股票
        data = await query_hk_basic_data(
            db,
            filters={'name__ilike': '%银行%'},
            order_by=['ts_code'],
            limit=20,
            offset=0
        )
    """
    from app.db.crud.hk_stock_crud.hk_basic_crud import HkBasicCRUD
    
    crud = HkBasicCRUD(db)
    results = await crud.get_hk_basic(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 获取市场分类统计
async def get_market_statistics(db) -> Dict[str, Any]:
    """
    统计不同市场类别的香港股票数量
    
    参数:
        db: 数据库连接对象
        
    返回:
        Dict: 包含不同市场类别统计信息的字典
    """
    query = """
    SELECT 
        market,
        COUNT(*) as stock_count,
        COUNT(CASE WHEN list_status = 'L' THEN 1 END) as listed_count,
        COUNT(CASE WHEN list_status = 'D' THEN 1 END) as delisted_count,
        COUNT(CASE WHEN list_status = 'P' THEN 1 END) as paused_count
    FROM 
        hk_basic
    GROUP BY 
        market
    ORDER BY 
        stock_count DESC
    """
    
    rows = await db.fetch(query)
    
    if not rows:
        return {"error": "未找到香港股票市场统计数据"}
    
    # 构建结果
    result = {
        "markets": [],
        "summary": {
            "total_stocks": 0,
            "total_listed": 0,
            "total_delisted": 0,
            "total_paused": 0
        }
    }
    
    for row in rows:
        market_data = {
            "market": row["market"] if row["market"] else "未知",
            "stock_count": row["stock_count"],
            "listed_count": row["listed_count"] or 0,
            "delisted_count": row["delisted_count"] or 0,
            "paused_count": row["paused_count"] or 0
        }
        result["markets"].append(market_data)
        
        # 更新总计
        result["summary"]["total_stocks"] += market_data["stock_count"]
        result["summary"]["total_listed"] += market_data["listed_count"]
        result["summary"]["total_delisted"] += market_data["delisted_count"]
        result["summary"]["total_paused"] += market_data["paused_count"]
    
    return result


# 获取上市时间分布
async def get_listing_date_distribution(db) -> Dict[str, Any]:
    """
    统计香港股票上市时间的分布情况
    
    参数:
        db: 数据库连接对象
        
    返回:
        Dict: 包含上市时间分布统计的字典
    """
    query = """
    SELECT 
        EXTRACT(YEAR FROM list_date) as year,
        COUNT(*) as stock_count
    FROM 
        hk_basic
    WHERE 
        list_date IS NOT NULL
    GROUP BY 
        year
    ORDER BY 
        year
    """
    
    rows = await db.fetch(query)
    
    if not rows:
        return {"error": "未找到香港股票上市时间分布数据"}
    
    # 构建结果
    result = {
        "yearly_distribution": [],
        "summary": {
            "total_with_list_date": 0,
            "earliest_year": None,
            "latest_year": None,
            "peak_year": None,
            "peak_count": 0
        }
    }
    
    for row in rows:
        year_data = {
            "year": int(row["year"]),
            "stock_count": row["stock_count"]
        }
        result["yearly_distribution"].append(year_data)
        
        # 更新总计和极值
        result["summary"]["total_with_list_date"] += year_data["stock_count"]
        
        if result["summary"]["earliest_year"] is None or year_data["year"] < result["summary"]["earliest_year"]:
            result["summary"]["earliest_year"] = year_data["year"]
            
        if result["summary"]["latest_year"] is None or year_data["year"] > result["summary"]["latest_year"]:
            result["summary"]["latest_year"] = year_data["year"]
            
        if result["summary"]["peak_count"] < year_data["stock_count"]:
            result["summary"]["peak_count"] = year_data["stock_count"]
            result["summary"]["peak_year"] = year_data["year"]
    
    return result


# 按交易单位分组统计
async def get_trade_unit_statistics(db) -> Dict[str, Any]:
    """
    统计香港股票按交易单位的分组情况
    
    参数:
        db: 数据库连接对象
        
    返回:
        Dict: 包含交易单位统计的字典
    """
    query = """
    SELECT 
        trade_unit,
        COUNT(*) as stock_count
    FROM 
        hk_basic
    WHERE 
        trade_unit IS NOT NULL AND 
        list_status = 'L'
    GROUP BY 
        trade_unit
    ORDER BY 
        trade_unit
    """
    
    rows = await db.fetch(query)
    
    if not rows:
        return {"error": "未找到香港股票交易单位统计数据"}
    
    # 构建结果
    result = {
        "trade_units": [],
        "summary": {
            "total_stocks": 0,
            "most_common_unit": None,
            "most_common_count": 0
        }
    }
    
    for row in rows:
        unit_data = {
            "trade_unit": float(row["trade_unit"]),
            "stock_count": row["stock_count"]
        }
        result["trade_units"].append(unit_data)
        
        # 更新总计和最常见单位
        result["summary"]["total_stocks"] += unit_data["stock_count"]
        
        if result["summary"]["most_common_count"] < unit_data["stock_count"]:
            result["summary"]["most_common_count"] = unit_data["stock_count"]
            result["summary"]["most_common_unit"] = unit_data["trade_unit"]
    
    return result