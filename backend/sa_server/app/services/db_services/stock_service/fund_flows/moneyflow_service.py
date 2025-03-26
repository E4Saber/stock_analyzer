import datetime
import pandas as pd
from typing import List, Optional, Dict, Any
from app.external.tushare_api.fund_flows_api import get_moneyflow
from app.data.db_modules.stock_modules.fund_flows.moneyflow import MoneyflowData


class MoneyflowService:
    """股票资金流向数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_moneyflow_data(self, ts_code: Optional[str] = None, 
                                   trade_date: Optional[str] = None,
                                   start_date: Optional[str] = None, 
                                   end_date: Optional[str] = None,
                                   batch_size: int = 1000) -> int:
        """
        从Tushare获取股票资金流向数据并高效导入数据库
        
        参数:
            ts_code: 可选，指定要导入的股票代码，为None时导入当日所有股票
            trade_date: 可选，交易日期，格式YYYYMMDD
            start_date: 可选，开始日期，格式YYYYMMDD
            end_date: 可选，结束日期，格式YYYYMMDD
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_moneyflow(ts_code=ts_code, trade_date=trade_date, 
                                 start_date=start_date, end_date=end_date)
        
        if df_result is None or df_result.empty:
            print(f"未找到资金流向数据: ts_code={ts_code}, trade_date={trade_date}, start_date={start_date}, end_date={end_date}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 定义必填字段及默认值
        required_fields = {
            'ts_code': '',
            'trade_date': None  # 日期字段为None时会引发错误
        }
        
        # 处理数据并确保所有必填字段都有值
        valid_records = []
        for record in records:
            for field, default_value in required_fields.items():
                if field not in record or record[field] is None or (isinstance(record[field], str) and record[field] == ''):
                    if field == 'trade_date':  # 日期不能为空
                        print(f"跳过无效记录，缺少交易日期: {record.get('ts_code', '未知')}")
                        continue
                    record[field] = default_value
            valid_records.append(record)
        
        # 分批处理
        batches = [valid_records[i:i + batch_size] for i in range(0, len(valid_records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为MoneyflowData对象
                moneyflow_data_list = []
                for record in batch:
                    try:
                        moneyflow_data = MoneyflowData(**record)
                        moneyflow_data_list.append(moneyflow_data)
                    except Exception as e:
                        print(f"创建MoneyflowData对象失败 {record.get('ts_code', '未知')} - {record.get('trade_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if moneyflow_data_list:
                    inserted = await self.batch_upsert_moneyflow(moneyflow_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_moneyflow(self, moneyflow_list: List[MoneyflowData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            moneyflow_list: 要插入或更新的资金流向数据列表
            
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
                    await conn.execute('CREATE TEMP TABLE temp_moneyflow (LIKE moneyflow) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_moneyflow', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（除了主键外的所有字段）
                    non_pk_columns = [col for col in columns if col not in ('ts_code', 'trade_date')]
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in non_pk_columns]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO moneyflow 
                        SELECT * FROM temp_moneyflow
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
    
    async def get_daily_moneyflow_summary(self, trade_date: str) -> Dict[str, Any]:
        """
        获取指定交易日的资金流向市场概况
        
        参数:
            trade_date: 交易日期，格式YYYYMMDD
            
        返回:
            市场资金流向汇总数据
        """
        async with self.db.pool.acquire() as conn:
            # 计算市场整体净流入
            total_net = await conn.fetchrow("""
                SELECT 
                    SUM(net_mf_amount) as total_net_amount,
                    COUNT(*) as total_stocks,
                    SUM(CASE WHEN net_mf_amount > 0 THEN 1 ELSE 0 END) as inflow_stocks,
                    SUM(CASE WHEN net_mf_amount < 0 THEN 1 ELSE 0 END) as outflow_stocks
                FROM moneyflow
                WHERE trade_date = $1
            """, trade_date)
            
            # 计算不同规模订单的净流入
            scale_net = await conn.fetchrow("""
                SELECT 
                    SUM(buy_sm_amount - sell_sm_amount) as small_net,
                    SUM(buy_md_amount - sell_md_amount) as medium_net,
                    SUM(buy_lg_amount - sell_lg_amount) as large_net,
                    SUM(buy_elg_amount - sell_elg_amount) as extra_large_net
                FROM moneyflow
                WHERE trade_date = $1
            """, trade_date)
            
            return {
                "trade_date": trade_date,
                "total_net_amount": total_net["total_net_amount"],
                "total_stocks": total_net["total_stocks"],
                "inflow_stocks": total_net["inflow_stocks"],
                "outflow_stocks": total_net["outflow_stocks"],
                "inflow_ratio": total_net["inflow_stocks"] / total_net["total_stocks"] if total_net["total_stocks"] > 0 else 0,
                "small_net": scale_net["small_net"],
                "medium_net": scale_net["medium_net"],
                "large_net": scale_net["large_net"],
                "extra_large_net": scale_net["extra_large_net"]
            }
    
    async def analyze_sector_moneyflow(self, trade_date: str, industry_field: str = 'industry') -> List[Dict[str, Any]]:
        """
        分析指定交易日各行业板块的资金流向情况
        
        参数:
            trade_date: 交易日期，格式YYYYMMDD
            industry_field: 行业分类字段，默认使用industry
            
        返回:
            各行业资金流向数据列表，按净流入金额排序
        """
        # 解析日期字符串为日期对象
        if isinstance(trade_date, str) and len(trade_date) == 8:
            parsed_date = datetime.date(
                int(trade_date[:4]), 
                int(trade_date[4:6]), 
                int(trade_date[6:8])
            )
        else:
            parsed_date = trade_date
            
        async with self.db.pool.acquire() as conn:
            query = f"""
                SELECT sb.{industry_field} as industry,
                       COUNT(*) as stock_count,
                       SUM(mf.net_mf_amount) as total_net_amount,
                       AVG(mf.net_mf_amount) as avg_net_amount,
                       SUM(CASE WHEN mf.net_mf_amount > 0 THEN 1 ELSE 0 END) as inflow_stocks,
                       SUM(CASE WHEN mf.net_mf_amount < 0 THEN 1 ELSE 0 END) as outflow_stocks,
                       SUM(mf.buy_lg_amount + mf.buy_elg_amount) as large_buy_amount,
                       SUM(mf.sell_lg_amount + mf.sell_elg_amount) as large_sell_amount
                FROM moneyflow mf
                JOIN stock_basic sb ON mf.ts_code = sb.ts_code
                WHERE mf.trade_date = $1
                GROUP BY sb.{industry_field}
                ORDER BY total_net_amount DESC
            """
            
            rows = await conn.fetch(query, parsed_date)
            
            result = []
            for row in rows:
                industry_data = dict(row)
                # 计算大单资金净流入
                industry_data["large_net_amount"] = industry_data["large_buy_amount"] - industry_data["large_sell_amount"]
                # 计算行业内个股净流入比例
                total_stocks = industry_data["stock_count"]
                industry_data["inflow_ratio"] = industry_data["inflow_stocks"] / total_stocks if total_stocks > 0 else 0
                result.append(industry_data)
                
            return result
    
    async def get_stock_moneyflow_trend(self, ts_code: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        获取个股资金流向趋势
        
        参数:
            ts_code: 股票代码
            start_date: 开始日期，格式YYYYMMDD
            end_date: 结束日期，格式YYYYMMDD
            
        返回:
            个股资金流向趋势数据
        """
        # 解析日期字符串为日期对象
        if isinstance(start_date, str) and len(start_date) == 8:
            parsed_start_date = datetime.date(
                int(start_date[:4]), 
                int(start_date[4:6]), 
                int(start_date[6:8])
            )
        else:
            parsed_start_date = start_date
            
        if isinstance(end_date, str) and len(end_date) == 8:
            parsed_end_date = datetime.date(
                int(end_date[:4]), 
                int(end_date[4:6]), 
                int(end_date[6:8])
            )
        else:
            parsed_end_date = end_date
            
        async with self.db.pool.acquire() as conn:
            query = """
                SELECT mf.*, p.close, p.change, p.pct_chg
                FROM moneyflow mf
                LEFT JOIN daily p ON mf.ts_code = p.ts_code AND mf.trade_date = p.trade_date
                WHERE mf.ts_code = $1 
                  AND mf.trade_date BETWEEN $2 AND $3
                ORDER BY mf.trade_date
            """
            
            rows = await conn.fetch(query, ts_code, parsed_start_date, parsed_end_date)
            
            result = []
            for row in rows:
                # 将行转换为字典
                data = dict(row)
                
                # 计算大单净流入和小单净流入
                data["large_net"] = (data["buy_lg_amount"] + data["buy_elg_amount"]) - (data["sell_lg_amount"] + data["sell_elg_amount"])
                data["small_net"] = (data["buy_sm_amount"] + data["buy_md_amount"]) - (data["sell_sm_amount"] + data["sell_md_amount"])
                
                # 根据价格变动和资金流向计算一致性指标
                # 正值表示资金流向与价格变动一致
                if data["pct_chg"] is not None and data["net_mf_amount"] is not None:
                    data["consistency"] = 1 if (data["pct_chg"] > 0 and data["net_mf_amount"] > 0) or \
                                             (data["pct_chg"] < 0 and data["net_mf_amount"] < 0) else 0
                else:
                    data["consistency"] = None
                    
                result.append(data)
                
            return result


# 快捷函数，用于导入特定日期的资金流向数据
async def import_daily_moneyflow(db, trade_date: str, batch_size: int = 1000):
    """
    导入特定交易日的所有股票资金流向数据
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期，格式YYYYMMDD
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = MoneyflowService(db)
    count = await service.import_moneyflow_data(trade_date=trade_date, batch_size=batch_size)
    print(f"成功导入 {count} 条 {trade_date} 交易日资金流向记录")
    return count


# 快捷函数，用于导入特定股票的资金流向数据
async def import_stock_moneyflow(db, ts_code: str, start_date: str, end_date: str):
    """
    导入特定股票在一段时间内的资金流向数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        start_date: 开始日期，格式YYYYMMDD
        end_date: 结束日期，格式YYYYMMDD
        
    返回:
        导入的记录数
    """
    service = MoneyflowService(db)
    count = await service.import_moneyflow_data(ts_code=ts_code, start_date=start_date, end_date=end_date)
    print(f"成功导入 {count} 条 {ts_code} 从 {start_date} 到 {end_date} 的资金流向记录")
    return count


# 快捷函数，用于获取市场资金流向概况
async def get_market_moneyflow_summary(db, trade_date: str):
    """
    获取指定交易日的市场资金流向概况
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期，格式YYYYMMDD
        
    返回:
        市场资金流向概况数据
    """
    service = MoneyflowService(db)
    summary = await service.get_daily_moneyflow_summary(trade_date)
    return summary


# 快捷函数，用于获取行业板块资金流向
async def get_industry_moneyflow(db, trade_date: str):
    """
    获取指定交易日的行业板块资金流向
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期，格式YYYYMMDD
        
    返回:
        行业板块资金流向数据
    """
    service = MoneyflowService(db)
    industry_data = await service.analyze_sector_moneyflow(trade_date)
    return industry_data