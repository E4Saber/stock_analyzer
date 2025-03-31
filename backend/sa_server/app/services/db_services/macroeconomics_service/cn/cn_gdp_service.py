import pandas as pd
import re
from typing import List, Optional, Dict, Any
from app.data.db_modules.macroeconomics_modules.cn.cn_gdp import CnGdpData
from app.external.tushare_api.macroeconomics_api import get_cn_gdp


class CnGdpService:
    """中国GDP数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_gdp_data(self, q: Optional[str] = None,
                              start_q: Optional[str] = None,
                              end_q: Optional[str] = None,
                              fields: Optional[str] = None,
                              batch_size: int = 100) -> int:
        """
        从Tushare获取中国GDP数据并高效导入数据库
        
        参数:
            q: 可选，指定季度(如2023Q1)
            start_q: 可选，开始季度
            end_q: 可选，结束季度
            fields: 可选，指定输出字段
            batch_size: 批量处理的记录数，默认100条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_cn_gdp(q=q, start_q=start_q, end_q=end_q, fields=fields)
        
        if df_result is None or df_result.empty:
            if q:
                print(f"未找到中国GDP数据: q={q}")
            else:
                print(f"未找到中国GDP数据: start_q={start_q}, end_q={end_q}")
            return 0
        
        # 确保所有必要的列都存在
        required_columns = ['quarter', 'gdp', 'gdp_yoy', 'pi', 'pi_yoy', 'si', 'si_yoy', 'ti', 'ti_yoy']
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
                # 将批次数据转换为CnGdpData对象
                gdp_data_list = []
                for record in batch:
                    try:
                        gdp_data = CnGdpData(**record)
                        gdp_data_list.append(gdp_data)
                    except Exception as e:
                        print(f"创建CnGdpData对象失败 {record.get('quarter', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if gdp_data_list:
                    inserted = await self.batch_upsert_gdp(gdp_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_gdp(self, gdp_list: List[CnGdpData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            gdp_list: 要插入或更新的GDP数据列表
            
        返回:
            处理的记录数
        """
        if not gdp_list:
            return 0
        
        # 获取字段列表
        columns = list(gdp_list[0].model_dump().keys())
        
        # 准备数据
        records = []
        for gdp in gdp_list:
            gdp_dict = gdp.model_dump()
            # 正确处理None值
            record = [gdp_dict[col] for col in columns]
            records.append(record)
        
        # 使用COPY命令批量导入数据
        async with self.db.pool.acquire() as conn:
            try:
                # 开始事务
                async with conn.transaction():
                    # 创建临时表，结构与目标表相同
                    await conn.execute('CREATE TEMP TABLE temp_cn_gdp (LIKE cn_gdp) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_cn_gdp', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（除了主键外的所有字段）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col != 'quarter']
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO cn_gdp 
                        SELECT * FROM temp_cn_gdp
                        ON CONFLICT (quarter) DO UPDATE SET {update_clause}
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
    
    async def analyze_gdp_trend(self, years: int = 5) -> Dict[str, Any]:
        """
        分析中国GDP增长趋势
        
        参数:
            years: 分析的年数
            
        返回:
            包含趋势分析的字典
        """
        # 查询数据
        query = """
            SELECT quarter, gdp, gdp_yoy, pi, si, ti
            FROM cn_gdp 
            ORDER BY quarter DESC
            LIMIT $1
        """
        rows = await self.db.fetch(query, years * 4)  # 4 quarters per year
        
        if not rows:
            return {
                "success": False,
                "message": f"无法找到最近{years}年的GDP数据"
            }
        
        # 转换为DataFrame进行分析
        df = pd.DataFrame(rows)
        df = df.sort_values(by='quarter')
        
        # 提取年份并分组
        df['year'] = df['quarter'].apply(lambda x: x.split('Q')[0])
        yearly_data = df.groupby('year').agg({
            'gdp': 'last',     # 取每年最后一个季度的累计值
            'gdp_yoy': 'mean', # 计算年平均增长率
            'pi': 'last',
            'si': 'last',
            'ti': 'last'
        }).reset_index()
        
        # 计算产业结构
        yearly_data['pi_ratio'] = (yearly_data['pi'] / yearly_data['gdp'] * 100).round(2)
        yearly_data['si_ratio'] = (yearly_data['si'] / yearly_data['gdp'] * 100).round(2)
        yearly_data['ti_ratio'] = (yearly_data['ti'] / yearly_data['gdp'] * 100).round(2)
        
        # 计算近几年的平均增长率
        avg_growth = df['gdp_yoy'].mean()
        
        # 将年度数据转换为列表
        yearly_trend = yearly_data.to_dict('records')
        
        # 获取最新季度数据
        latest_quarter = max(df['quarter'])
        latest_data = df[df['quarter'] == latest_quarter].iloc[0].to_dict()
        
        return {
            "success": True,
            "years_analyzed": years,
            "latest_quarter": latest_quarter,
            "latest_gdp": latest_data.get('gdp'),
            "latest_growth_rate": latest_data.get('gdp_yoy'),
            "avg_growth_rate": avg_growth,
            "yearly_trend": yearly_trend,
            "industry_structure": {
                "latest_year": yearly_trend[-1]['year'] if yearly_trend else None,
                "primary_industry": yearly_trend[-1]['pi_ratio'] if yearly_trend else None,
                "secondary_industry": yearly_trend[-1]['si_ratio'] if yearly_trend else None,
                "tertiary_industry": yearly_trend[-1]['ti_ratio'] if yearly_trend else None
            },
            "quarterly_data": df[['quarter', 'gdp', 'gdp_yoy']].to_dict('records')
        }


# 快捷函数，用于导入GDP数据
async def import_gdp(db, q: Optional[str] = None, start_q: Optional[str] = None, end_q: Optional[str] = None):
    """
    导入中国GDP数据
    
    参数:
        db: 数据库连接对象
        q: 可选，指定季度
        start_q: 可选，开始季度
        end_q: 可选，结束季度
        
    返回:
        导入的记录数
    """
    service = CnGdpService(db)
    count = await service.import_gdp_data(q=q, start_q=start_q, end_q=end_q)
    print(f"成功导入 {count} 条中国GDP记录")
    return count


# 快捷函数，用于导入所有GDP数据
async def import_all_gdp(db, batch_size: int = 100):
    """
    导入所有可用的中国GDP数据
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = CnGdpService(db)
    count = await service.import_gdp_data(batch_size=batch_size)
    print(f"成功导入 {count} 条中国GDP记录")
    return count


# 快捷函数，用于导入特定年份的GDP数据
async def import_gdp_by_year(db, year: int):
    """
    导入特定年份的GDP数据
    
    参数:
        db: 数据库连接对象
        year: 年份，如2023
        
    返回:
        导入的记录数
    """
    start_q = f"{year}Q1"
    end_q = f"{year}Q4"
    
    service = CnGdpService(db)
    count = await service.import_gdp_data(start_q=start_q, end_q=end_q)
    print(f"成功导入 {count} 条{year}年的GDP记录")
    return count


# 快捷函数，用于导入特定季度的GDP数据
async def import_gdp_by_quarter(db, quarter: str):
    """
    导入特定季度的GDP数据
    
    参数:
        db: 数据库连接对象
        quarter: 季度，如2023Q1
        
    返回:
        导入的记录数
    """
    # 验证季度格式
    pattern = r"^\d{4}Q[1-4]$"
    if not re.match(pattern, quarter):
        print(f"无效的季度格式: {quarter}，正确格式应为'YYYYQN'，如'2023Q1'")
        return 0
    
    service = CnGdpService(db)
    count = await service.import_gdp_data(q=quarter)
    print(f"成功导入 {count} 条{quarter}季度的GDP记录")
    return count


# 快捷函数，用于导入最近几年的GDP数据
async def import_recent_gdp(db, years: int = 5):
    """
    导入最近几年的GDP数据
    
    参数:
        db: 数据库连接对象
        years: 年数
        
    返回:
        导入的记录数
    """
    # 计算开始季度（假设当前是2023年）
    import datetime
    current_year = datetime.datetime.now().year
    start_year = current_year - years
    start_q = f"{start_year}Q1"
    
    service = CnGdpService(db)
    count = await service.import_gdp_data(start_q=start_q)
    print(f"成功导入 {count} 条最近{years}年的GDP记录")
    return count


# 快捷函数，用于分析GDP趋势
async def analyze_gdp(db, years: int = 5):
    """
    分析中国GDP趋势
    
    参数:
        db: 数据库连接对象
        years: 分析的年数
        
    返回:
        分析结果
    """
    service = CnGdpService(db)
    result = await service.analyze_gdp_trend(years=years)
    
    if result["success"]:
        print(f"中国GDP分析结果:")
        print(f"- 最新季度: {result['latest_quarter']}")
        print(f"- 最新GDP: {result['latest_gdp']:.2f}亿元")
        print(f"- 最新增长率: {result['latest_growth_rate']:.2f}%")
        print(f"- {years}年平均增长率: {result['avg_growth_rate']:.2f}%")
        print(f"- 最新产业结构比例(%): 第一产业 {result['industry_structure']['primary_industry']}, "
              f"第二产业 {result['industry_structure']['secondary_industry']}, "
              f"第三产业 {result['industry_structure']['tertiary_industry']}")
    else:
        print(result["message"])
    
    return result


# 快捷函数，用于导入并分析GDP数据
async def import_and_analyze_gdp(db, years: int = 5):
    """
    导入并分析GDP数据
    
    参数:
        db: 数据库连接对象
        years: 分析的年数
        
    返回:
        包含导入数量和分析结果的字典
    """
    # 首先导入数据
    import_count = await import_recent_gdp(db, years)
    
    # 然后进行分析
    analysis = await analyze_gdp(db, years)
    
    return {
        "import_count": import_count,
        "analysis": analysis
    }