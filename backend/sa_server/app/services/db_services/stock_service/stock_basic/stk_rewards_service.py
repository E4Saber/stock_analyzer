import math
import pandas as pd
from typing import List, Optional
from decimal import Decimal, DecimalException
from app.external.tushare_api.stock_info_api import get_stk_rewards
from app.data.db_modules.stock_modules.stock_basic.stk_rewards import StockRewardData

class StockRewardService:
    """股票管理层薪酬和持股数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_reward_data(self, ts_code: str, end_date: Optional[str] = None, batch_size: int = 1000) -> int:
        """
        从Tushare获取股票管理层薪酬和持股数据并高效导入数据库
        
        参数:
            ts_code: 必填，指定要导入的股票代码
            end_date: 可选，截止日期
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 参数验证
        if not ts_code:
            print("ts_code参数为必填项")
            return 0
            
        # 从Tushare获取数据
        df_result = get_stk_rewards(ts_code=ts_code, end_date=end_date)
        
        if df_result is None or df_result.empty:
            query_params = [f"ts_code={ts_code}"]
            if end_date:
                query_params.append(f"end_date={end_date}")
                
            params_str = ", ".join(query_params)
            print(f"未找到股票管理层薪酬和持股数据: {params_str}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 定义必填字段及默认值
        required_fields = {
            'ts_code': ts_code,
            'name': ''
        }
        
        # 处理数据并确保所有必填字段都有值
        valid_records = []
        for record in records:
            for field, default_value in required_fields.items():
                if field not in record or record[field] is None or (isinstance(record[field], str) and record[field] == ''):
                    record[field] = default_value
            
            # 确保股票代码存在
            record['ts_code'] = ts_code
            
            # 确保数值字段为有效的数字类型
            for field in ['reward', 'hold_vol']:
                if field in record and record[field] is not None:
                    # 处理 NaN 和 Infinity 值
                    if isinstance(record[field], float) and (math.isnan(record[field]) or math.isinf(record[field])):
                        record[field] = None
                        continue
                        
                    # 尝试转换为 Decimal
                    try:
                        decimal_value = Decimal(str(record[field]))
                        # 再次检查是否为有限值
                        if decimal_value.is_nan() or decimal_value.is_infinite():
                            record[field] = None
                        else:
                            record[field] = decimal_value
                    except (ValueError, TypeError, DecimalException):
                        record[field] = None
            
            valid_records.append(record)
        
        # 分批处理
        batches = [valid_records[i:i + batch_size] for i in range(0, len(valid_records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为StockRewardData对象
                reward_data_list = []
                for record in batch:
                    try:
                        reward_data = StockRewardData(**record)
                        reward_data_list.append(reward_data)
                    except Exception as e:
                        print(f"创建StockRewardData对象失败 {record.get('name', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if reward_data_list:
                    inserted = await self.batch_upsert_rewards(reward_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_rewards(self, reward_list: List[StockRewardData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            reward_list: 要插入或更新的薪酬和持股数据列表
            
        返回:
            处理的记录数
        """
        if not reward_list:
            return 0
        
        # 获取字段列表（排除id字段，因为它是自动生成的）
        columns = [col for col in list(reward_list[0].model_dump().keys()) if col != 'id']
        
        # 准备数据
        records = []
        for reward in reward_list:
            reward_dict = reward.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = reward_dict[col]
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
                    await conn.execute('CREATE TEMP TABLE temp_stk_rewards (LIKE stk_rewards) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_stk_rewards', records=records, columns=columns)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    # 注意: stk_rewards表使用ts_code, name, end_date作为唯一约束
                    result = await conn.execute('''
                        INSERT INTO stk_rewards (
                            ts_code, ann_date, end_date, name, title, reward, hold_vol
                        )
                        SELECT 
                            ts_code, ann_date, end_date, name, title, reward, hold_vol
                        FROM temp_stk_rewards
                        ON CONFLICT (ts_code, name, end_date) DO UPDATE SET
                            ann_date = EXCLUDED.ann_date,
                            title = EXCLUDED.title,
                            reward = EXCLUDED.reward,
                            hold_vol = EXCLUDED.hold_vol
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
                
    async def get_annual_reward_summary(self, ts_code: str, year: int) -> dict:
        """
        获取指定股票在特定年份的薪酬统计摘要
        
        参数:
            ts_code: 股票代码
            year: 年份
            
        返回:
            包含统计信息的字典
        """
        query = """
            SELECT 
                COUNT(*) as total_managers,
                SUM(reward) as total_reward,
                AVG(reward) as avg_reward,
                MAX(reward) as max_reward,
                MIN(reward) as min_reward
            FROM stk_rewards
            WHERE ts_code = $1 AND EXTRACT(YEAR FROM end_date) = $2
        """
        
        async with self.db.pool.acquire() as conn:
            row = await conn.fetchrow(query, ts_code, year)
            if row:
                return dict(row)
            return {
                'total_managers': 0,
                'total_reward': Decimal('0'),
                'avg_reward': Decimal('0'),
                'max_reward': Decimal('0'),
                'min_reward': Decimal('0')
            }


# 快捷函数，用于导入指定股票的薪酬和持股数据
async def import_stock_rewards(db, ts_code: str, batch_size: int = 1000):
    """
    导入指定股票的管理层薪酬和持股数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StockRewardService(db)
    count = await service.import_reward_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条薪酬和持股记录 (股票代码: {ts_code})")
    return count


# 快捷函数，用于按指定截止日期导入特定股票的薪酬和持股数据
async def import_stock_rewards_by_date(db, ts_code: str, end_date: str, batch_size: int = 1000):
    """
    按指定截止日期导入特定股票的管理层薪酬和持股数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        end_date: 截止日期
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StockRewardService(db)
    count = await service.import_reward_data(ts_code=ts_code, end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条截止日期为 {end_date} 的薪酬和持股记录 (股票代码: {ts_code})")
    return count


# 快捷函数，用于导入多只股票的薪酬和持股数据
async def import_multiple_stocks_rewards(db, ts_codes: List[str], end_date: Optional[str] = None, batch_size: int = 1000):
    """
    批量导入多只股票的管理层薪酬和持股数据
    
    参数:
        db: 数据库连接对象
        ts_codes: 股票TS代码列表
        end_date: 可选，截止日期
        batch_size: 批量处理大小
        
    返回:
        总导入的记录数
    """
    service = StockRewardService(db)
    total_count = 0
    
    for ts_code in ts_codes:
        count = await service.import_reward_data(ts_code=ts_code, end_date=end_date, batch_size=batch_size)
        total_count += count
        print(f"成功导入 {count} 条薪酬和持股记录 (股票代码: {ts_code})")
    
    date_info = f"，截止日期: {end_date}" if end_date else ""
    print(f"总共导入 {total_count} 条薪酬和持股记录{date_info}")
    return total_count