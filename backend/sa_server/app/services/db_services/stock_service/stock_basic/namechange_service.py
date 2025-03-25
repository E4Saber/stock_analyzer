import datetime
import pandas as pd
from typing import List, Optional, Union
from app.external.tushare_api.stock_info_api import get_namechange
from app.data.db_modules.stock_modules.stock_basic.namechange import NameChangeData


class NameChangeService:
    """股票曾用名数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_namechange_data(self, 
                                    ts_code: Optional[str] = None,
                                    start_date: Optional[Union[str, datetime.date]] = None,
                                    end_date: Optional[Union[str, datetime.date]] = None,
                                    batch_size: int = 1000) -> int:
        """
        从Tushare获取股票曾用名数据并高效导入数据库
        
        参数:
            ts_code: 可选，指定要导入的股票代码
            start_date: 可选，起始日期
            end_date: 可选，结束日期
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 处理日期参数
        start_date_str = self._format_date(start_date) if start_date else None
        end_date_str = self._format_date(end_date) if end_date else None
        
        # 从Tushare获取数据
        df_result = get_namechange(ts_code=ts_code, start_date=start_date_str, end_date=end_date_str)
        
        if df_result is None or df_result.empty:
            print(f"未找到股票曾用名数据: ts_code={ts_code}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 分批处理
        batches = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为NameChangeData对象
                namechange_data_list = []
                for record in batch:
                    try:
                        namechange_data = NameChangeData(**record)
                        namechange_data_list.append(namechange_data)
                    except Exception as e:
                        print(f"创建NameChangeData对象失败 {record.get('ts_code', '未知')}, {record.get('start_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if namechange_data_list:
                    inserted = await self.batch_upsert_namechange(namechange_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_namechange(self, namechange_list: List[NameChangeData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            namechange_list: 要插入或更新的曾用名数据列表
            
        返回:
            处理的记录数
        """
        if not namechange_list:
            return 0
        
        # 获取字段列表 (不包括id字段，因为它是自增的)
        columns = [col for col in list(namechange_list[0].model_dump().keys()) if col != 'id']

        # 对输入数据进行去重，确保唯一键(ts_code, start_date)不重复
        seen_keys = set()
        unique_namechange_list = []
        
        for namechange in namechange_list:
            key = (namechange.ts_code, str(namechange.start_date))
            if key not in seen_keys:
                seen_keys.add(key)
                unique_namechange_list.append(namechange)
            else:
                print(f"检测到重复记录: {namechange.ts_code}, {namechange.start_date}，已跳过")
        
        # 准备数据
        records = []
        for namechange in unique_namechange_list:
            namechange_dict = namechange.model_dump()
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = namechange_dict[col]
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
                        CREATE TEMP TABLE temp_namechange (
                            {column_defs}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_namechange', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（除了ts_code和start_date外的所有字段）
                    update_fields = [col for col in columns if col not in ('ts_code', 'start_date')]
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in update_fields]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO namechange ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_namechange
                        ON CONFLICT (ts_code, start_date) DO UPDATE SET {update_clause}
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
    
    def _format_date(self, date_input: Union[str, datetime.date]) -> str:
        """将日期转换为YYYYMMDD格式字符串"""
        if isinstance(date_input, str):
            try:
                if date_input.isdigit() and len(date_input) == 8:
                    return date_input
                date_obj = datetime.date.fromisoformat(date_input)
                return date_obj.strftime('%Y%m%d')
            except ValueError:
                raise ValueError(f"无效的日期格式: {date_input}")
        elif isinstance(date_input, datetime.date):
            return date_input.strftime('%Y%m%d')
        else:
            raise TypeError(f"不支持的日期类型: {type(date_input)}")
    
    def _get_column_type(self, column_name: str) -> str:
        """
        根据字段名称获取PostgreSQL数据类型
        这个方法帮助创建临时表时确定正确的列类型
        """
        type_mapping = {
            'ts_code': 'VARCHAR(20)',
            'name': 'VARCHAR(50)',
            'start_date': 'DATE',
            'end_date': 'DATE',
            'ann_date': 'DATE',
            'change_reason': 'VARCHAR(200)'
        }
        return type_mapping.get(column_name, 'TEXT')


# 快捷函数，用于导入指定股票的曾用名数据
async def import_stock_namechange(db, ts_code: str) -> int:
    """
    导入指定股票的曾用名数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        
    返回:
        导入的记录数
    """
    service = NameChangeService(db)
    count = await service.import_namechange_data(ts_code=ts_code)
    print(f"成功导入 {count} 条 {ts_code} 的曾用名记录")
    return count


# 快捷函数，用于导入指定日期范围内的曾用名数据
async def import_namechange_by_date(db, 
                                 start_date: Union[str, datetime.date], 
                                 end_date: Union[str, datetime.date]) -> int:
    """
    导入指定日期范围内的曾用名数据
    
    参数:
        db: 数据库连接对象
        start_date: 起始日期
        end_date: 结束日期
        
    返回:
        导入的记录数
    """
    service = NameChangeService(db)
    count = await service.import_namechange_data(start_date=start_date, end_date=end_date)
    print(f"成功导入 {count} 条曾用名记录")
    return count


# 辅助函数，用于获取股票在某个日期的名称
async def get_stock_name_at_date(db, ts_code: str, date: Optional[datetime.date] = None) -> Optional[str]:
    """
    获取股票在特定日期的名称
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        date: 日期，默认为当天
        
    返回:
        股票名称，如果未找到则返回None
    """
    from app.db.crud.stock_crud.stock_basic.namechange_crud import NameChangeCRUD
    
    crud = NameChangeCRUD(db)
    name = await crud.get_current_name(ts_code, date)
    
    if name is None:
        # 如果在namechange表中未找到，尝试从stock_basic表获取当前名称
        try:
            from app.db.crud.stock_crud.stock_basic.stock_basic_crud import StockBasicCRUD
            
            stock_crud = StockBasicCRUD(db)
            stock = await stock_crud.get_stock_by_ts_code(ts_code)
            if stock:
                name = stock.name
        except Exception as e:
            print(f"获取股票基本信息失败: {str(e)}")
    
    return name