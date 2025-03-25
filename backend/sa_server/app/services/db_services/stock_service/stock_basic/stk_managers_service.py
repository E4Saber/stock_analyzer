import pandas as pd
from typing import List, Optional
from app.external.tushare_api.stock_info_api import get_stk_managers
from app.data.db_modules.stock_modules.stock_basic.stk_managers import StockManagerData

class StockManagerService:
    """股票管理层数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_manager_data(self, ts_code: Optional[str] = None, 
                                 ann_date: Optional[str] = None,
                                 start_date: Optional[str] = None, 
                                 end_date: Optional[str] = None,
                                 batch_size: int = 1000) -> int:
        """
        从Tushare获取股票管理层数据并高效导入数据库
        
        参数:
            ts_code: 可选，指定要导入的股票代码
            ann_date: 可选，公告日期
            start_date: 可选，开始日期
            end_date: 可选，结束日期
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 至少需要提供一个查询参数
        if not any([ts_code, ann_date, start_date, end_date]):
            print("必须提供至少一个查询参数: ts_code、ann_date、start_date 或 end_date")
            return 0
            
        # 从Tushare获取数据
        df_result = get_stk_managers(ts_code=ts_code, ann_date=ann_date,
                                    start_date=start_date, end_date=end_date)
        
        if df_result is None or df_result.empty:
            query_params = []
            if ts_code:
                query_params.append(f"ts_code={ts_code}")
            if ann_date:
                query_params.append(f"ann_date={ann_date}")
            if start_date:
                query_params.append(f"start_date={start_date}")
            if end_date:
                query_params.append(f"end_date={end_date}")
                
            params_str = ", ".join(query_params) if query_params else "所有条件"
            print(f"未找到股票管理层数据: {params_str}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 处理数据并确保所有必填字段都有值
        valid_records = []
        for record in records:
            # 确保name字段存在
            if 'name' not in record or not record['name']:
                print(f"跳过缺少name字段的记录: {record}")
                continue
                
            # 确保ts_code字段存在，如果未提供则使用查询参数
            if 'ts_code' not in record or not record['ts_code']:
                if ts_code:
                    record['ts_code'] = ts_code
                else:
                    print(f"跳过缺少ts_code字段的记录: {record}")
                    continue
            
            valid_records.append(record)
        
        # 分批处理
        batches = [valid_records[i:i + batch_size] for i in range(0, len(valid_records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为StockManagerData对象
                manager_data_list = []
                for record in batch:
                    try:
                        manager_data = StockManagerData(**record)
                        manager_data_list.append(manager_data)
                    except Exception as e:
                        print(f"创建StockManagerData对象失败 {record.get('name', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if manager_data_list:
                    inserted = await self.batch_upsert_managers(manager_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_managers(self, manager_list: List[StockManagerData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            manager_list: 要插入或更新的管理层数据列表
            
        返回:
            处理的记录数
        """
        if not manager_list:
            return 0
        
        # 获取字段列表（排除id字段，因为它是自动生成的）
        columns = [col for col in list(manager_list[0].model_dump().keys()) if col != 'id']
        
        # 准备数据
        records = []
        for manager in manager_list:
            manager_dict = manager.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = manager_dict[col]
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
                    # 创建临时表，结构与目标表相同（排除id字段）
                    await conn.execute('CREATE TEMP TABLE temp_stk_managers (LIKE stk_managers) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_stk_managers', records=records, columns=columns)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    # 注意: stk_managers表使用ts_code, name, begin_date作为唯一约束
                    result = await conn.execute('''
                        INSERT INTO stk_managers (
                            ts_code, ann_date, name, gender, lev, title, edu,
                            national, birthday, begin_date, end_date, resume
                        )
                        SELECT 
                            ts_code, ann_date, name, gender, lev, title, edu,
                            national, birthday, begin_date, end_date, resume
                        FROM temp_stk_managers
                        ON CONFLICT (ts_code, name, begin_date) DO UPDATE SET
                            ann_date = EXCLUDED.ann_date,
                            gender = EXCLUDED.gender,
                            lev = EXCLUDED.lev,
                            title = EXCLUDED.title,
                            edu = EXCLUDED.edu,
                            national = EXCLUDED.national,
                            birthday = EXCLUDED.birthday,
                            end_date = EXCLUDED.end_date,
                            resume = EXCLUDED.resume
                    ''')
                    
                    # 解析结果获取处理的记录数
                    parts = result.split()
                    if len(parts) >= 3:
                        count = int(parts[2])
                    else:
                        count = len(records)  # 如果无法解析，假定全部成功
                    
                    return count
                    
            except Exception as e:
                print(f"批量导入过程中发生错误: {str(e)}")
                raise


# 快捷函数，用于导入指定股票的管理层数据
async def import_stock_managers(db, ts_code: str, batch_size: int = 1000):
    """
    导入指定股票的管理层数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StockManagerService(db)
    count = await service.import_manager_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条管理层记录 (股票代码: {ts_code})")
    return count


# 快捷函数，用于按公告日期导入管理层数据
async def import_managers_by_ann_date(db, ann_date: str, batch_size: int = 1000):
    """
    按公告日期导入管理层数据
    
    参数:
        db: 数据库连接对象
        ann_date: 公告日期
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StockManagerService(db)
    count = await service.import_manager_data(ann_date=ann_date, batch_size=batch_size)
    print(f"成功导入 {count} 条公告日期为 {ann_date} 的管理层记录")
    return count


# 快捷函数，用于按日期范围导入管理层数据
async def import_managers_by_date_range(db, start_date: str, end_date: str, batch_size: int = 1000):
    """
    按日期范围导入管理层数据
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期
        end_date: 结束日期
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StockManagerService(db)
    count = await service.import_manager_data(start_date=start_date, end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条日期范围为 {start_date} 至 {end_date} 的管理层记录")
    return count


# 快捷函数，用于导入多只股票的管理层数据
async def import_multiple_stocks_managers(db, ts_codes: List[str], batch_size: int = 1000):
    """
    批量导入多只股票的管理层数据
    
    参数:
        db: 数据库连接对象
        ts_codes: 股票TS代码列表
        batch_size: 批量处理大小
        
    返回:
        总导入的记录数
    """
    service = StockManagerService(db)
    total_count = 0
    
    for ts_code in ts_codes:
        count = await service.import_manager_data(ts_code=ts_code, batch_size=batch_size)
        total_count += count
        print(f"成功导入 {count} 条管理层记录 (股票代码: {ts_code})")
    
    print(f"总共导入 {total_count} 条管理层记录")
    return total_count