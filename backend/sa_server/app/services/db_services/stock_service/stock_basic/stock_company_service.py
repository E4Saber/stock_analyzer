import pandas as pd
from typing import List, Optional, Dict, Set
from app.external.tushare_api.stock_info_api import get_stock_company
from app.data.db_modules.stock_modules.stock_basic.stock_company import StockCompanyData


class StockCompanyService:
    """上市公司基本信息导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_company_data(self, 
                               ts_code: Optional[str] = None,
                               exchange: Optional[str] = None,
                               batch_size: int = 1000) -> int:
        """
        从Tushare获取上市公司基本信息并高效导入数据库
        
        参数:
            ts_code: 可选，指定要导入的股票代码
            exchange: 可选，交易所代码 SSE上交所 SZSE深交所
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_stock_company(ts_code=ts_code, exchange=exchange)
        
        if df_result is None or df_result.empty:
            print(f"未找到上市公司基本信息: ts_code={ts_code}, exchange={exchange}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 分批处理
        batches = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为StockCompanyData对象
                company_data_list = []
                for record in batch:
                    try:
                        company_data = StockCompanyData(**record)
                        company_data_list.append(company_data)
                    except Exception as e:
                        print(f"创建StockCompanyData对象失败 {record.get('ts_code', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if company_data_list:
                    inserted = await self.batch_upsert_company(company_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_company(self, company_list: List[StockCompanyData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            company_list: 要插入或更新的上市公司数据列表
            
        返回:
            处理的记录数
        """
        if not company_list:
            return 0
        
        # 获取字段列表
        columns = list(company_list[0].model_dump().keys())
        
        # 对输入数据进行去重，确保主键不重复
        seen_keys: Set[str] = set()
        unique_company_list = []
        
        for company in company_list:
            if company.ts_code not in seen_keys:
                seen_keys.add(company.ts_code)
                unique_company_list.append(company)
            else:
                print(f"检测到重复记录: {company.ts_code}，已跳过")
        
        # 准备数据
        records = []
        for company in unique_company_list:
            company_dict = company.model_dump()
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = company_dict[col]
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
                    column_defs = ', '.join([
                        f"{col} {self._get_column_type(col)}" 
                        for col in columns
                    ])
                    
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_stock_company (
                            {column_defs},
                            PRIMARY KEY (ts_code)
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    try:
                        await conn.copy_records_to_table('temp_stock_company', records=records, columns=columns)
                    except Exception as e:
                        print(f"复制数据到临时表失败，可能存在重复记录: {str(e)}")
                        # 如果批量复制失败，尝试逐条插入
                        await conn.execute("TRUNCATE TABLE temp_stock_company")
                        for record in records:
                            try:
                                insert_values = ", ".join([f"${i+1}" for i in range(len(record))])
                                await conn.execute(
                                    f"INSERT INTO temp_stock_company ({', '.join(columns)}) VALUES ({insert_values})",
                                    *record
                                )
                            except Exception as insert_error:
                                print(f"插入记录失败: {str(insert_error)}")
                    
                    # 构建更新语句中的SET部分（除了主键外的所有字段）
                    update_fields = [col for col in columns if col != 'ts_code']
                    if not update_fields:  # 如果没有可更新的字段，则简单跳过冲突
                        result = await conn.execute(f'''
                            INSERT INTO stock_company
                            SELECT * FROM temp_stock_company
                            ON CONFLICT (ts_code) DO NOTHING
                        ''')
                    else:
                        update_sets = [f"{col} = EXCLUDED.{col}" for col in update_fields]
                        update_clause = ', '.join(update_sets)
                        
                        # 从临时表插入到目标表，有冲突则更新
                        result = await conn.execute(f'''
                            INSERT INTO stock_company
                            SELECT * FROM temp_stock_company
                            ON CONFLICT (ts_code) DO UPDATE SET {update_clause}
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
    
    def _get_column_type(self, column_name: str) -> str:
        """
        根据字段名称获取PostgreSQL数据类型
        这个方法帮助创建临时表时确定正确的列类型
        """
        type_mapping = {
            'ts_code': 'VARCHAR(20)',
            'com_name': 'VARCHAR(100)',
            'com_id': 'VARCHAR(30)',
            'exchange': 'VARCHAR(20)',
            'chairman': 'VARCHAR(50)',
            'manager': 'VARCHAR(50)',
            'secretary': 'VARCHAR(50)',
            'reg_capital': 'NUMERIC(20,2)',
            'setup_date': 'DATE',
            'province': 'VARCHAR(30)',
            'city': 'VARCHAR(30)',
            'introduction': 'TEXT',
            'website': 'VARCHAR(100)',
            'email': 'VARCHAR(100)',
            'office': 'VARCHAR(150)',
            'employees': 'INTEGER',
            'main_business': 'TEXT',
            'business_scope': 'TEXT'
        }
        return type_mapping.get(column_name, 'TEXT')


# 快捷函数，用于导入所有上市公司信息
async def import_all_companies(db, batch_size: int = 1000) -> int:
    """
    导入所有上市公司基本信息
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StockCompanyService(db)
    count = await service.import_company_data(batch_size=batch_size)
    print(f"成功导入 {count} 条上市公司记录")
    return count


# 快捷函数，用于导入特定交易所的上市公司信息
async def import_exchange_companies(db, exchange: str, batch_size: int = 1000) -> int:
    """
    导入特定交易所的上市公司基本信息
    
    参数:
        db: 数据库连接对象
        exchange: 交易所代码 SSE上交所 SZSE深交所
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StockCompanyService(db)
    count = await service.import_company_data(exchange=exchange, batch_size=batch_size)
    print(f"成功导入 {count} 条 {exchange} 交易所的上市公司记录")
    return count


# 快捷函数，用于导入单个上市公司信息
async def import_single_company(db, ts_code: str) -> bool:
    """
    导入单个上市公司基本信息
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        
    返回:
        是否成功导入
    """
    service = StockCompanyService(db)
    count = await service.import_company_data(ts_code=ts_code)
    return count > 0


# 辅助函数，用于获取上市公司分布情况
async def get_company_distribution(db) -> Dict[str, int]:
    """
    获取上市公司在各省份的分布情况
    
    参数:
        db: 数据库连接对象
        
    返回:
        省份分布字典，键为省份名称，值为公司数量
    """
    from app.db.crud.stock_company_crud import StockCompanyCRUD
    
    crud = StockCompanyCRUD(db)
    distribution = await crud.get_company_count_by_province()
    return distribution