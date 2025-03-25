import pandas as pd
from typing import List, Optional
from app.external.tushare_api.index_info_api import get_index_basic
from app.data.db_modules.index_modules.index_basic import IndexBasicData

class IndexBasicService:
    """指数基础数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_index_data(self, ts_code: Optional[str] = None, name: Optional[str] = None, 
                              market: Optional[str] = None, publisher: Optional[str] = None, 
                              category: Optional[str] = None, batch_size: int = 1000) -> int:
        """
        从Tushare获取指数数据并高效导入数据库
        
        参数:
            ts_code: 可选，指数代码
            name: 可选，指数简称
            market: 可选，指定要导入的市场，为None时导入所有市场指数
            publisher: 可选，发布商
            category: 可选，指数类别
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_index_basic(ts_code=ts_code, name=name, market=market, 
                                   publisher=publisher, category=category)
        
        if df_result is None or df_result.empty:
            print(f"未找到指数数据: {market if market else '所有市场'}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 定义必填字段及默认值
        required_fields = {
            'ts_code': '',
            'name': '',
            'market': '未知',
        }
        
        # 处理数据并确保所有必填字段都有值
        valid_records = []
        for record in records:
            for field, default_value in required_fields.items():
                if field not in record or record[field] is None or (isinstance(record[field], str) and record[field] == ''):
                    record[field] = default_value
                    
            # 将'desc'字段重命名为'description'（如果存在）
            if 'desc' in record:
                record['description'] = record.pop('desc')
                
            valid_records.append(record)
        
        # 分批处理
        batches = [valid_records[i:i + batch_size] for i in range(0, len(valid_records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为IndexBasicData对象
                index_data_list = []
                for record in batch:
                    try:
                        index_data = IndexBasicData(**record)
                        index_data_list.append(index_data)
                    except Exception as e:
                        print(f"创建IndexBasicData对象失败 {record.get('ts_code', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if index_data_list:
                    inserted = await self.batch_upsert_indexes(index_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_indexes(self, index_list: List[IndexBasicData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            index_list: 要插入或更新的指数数据列表
            
        返回:
            处理的记录数
        """
        if not index_list:
            return 0
        
        # 获取字段列表
        columns = list(index_list[0].model_dump().keys())
        
        # 准备数据
        records = []
        for index in index_list:
            index_dict = index.model_dump()
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = index_dict[col]
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
                    # 创建临时表，结构与目标表相同
                    await conn.execute('CREATE TEMP TABLE temp_index_basic (LIKE index_basic) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_index_basic', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（除了主键外的所有字段）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col != 'ts_code']
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO index_basic 
                        SELECT * FROM temp_index_basic
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


# 快捷函数，用于导入所有市场的指数数据
async def import_all_indexes(db, batch_size: int = 1000):
    """
    导入所有市场的指数基础数据
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = IndexBasicService(db)
    count = await service.import_index_data(batch_size=batch_size)
    print(f"成功导入 {count} 条指数记录")
    return count


# 快捷函数，用于导入特定市场的指数数据
async def import_market_indexes(db, market: str):
    """
    导入特定市场的指数基础数据
    
    参数:
        db: 数据库连接对象
        market: 市场标识
        
    返回:
        导入的记录数
    """
    service = IndexBasicService(db)
    count = await service.import_index_data(market=market)
    print(f"成功导入 {count} 条 {market} 市场指数记录")
    return count


# 快捷函数，用于导入单个指数的数据
async def import_single_index(db, ts_code: str):
    """
    导入单个指数的基础数据
    
    参数:
        db: 数据库连接对象
        ts_code: 指数TS代码
        
    返回:
        是否成功导入
    """
    service = IndexBasicService(db)
    count = await service.import_index_data(ts_code=ts_code)
    return count > 0


# 快捷函数，用于按类别导入指数数据
async def import_category_indexes(db, category: str):
    """
    导入特定类别的指数基础数据
    
    参数:
        db: 数据库连接对象
        category: 指数类别
        
    返回:
        导入的记录数
    """
    service = IndexBasicService(db)
    count = await service.import_index_data(category=category)
    print(f"成功导入 {count} 条 {category} 类别指数记录")
    return count


# 快捷函数，用于按发布商导入指数数据
async def import_publisher_indexes(db, publisher: str):
    """
    导入特定发布商的指数基础数据
    
    参数:
        db: 数据库连接对象
        publisher: 发布商
        
    返回:
        导入的记录数
    """
    service = IndexBasicService(db)
    count = await service.import_index_data(publisher=publisher)
    print(f"成功导入 {count} 条由 {publisher} 发布的指数记录")
    return count