import pandas as pd
import re
from typing import List, Optional, Dict, Any
from app.data.db_modules.macroeconomics_modules.cn.cn_m import CnMData
from app.external.tushare_api.macroeconomics_api import get_cn_m


class CnMService:
    """中国货币供应量数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_m_data(self, m: Optional[str] = None,
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None,
                            fields: Optional[str] = None,
                            batch_size: int = 100) -> int:
        """
        从Tushare获取中国货币供应量数据并高效导入数据库
        
        参数:
            m: 可选，指定月份(如202301)，支持多个月份同时输入，逗号分隔
            start_date: 可选，开始月份
            end_date: 可选，结束月份
            fields: 可选，指定输出字段
            batch_size: 批量处理的记录数，默认100条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_cn_m(m=m, start_date=start_date, end_date=end_date, fields=fields)
        
        if df_result is None or df_result.empty:
            if m:
                print(f"未找到中国货币供应量数据: m={m}")
            else:
                print(f"未找到中国货币供应量数据: start_date={start_date}, end_date={end_date}")
            return 0
        
        # 确保所有必要的列都存在
        required_columns = ['month', 'm0', 'm0_yoy', 'm0_mom', 
                           'm1', 'm1_yoy', 'm1_mom', 
                           'm2', 'm2_yoy', 'm2_mom']
        for col in required_columns:
            if col not in df_result.columns:
                df_result[col] = None
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 分批处理
        batches = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为CnMData对象
                m_data_list = []
                for record in batch:
                    try:
                        m_data = CnMData(**record)
                        m_data_list.append(m_data)
                    except Exception as e:
                        print(f"创建CnMData对象失败 {record.get('month', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if m_data_list:
                    inserted = await self.batch_upsert_m(m_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_m(self, m_list: List[CnMData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            m_list: 要插入或更新的货币供应量数据列表
            
        返回:
            处理的记录数
        """
        if not m_list:
            return 0
        
        # 获取字段列表
        columns = list(m_list[0].model_dump().keys())
        
        # 准备数据
        records = []
        for m_data in m_list:
            m_dict = m_data.model_dump()
            # 正确处理None值
            record = [m_dict[col] for col in columns]
            records.append(record)
        
        # 使用COPY命令批量导入数据
        async with self.db.pool.acquire() as conn:
            try:
                # 开始事务
                async with conn.transaction():
                    # 创建临时表，结构与目标表相同
                    await conn.execute('CREATE TEMP TABLE temp_cn_m (LIKE cn_m) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_cn_m', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（除了主键外的所有字段）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col != 'month']
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO cn_m 
                        SELECT * FROM temp_cn_m
                        ON CONFLICT (month) DO UPDATE SET {update_clause}
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
    
    async def analyze_m_trend(self, months: int = 12) -> Dict[str, Any]:
        """
        分析中国货币供应量变化趋势
        
        参数:
            months: 分析的月数
            
        返回:
            包含趋势分析的字典
        """
        # 查询数据
        query = """
            SELECT month, m0, m0_yoy, m0_mom, 
                   m1, m1_yoy, m1_mom,
                   m2, m2_yoy, m2_mom
            FROM cn_m 
            ORDER BY month DESC
            LIMIT $1
        """
        rows = await self.db.fetch(query, months)
        
        if not rows:
            return {
                "success": False,
                "message": f"无法找到最近{months}个月的货币供应量数据"
            }
        
        # 转换为DataFrame进行分析
        df = pd.DataFrame(rows)
        df = df.sort_values(by='month')
        
        # 提取年份和月份
        df['year'] = df['month'].apply(lambda x: x[:4])
        df['month_num'] = df['month'].apply(lambda x: x[4:6])
        
        # 按年份分组计算年度平均增长率
        yearly_avg = df.groupby('year').agg({
            'm0_yoy': 'mean',
            'm1_yoy': 'mean',
            'm2_yoy': 'mean'
        }).reset_index()
        
        # 计算M2/M1比率和M2/M0比率
        if 'm2' in df.columns and 'm1' in df.columns and 'm0' in df.columns:
            df['m2_m1_ratio'] = df['m2'] / df['m1']
            df['m2_m0_ratio'] = df['m2'] / df['m0']
            df['m1_m0_ratio'] = df['m1'] / df['m0']
            
            avg_m2_m1_ratio = df['m2_m1_ratio'].mean()
            avg_m2_m0_ratio = df['m2_m0_ratio'].mean()
            avg_m1_m0_ratio = df['m1_m0_ratio'].mean()
        else:
            avg_m2_m1_ratio = None
            avg_m2_m0_ratio = None
            avg_m1_m0_ratio = None
        
        # 获取最新月份数据
        latest_month = max(df['month'])
        latest_data = df[df['month'] == latest_month].iloc[0].to_dict()
        
        # 计算增长率加速度（二阶导数近似）
        if len(df) >= 3:
            df['m0_yoy_accel'] = df['m0_yoy'].diff().diff()
            df['m1_yoy_accel'] = df['m1_yoy'].diff().diff()
            df['m2_yoy_accel'] = df['m2_yoy'].diff().diff()
            avg_m0_accel = df['m0_yoy_accel'].mean()
            avg_m1_accel = df['m1_yoy_accel'].mean()
            avg_m2_accel = df['m2_yoy_accel'].mean()
        else:
            avg_m0_accel = None
            avg_m1_accel = None
            avg_m2_accel = None
        
        # 将月度数据转换为列表
        monthly_trend = df[['month', 'm0', 'm0_yoy', 'm1', 'm1_yoy', 'm2', 'm2_yoy']].to_dict('records')
        
        return {
            "success": True,
            "months_analyzed": months,
            "latest_month": latest_month,
            "latest_data": {
                "m0": latest_data.get('m0'),
                "m0_yoy": latest_data.get('m0_yoy'),
                "m1": latest_data.get('m1'),
                "m1_yoy": latest_data.get('m1_yoy'),
                "m2": latest_data.get('m2'),
                "m2_yoy": latest_data.get('m2_yoy')
            },
            "average_growth_rates": {
                "m0_yoy": df['m0_yoy'].mean(),
                "m1_yoy": df['m1_yoy'].mean(),
                "m2_yoy": df['m2_yoy'].mean()
            },
            "average_mom_rates": {
                "m0_mom": df['m0_mom'].mean(),
                "m1_mom": df['m1_mom'].mean(),
                "m2_mom": df['m2_mom'].mean()
            },
            "growth_acceleration": {
                "m0_accel": avg_m0_accel,
                "m1_accel": avg_m1_accel,
                "m2_accel": avg_m2_accel
            },
            "money_supply_ratios": {
                "m2_m1_ratio": avg_m2_m1_ratio,
                "m2_m0_ratio": avg_m2_m0_ratio,
                "m1_m0_ratio": avg_m1_m0_ratio
            },
            "yearly_averages": yearly_avg.to_dict('records'),
            "monthly_trend": monthly_trend
        }
    
    async def calculate_money_multiplier(self, months: int = 12) -> Dict[str, Any]:
        """
        计算货币乘数（M2/M0和M1/M0）
        
        参数:
            months: 分析的月数
            
        返回:
            包含货币乘数分析的字典
        """
        # 查询数据
        query = """
            SELECT month, m0, m1, m2
            FROM cn_m 
            ORDER BY month DESC
            LIMIT $1
        """
        rows = await self.db.fetch(query, months)
        
        if not rows:
            return {
                "success": False,
                "message": f"无法找到最近{months}个月的货币供应量数据"
            }
        
        # 转换为DataFrame进行分析
        df = pd.DataFrame(rows)
        df = df.sort_values(by='month')
        
        # 计算货币乘数
        df['m1_m0_multiplier'] = df['m1'] / df['m0']
        df['m2_m0_multiplier'] = df['m2'] / df['m0']
        
        # 计算乘数变化率
        df['m1_m0_mult_change'] = df['m1_m0_multiplier'].pct_change() * 100
        df['m2_m0_mult_change'] = df['m2_m0_multiplier'].pct_change() * 100
        
        # 获取最新月份数据
        latest_month = max(df['month'])
        latest_data = df[df['month'] == latest_month].iloc[0].to_dict()
        
        # 计算平均值和趋势
        avg_m1_m0_mult = df['m1_m0_multiplier'].mean()
        avg_m2_m0_mult = df['m2_m0_multiplier'].mean()
        
        # 将月度数据转换为列表
        monthly_multipliers = df[['month', 'm1_m0_multiplier', 'm2_m0_multiplier']].to_dict('records')
        
        return {
            "success": True,
            "months_analyzed": months,
            "latest_month": latest_month,
            "latest_multipliers": {
                "m1_m0_multiplier": latest_data.get('m1_m0_multiplier'),
                "m2_m0_multiplier": latest_data.get('m2_m0_multiplier')
            },
            "average_multipliers": {
                "avg_m1_m0_multiplier": avg_m1_m0_mult,
                "avg_m2_m0_multiplier": avg_m2_m0_mult
            },
            "monthly_trend": monthly_multipliers
        }


# 快捷函数，用于导入货币供应量数据
async def import_m(db, m: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    导入中国货币供应量数据
    
    参数:
        db: 数据库连接对象
        m: 可选，指定月份，支持多个月份同时输入，逗号分隔
        start_date: 可选，开始月份
        end_date: 可选，结束月份
        
    返回:
        导入的记录数
    """
    service = CnMService(db)
    count = await service.import_m_data(m=m, start_date=start_date, end_date=end_date)
    print(f"成功导入 {count} 条中国货币供应量记录")
    return count


# 快捷函数，用于导入所有货币供应量数据
async def import_all_m(db, batch_size: int = 100):
    """
    导入所有中国货币供应量数据
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理的记录数，默认100条
        
    返回:
        导入的记录数
    """
    service = CnMService(db)
    count = await service.import_m_data(batch_size=batch_size)
    print(f"成功导入 {count} 条中国货币供应量记录")
    return count

# 快捷函数，用于分析货币供应量趋势
async def analyze_m_trend(db, months: int = 12) -> Dict[str, Any]:
    """
    分析中国货币供应量趋势
    
    参数:
        db: 数据库连接对象
        months: 分析的月数
        
    返回:
        包含趋势分析的字典
    """
    service = CnMService(db)
    result = await service.analyze_m_trend(months=months)
    return result

