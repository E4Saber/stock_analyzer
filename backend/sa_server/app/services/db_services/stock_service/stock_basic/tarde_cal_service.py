import datetime
import pandas as pd
from typing import List, Optional, Union
from app.external.tushare_api.stock_info_api import get_trade_cal
from app.data.db_modules.stock_modules.stock_basic.tarde_cal import TradeCalData


class TradeCalService:
    """交易日历数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_trade_cal(self, 
                              exchange: Optional[str] = None,
                              start_date: Optional[Union[str, datetime.date]] = None,
                              end_date: Optional[Union[str, datetime.date]] = None,
                              is_open: Optional[str] = None,
                              batch_size: int = 1000) -> int:
        """
        从Tushare获取交易日历数据并高效导入数据库
        
        参数:
            exchange: 可选，指定要导入的交易所，为None时导入所有交易所
            start_date: 可选，起始日期
            end_date: 可选，结束日期
            is_open: 可选，是否交易 0休市 1交易
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 处理日期参数
        start_date_str = self._format_date(start_date) if start_date else None
        end_date_str = self._format_date(end_date) if end_date else None
        
        # 验证is_open参数
        if is_open is not None and is_open not in ['0', '1']:
            print(f"无效的is_open参数: {is_open}，应为'0'或'1'")
            return 0
            
        # 从Tushare获取数据
        df_result = get_trade_cal(
            exchange=exchange, 
            start_date=start_date_str, 
            end_date=end_date_str,
            is_open=is_open
        )
        
        if df_result is None or df_result.empty:
            query_params = []
            if exchange:
                query_params.append(f"exchange={exchange}")
            if start_date_str:
                query_params.append(f"start_date={start_date_str}")
            if end_date_str:
                query_params.append(f"end_date={end_date_str}")
            if is_open:
                query_params.append(f"is_open={is_open}")
                
            params_str = ", ".join(query_params) if query_params else "所有条件"
            print(f"未找到交易日历数据: {params_str}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 分批处理
        batches = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为TradeCalData对象
                trade_cal_list = []
                for record in batch:
                    try:
                        trade_cal_data = TradeCalData(**record)
                        trade_cal_list.append(trade_cal_data)
                    except Exception as e:
                        print(f"创建TradeCalData对象失败 {record.get('exchange', '未知')}, {record.get('cal_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if trade_cal_list:
                    inserted = await self.batch_upsert_trade_cal(trade_cal_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_trade_cal(self, trade_cal_list: List[TradeCalData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            trade_cal_list: 要插入或更新的交易日历数据列表
            
        返回:
            处理的记录数
        """
        if not trade_cal_list:
            return 0
        
        # 获取字段列表
        columns = list(trade_cal_list[0].model_dump().keys())
        
        # 准备数据
        records = []
        for trade_cal in trade_cal_list:
            trade_cal_dict = trade_cal.model_dump()
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = trade_cal_dict[col]
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
                    await conn.execute('CREATE TEMP TABLE temp_tarde_cal (LIKE tarde_cal) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_tarde_cal', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（除了主键外的所有字段）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ('exchange', 'cal_date')]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO tarde_cal 
                        SELECT * FROM temp_tarde_cal
                        ON CONFLICT (exchange, cal_date) DO UPDATE SET {update_clause}
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


# 快捷函数，用于导入指定交易所的交易日历
async def import_exchange_calendar(db, exchange: str, 
                                start_date: Optional[Union[str, datetime.date]] = None,
                                end_date: Optional[Union[str, datetime.date]] = None,
                                is_open: Optional[str] = None) -> int:
    """
    导入指定交易所的交易日历数据
    
    参数:
        db: 数据库连接对象
        exchange: 交易所代码
        start_date: 可选，起始日期
        end_date: 可选，结束日期
        is_open: 可选，是否交易 0休市 1交易
        
    返回:
        导入的记录数
    """
    service = TradeCalService(db)
    count = await service.import_trade_cal(
        exchange=exchange, 
        start_date=start_date, 
        end_date=end_date,
        is_open=is_open
    )
    
    is_open_str = ""
    if is_open == '1':
        is_open_str = "交易日"
    elif is_open == '0':
        is_open_str = "休市日"
        
    print(f"成功导入 {count} 条 {exchange} 交易所的{is_open_str}交易日历记录")
    return count


# 快捷函数，用于导入最近一年的交易日历
async def import_recent_calendar(db, exchange: Optional[str] = None, is_open: Optional[str] = None) -> int:
    """
    导入最近一年的交易日历数据
    
    参数:
        db: 数据库连接对象
        exchange: 可选，交易所代码，为None时导入所有交易所
        is_open: 可选，是否交易 0休市 1交易
        
    返回:
        导入的记录数
    """
    today = datetime.date.today()
    one_year_ago = datetime.date(today.year - 1, today.month, today.day)
    one_year_ahead = datetime.date(today.year + 1, today.month, today.day)
    
    service = TradeCalService(db)
    count = await service.import_trade_cal(
        exchange=exchange, 
        start_date=one_year_ago,
        end_date=one_year_ahead,
        is_open=is_open
    )
    
    exchange_str = exchange if exchange else "所有"
    is_open_str = ""
    if is_open == '1':
        is_open_str = "交易日"
    elif is_open == '0':
        is_open_str = "休市日"
        
    print(f"成功导入 {count} 条 {exchange_str} 交易所的最近一年{is_open_str}交易日历记录")
    return count


# 快捷函数，用于导入仅交易日的日历数据
async def import_trading_days(db, exchange: str = 'SSE', 
                           start_date: Optional[Union[str, datetime.date]] = None,
                           end_date: Optional[Union[str, datetime.date]] = None) -> int:
    """
    导入仅交易日的日历数据
    
    参数:
        db: 数据库连接对象
        exchange: 交易所代码，默认为上交所(SSE)
        start_date: 可选，起始日期
        end_date: 可选，结束日期
        
    返回:
        导入的记录数
    """
    service = TradeCalService(db)
    count = await service.import_trade_cal(
        exchange=exchange, 
        start_date=start_date,
        end_date=end_date,
        is_open='1'
    )
    
    date_range = ""
    if start_date and end_date:
        date_range = f"从 {start_date} 到 {end_date} 期间"
    elif start_date:
        date_range = f"从 {start_date} 之后"
    elif end_date:
        date_range = f"到 {end_date} 之前"
        
    print(f"成功导入 {count} 条 {exchange} 交易所{date_range}的交易日记录")
    return count


# 快捷函数，用于判断某日是否为交易日
async def is_trading_day(db, date: Union[str, datetime.date], exchange: str = 'SSE') -> bool:
    """
    判断指定日期是否为交易日
    
    参数:
        db: 数据库连接对象
        date: 要检查的日期
        exchange: 交易所代码，默认为上交所(SSE)
        
    返回:
        是否为交易日
    """
    from app.db.crud.stock_crud.stock_basic.tarde_cal_crud import TradeCalCRUD
    
    # 处理日期参数
    if isinstance(date, str):
        try:
            if len(date) == 8 and date.isdigit():
                year = int(date[:4])
                month = int(date[4:6])
                day = int(date[6:8])
                date_obj = datetime.date(year, month, day)
            else:
                date_obj = datetime.date.fromisoformat(date)
        except ValueError:
            raise ValueError(f"无效的日期格式: {date}")
    else:
        date_obj = date
    
    crud = TradeCalCRUD(db)
    return await crud.is_trading_day(exchange, date_obj)