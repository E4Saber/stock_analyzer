import datetime
import pandas as pd
from typing import List, Optional
from app.external.tushare_api.fund_flows_api import get_moneyflow_hsgt
from app.data.db_modules.stock_modules.fund_flows.moneyflow_hsgt import MoneyflowHsgtData

class MoneyflowHsgtService:
    """沪深港通资金流向数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_moneyflow_hsgt_data(self, trade_date: Optional[str] = None,
                                       start_date: Optional[str] = None, 
                                       end_date: Optional[str] = None,
                                       batch_size: int = 1000) -> int:
        """
        从Tushare获取沪深港通资金流向数据并高效导入数据库
        
        参数:
            trade_date: 可选，交易日期 YYYYMMDD格式
            start_date: 可选，开始日期 YYYYMMDD格式
            end_date: 可选，结束日期 YYYYMMDD格式
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_moneyflow_hsgt(trade_date=trade_date, start_date=start_date, end_date=end_date)
        
        if df_result is None or df_result.empty:
            print(f"未找到沪深港通资金流向数据: trade_date={trade_date}, start_date={start_date}, end_date={end_date}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 分批处理
        batches = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为MoneyflowHsgtData对象
                moneyflow_data_list = []
                for record in batch:
                    try:
                        moneyflow_data = MoneyflowHsgtData(**record)
                        moneyflow_data_list.append(moneyflow_data)
                    except Exception as e:
                        print(f"创建MoneyflowHsgtData对象失败 {record.get('trade_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if moneyflow_data_list:
                    inserted = await self.batch_upsert_moneyflow_hsgt(moneyflow_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_moneyflow_hsgt(self, moneyflow_list: List[MoneyflowHsgtData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            moneyflow_list: 要插入或更新的沪深港通资金流向数据列表
            
        返回:
            处理的记录数
        """
        if not moneyflow_list:
            return 0
        
        # 获取字段列表
        columns = list(moneyflow_list[0].model_dump().keys())
        
        # 准备数据
        records = []
        for moneyflow in moneyflow_list:
            moneyflow_dict = moneyflow.model_dump()
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = moneyflow_dict[col]
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
                    await conn.execute('CREATE TEMP TABLE temp_moneyflow_hsgt (LIKE moneyflow_hsgt) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_moneyflow_hsgt', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（除了主键外的所有字段）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col != 'trade_date']
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO moneyflow_hsgt 
                        SELECT * FROM temp_moneyflow_hsgt
                        ON CONFLICT (trade_date) DO UPDATE SET {update_clause}
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


# 快捷函数，用于导入单日的沪深港通资金流向数据
async def import_daily_moneyflow_hsgt(db, trade_date: str):
    """
    导入指定交易日的沪深港通资金流向数据
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期，YYYYMMDD格式
        
    返回:
        导入的记录数
    """
    service = MoneyflowHsgtService(db)
    count = await service.import_moneyflow_hsgt_data(trade_date=trade_date)
    print(f"成功导入 {count} 条 {trade_date} 日沪深港通资金流向记录")
    return count


# 快捷函数，用于导入日期范围内的沪深港通资金流向数据
async def import_date_range_moneyflow_hsgt(db, start_date: str, end_date: str, batch_size: int = 1000):
    """
    导入日期范围内的沪深港通资金流向数据
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期，YYYYMMDD格式
        end_date: 结束日期，YYYYMMDD格式
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = MoneyflowHsgtService(db)
    count = await service.import_moneyflow_hsgt_data(start_date=start_date, end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条 {start_date} 至 {end_date} 期间沪深港通资金流向记录")
    return count


# 快捷函数，用于导入最近n天的沪深港通资金流向数据
async def import_recent_moneyflow_hsgt(db, days: int = 30):
    """
    导入最近n天的沪深港通资金流向数据
    
    参数:
        db: 数据库连接对象
        days: 天数，默认30天
        
    返回:
        导入的记录数
    """
    # 计算开始日期（今天减去days天）
    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=days)).strftime("%Y%m%d")
    end_date = today.strftime("%Y%m%d")
    
    service = MoneyflowHsgtService(db)
    count = await service.import_moneyflow_hsgt_data(start_date=start_date, end_date=end_date)
    print(f"成功导入 {count} 条最近 {days} 天的沪深港通资金流向记录")
    return count


# 分析功能：计算北向资金连续流入天数
async def analyze_north_money_streak(db, end_date: Optional[str] = None, days: int = 30):
    """
    分析指定日期之前的北向资金连续流入/流出天数
    
    参数:
        db: 数据库连接对象
        end_date: 结束日期，YYYYMMDD格式，默认为今天
        days: 分析的天数范围，默认30天
        
    返回:
        (连续天数, 是否为流入)，正数表示连续流入天数，负数表示连续流出天数
    """
    # 如果未指定结束日期，使用今天
    if not end_date:
        end_date = datetime.date.today().strftime("%Y%m%d")
    
    # 解析结束日期
    end_date_obj = datetime.datetime.strptime(end_date, "%Y%m%d").date()
    
    # 计算开始日期
    start_date_obj = end_date_obj - datetime.timedelta(days=days)
    
    # 获取数据
    crud = MoneyflowHsgtCRUD(db)
    records = await crud.get_moneyflow_hsgt_by_date_range(start_date_obj, end_date_obj)
    
    # 按日期降序排序
    records.sort(key=lambda x: x.trade_date, reverse=True)
    
    if not records:
        return 0, False
    
    # 计算连续天数
    streak = 0
    is_inflow = records[0].north_money > 0
    
    for record in records:
        if (is_inflow and record.north_money > 0) or (not is_inflow and record.north_money < 0):
            streak += 1
        else:
            break
    
    return streak * (1 if is_inflow else -1), is_inflow