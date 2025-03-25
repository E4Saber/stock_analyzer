import datetime
import pandas as pd
from typing import List, Optional, Dict, Set, Tuple
from app.external.tushare_api.stock_info_api import get_hs_const
from app.data.db_modules.stock_modules.stock_basic.hs_const import HsConstData


class HsConstService:
    """沪深港通成份股数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_hs_const_data(self, 
                                  hs_type: Optional[str] = None,
                                  is_new: Optional[str] = None,
                                  batch_size: int = 1000) -> int:
        """
        从Tushare获取沪深港通成份股数据并高效导入数据库
        
        参数:
            hs_type: 可选，沪深港通类型，SH沪，SZ深
            is_new: 可选，是否最新，1是，0否
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 参数验证
        if hs_type and hs_type not in ['SH', 'SZ']:
            print(f"无效的hs_type参数: {hs_type}，应为'SH'或'SZ'")
            return 0
            
        if is_new and is_new not in ['0', '1']:
            print(f"无效的is_new参数: {is_new}，应为'0'或'1'")
            return 0
            
        # 从Tushare获取数据
        df_result = get_hs_const(hs_type=hs_type, is_new=is_new)
        
        if df_result is None or df_result.empty:
            query_params = []
            if hs_type:
                query_params.append(f"hs_type={hs_type}")
            if is_new:
                query_params.append(f"is_new={is_new}")
                
            params_str = ", ".join(query_params) if query_params else "所有条件"
            print(f"未找到沪深港通成份股数据: {params_str}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 分批处理
        batches = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为HsConstData对象
                hs_const_data_list = []
                for record in batch:
                    try:
                        hs_const_data = HsConstData(**record)
                        hs_const_data_list.append(hs_const_data)
                    except Exception as e:
                        print(f"创建HsConstData对象失败 {record.get('ts_code', '未知')}, {record.get('hs_type', '未知')}, {record.get('in_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if hs_const_data_list:
                    inserted = await self.batch_upsert_hs_const(hs_const_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_hs_const(self, hs_const_list: List[HsConstData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            hs_const_list: 要插入或更新的沪深港通成份股数据列表
            
        返回:
            处理的记录数
        """
        if not hs_const_list:
            return 0
        
        # 获取字段列表 (不包括id字段，因为它是自增的)
        columns = [col for col in list(hs_const_list[0].model_dump().keys()) if col != 'id']
        
        # 对输入数据进行去重，确保唯一键(ts_code, hs_type, in_date)不重复
        seen_keys: Set[Tuple[str, str, str]] = set()
        unique_hs_const_list = []
        
        for hs_const in hs_const_list:
            key = (hs_const.ts_code, hs_const.hs_type, str(hs_const.in_date))
            if key not in seen_keys:
                seen_keys.add(key)
                unique_hs_const_list.append(hs_const)
            else:
                print(f"检测到重复记录: {hs_const.ts_code}, {hs_const.hs_type}, {hs_const.in_date}，已跳过")
        
        # 准备数据
        records = []
        for hs_const in unique_hs_const_list:
            hs_const_dict = hs_const.model_dump()
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = hs_const_dict[col]
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
                    # 创建临时表，结构与目标表相同但不包括id字段
                    column_defs = ', '.join([
                        f"{col} {self._get_column_type(col)}" 
                        for col in columns
                    ])
                    
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_hs_const (
                            {column_defs},
                            UNIQUE (ts_code, hs_type, in_date)
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    try:
                        await conn.copy_records_to_table('temp_hs_const', records=records, columns=columns)
                    except Exception as e:
                        print(f"复制数据到临时表失败，可能存在重复记录: {str(e)}")
                        # 如果批量复制失败，尝试逐条插入
                        await conn.execute("TRUNCATE TABLE temp_hs_const")
                        for record in records:
                            try:
                                insert_values = ", ".join([f"${i+1}" for i in range(len(record))])
                                await conn.execute(
                                    f"INSERT INTO temp_hs_const ({', '.join(columns)}) VALUES ({insert_values})",
                                    *record
                                )
                            except Exception as insert_error:
                                print(f"插入记录失败: {str(insert_error)}")
                    
                    # 构建更新语句中的SET部分（除了唯一键外的所有字段）
                    update_fields = [col for col in columns if col not in ('ts_code', 'hs_type', 'in_date')]
                    if not update_fields:  # 如果没有可更新的字段，则简单跳过冲突
                        result = await conn.execute(f'''
                            INSERT INTO hs_const ({', '.join(columns)})
                            SELECT {', '.join(columns)} FROM temp_hs_const
                            ON CONFLICT (ts_code, hs_type, in_date) DO NOTHING
                        ''')
                    else:
                        update_sets = [f"{col} = EXCLUDED.{col}" for col in update_fields]
                        update_clause = ', '.join(update_sets)
                        
                        # 从临时表插入到目标表，有冲突则更新
                        result = await conn.execute(f'''
                            INSERT INTO hs_const ({', '.join(columns)})
                            SELECT {', '.join(columns)} FROM temp_hs_const
                            ON CONFLICT (ts_code, hs_type, in_date) DO UPDATE SET {update_clause}
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
            'hs_type': 'VARCHAR(2)',
            'in_date': 'DATE',
            'out_date': 'DATE',
            'is_new': 'CHAR(1)'
        }
        return type_mapping.get(column_name, 'TEXT')
    
    async def update_is_new_status(self) -> int:
        """
        更新所有记录的is_new状态，确保每个股票的每种类型只有一个最新记录
        
        返回:
            更新的记录数
        """
        async with self.db.pool.acquire() as conn:
            try:
                async with conn.transaction():
                    # 首先将所有记录设置为非最新
                    await conn.execute("UPDATE hs_const SET is_new = '0'")
                    
                    # 然后将每个股票每种类型的最新in_date的记录设置为最新
                    result = await conn.execute("""
                        UPDATE hs_const AS hc
                        SET is_new = '1'
                        FROM (
                            SELECT ts_code, hs_type, MAX(in_date) as max_in_date
                            FROM hs_const
                            WHERE out_date IS NULL OR out_date >= CURRENT_DATE
                            GROUP BY ts_code, hs_type
                        ) AS latest
                        WHERE hc.ts_code = latest.ts_code
                        AND hc.hs_type = latest.hs_type
                        AND hc.in_date = latest.max_in_date
                    """)
                    
                    # 解析结果获取更新的记录数
                    parts = result.split()
                    if len(parts) >= 3:
                        count = int(parts[2])
                        return count
                    return 0
            except Exception as e:
                print(f"更新is_new状态时发生错误: {str(e)}")
                raise


# 快捷函数，用于导入沪港通成份股数据
async def import_sh_connect(db, is_new: str = '1') -> int:
    """
    导入沪港通成份股数据
    
    参数:
        db: 数据库连接对象
        is_new: 是否最新，默认为'1'
        
    返回:
        导入的记录数
    """
    service = HsConstService(db)
    count = await service.import_hs_const_data(hs_type='SH', is_new=is_new)
    print(f"成功导入 {count} 条沪港通成份股记录")
    return count


# 快捷函数，用于导入深港通成份股数据
async def import_sz_connect(db, is_new: str = '1') -> int:
    """
    导入深港通成份股数据
    
    参数:
        db: 数据库连接对象
        is_new: 是否最新，默认为'1'
        
    返回:
        导入的记录数
    """
    service = HsConstService(db)
    count = await service.import_hs_const_data(hs_type='SZ', is_new=is_new)
    print(f"成功导入 {count} 条深港通成份股记录")
    return count


# 快捷函数，用于导入所有沪深港通成份股数据并更新最新状态
async def import_all_hs_connect(db) -> int:
    """
    导入所有沪深港通成份股数据并更新最新状态
    
    参数:
        db: 数据库连接对象
        
    返回:
        导入的总记录数
    """
    service = HsConstService(db)
    
    # 导入沪港通数据
    count_sh = await service.import_hs_const_data(hs_type='SH')
    print(f"成功导入 {count_sh} 条沪港通成份股记录")
    
    # 导入深港通数据
    count_sz = await service.import_hs_const_data(hs_type='SZ')
    print(f"成功导入 {count_sz} 条深港通成份股记录")
    
    # 更新最新状态
    updated = await service.update_is_new_status()
    print(f"更新了 {updated} 条记录的最新状态")
    
    return count_sh + count_sz


# 辅助函数，用于检查股票是否为沪深港通成份股
async def check_is_hs_stock(db, ts_code: str, date: Optional[datetime.date] = None) -> Dict[str, bool]:
    """
    检查股票是否为沪深港通成份股
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        date: 日期，默认为当天
        
    返回:
        包含沪港通和深港通状态的字典
    """
    from app.db.crud.stock_crud.stock_basic.hs_const_crud import HsConstCRUD
    
    crud = HsConstCRUD(db)
    check_date = date or datetime.date.today()
    
    # 检查是否为沪港通成份股
    is_sh = await crud.check_is_constituent(ts_code, check_date, 'SH')
    
    # 检查是否为深港通成份股
    is_sz = await crud.check_is_constituent(ts_code, check_date, 'SZ')
    
    return {
        'is_sh_connect': is_sh,
        'is_sz_connect': is_sz,
        'is_hs_stock': is_sh or is_sz
    }