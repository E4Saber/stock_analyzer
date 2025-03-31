import pandas as pd
import re
from typing import List, Optional, Dict, Any
from app.data.db_modules.macroeconomics_modules.cn.cn_cpi import CnCpiData
from app.external.tushare_api.macroeconomics_api import get_cn_cpi


class CnCpiService:
    """中国CPI数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_cpi_data(self, m: Optional[str] = None,
                              start_date: Optional[str] = None,
                              end_date: Optional[str] = None,
                              batch_size: int = 100) -> int:
        """
        从Tushare获取中国CPI数据并高效导入数据库
        
        参数:
            m: 可选，指定月份(如202301)，支持多个月份同时输入，逗号分隔
            start_date: 可选，开始月份
            end_date: 可选，结束月份
            batch_size: 批量处理的记录数，默认100条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_cn_cpi(m=m, start_date=start_date, end_date=end_date)
        
        if df_result is None or df_result.empty:
            if m:
                print(f"未找到中国CPI数据: m={m}")
            else:
                print(f"未找到中国CPI数据: start_date={start_date}, end_date={end_date}")
            return 0
        
        # 确保所有必要的列都存在
        required_columns = ['month', 'nt_val', 'nt_yoy', 'nt_mom', 'nt_accu', 
                           'town_val', 'town_yoy', 'town_mom', 'town_accu',
                           'cnt_val', 'cnt_yoy', 'cnt_mom', 'cnt_accu']
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
                # 将批次数据转换为CnCpiData对象
                cpi_data_list = []
                for record in batch:
                    try:
                        cpi_data = CnCpiData(**record)
                        cpi_data_list.append(cpi_data)
                    except Exception as e:
                        print(f"创建CnCpiData对象失败 {record.get('month', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if cpi_data_list:
                    inserted = await self.batch_upsert_cpi(cpi_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_cpi(self, cpi_list: List[CnCpiData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            cpi_list: 要插入或更新的CPI数据列表
            
        返回:
            处理的记录数
        """
        if not cpi_list:
            return 0
        
        # 获取字段列表
        columns = list(cpi_list[0].model_dump().keys())
        
        # 准备数据
        records = []
        for cpi in cpi_list:
            cpi_dict = cpi.model_dump()
            # 正确处理None值
            record = [cpi_dict[col] for col in columns]
            records.append(record)
        
        # 使用COPY命令批量导入数据
        async with self.db.pool.acquire() as conn:
            try:
                # 开始事务
                async with conn.transaction():
                    # 创建临时表，结构与目标表相同
                    await conn.execute('CREATE TEMP TABLE temp_cn_cpi (LIKE cn_cpi) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_cn_cpi', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（除了主键外的所有字段）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col != 'month']
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO cn_cpi 
                        SELECT * FROM temp_cn_cpi
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
    
    async def analyze_cpi_trend(self, months: int = 12) -> Dict[str, Any]:
        """
        分析中国CPI变化趋势
        
        参数:
            months: 分析的月数
            
        返回:
            包含趋势分析的字典
        """
        # 查询数据
        query = """
            SELECT month, nt_val, nt_yoy, nt_mom, town_val, town_yoy, cnt_val, cnt_yoy
            FROM cn_cpi 
            ORDER BY month DESC
            LIMIT $1
        """
        rows = await self.db.fetch(query, months)
        
        if not rows:
            return {
                "success": False,
                "message": f"无法找到最近{months}个月的CPI数据"
            }
        
        # 转换为DataFrame进行分析
        df = pd.DataFrame(rows)
        df = df.sort_values(by='month')
        
        # 提取年份和月份
        df['year'] = df['month'].apply(lambda x: x[:4])
        df['month_num'] = df['month'].apply(lambda x: x[4:6])
        
        # 按年份分组计算年度平均CPI
        yearly_avg = df.groupby('year').agg({
            'nt_yoy': 'mean',
            'town_yoy': 'mean',
            'cnt_yoy': 'mean'
        }).reset_index()
        
        # 计算城乡差异
        df['urban_rural_diff'] = df['town_yoy'] - df['cnt_yoy']
        avg_urban_rural_diff = df['urban_rural_diff'].mean()
        
        # 获取最新月份数据
        latest_month = max(df['month'])
        latest_data = df[df['month'] == latest_month].iloc[0].to_dict()
        
        # 计算同比环比加速度（二阶导数近似）
        if len(df) >= 3:
            df['nt_yoy_accel'] = df['nt_yoy'].diff().diff()
            df['nt_mom_accel'] = df['nt_mom'].diff().diff()
            avg_yoy_accel = df['nt_yoy_accel'].mean()
            avg_mom_accel = df['nt_mom_accel'].mean()
        else:
            avg_yoy_accel = None
            avg_mom_accel = None
        
        # 将月度数据转换为列表
        monthly_trend = df[['month', 'nt_val', 'nt_yoy', 'nt_mom']].to_dict('records')
        
        return {
            "success": True,
            "months_analyzed": months,
            "latest_month": latest_month,
            "latest_cpi": latest_data.get('nt_val'),
            "latest_yoy": latest_data.get('nt_yoy'),
            "latest_mom": latest_data.get('nt_mom'),
            "avg_yoy": df['nt_yoy'].mean(),
            "avg_mom": df['nt_mom'].mean(),
            "avg_yoy_acceleration": avg_yoy_accel,
            "avg_mom_acceleration": avg_mom_accel,
            "urban_rural_comparison": {
                "avg_urban_yoy": df['town_yoy'].mean(),
                "avg_rural_yoy": df['cnt_yoy'].mean(),
                "avg_difference": avg_urban_rural_diff
            },
            "yearly_averages": yearly_avg.to_dict('records'),
            "monthly_trend": monthly_trend
        }


# 快捷函数，用于导入CPI数据
async def import_cpi(db, m: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    导入中国CPI数据
    
    参数:
        db: 数据库连接对象
        m: 可选，指定月份，支持多个月份同时输入，逗号分隔
        start_date: 可选，开始月份
        end_date: 可选，结束月份
        
    返回:
        导入的记录数
    """
    service = CnCpiService(db)
    count = await service.import_cpi_data(m=m, start_date=start_date, end_date=end_date)
    print(f"成功导入 {count} 条中国CPI记录")
    return count


# 快捷函数，用于导入所有CPI数据
async def import_all_cpi(db, batch_size: int = 100):
    """
    导入所有可用的中国CPI数据
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = CnCpiService(db)
    count = await service.import_cpi_data(batch_size=batch_size)
    print(f"成功导入 {count} 条中国CPI记录")
    return count


# 快捷函数，用于导入特定年份的CPI数据
async def import_cpi_by_year(db, year: int):
    """
    导入特定年份的CPI数据
    
    参数:
        db: 数据库连接对象
        year: 年份，如2023
        
    返回:
        导入的记录数
    """
    start_date = f"{year}01"
    end_date = f"{year}12"
    
    service = CnCpiService(db)
    count = await service.import_cpi_data(start_date=start_date, end_date=end_date)
    print(f"成功导入 {count} 条{year}年的CPI记录")
    return count


# 快捷函数，用于导入特定月份的CPI数据
async def import_cpi_by_month(db, month: str):
    """
    导入特定月份的CPI数据
    
    参数:
        db: 数据库连接对象
        month: 月份，如202301
        
    返回:
        导入的记录数
    """
    # 验证月份格式
    pattern = r"^\d{6}$"
    if not re.match(pattern, month):
        print(f"无效的月份格式: {month}，正确格式应为'YYYYMM'，如'202301'")
        return 0
    
    service = CnCpiService(db)
    count = await service.import_cpi_data(m=month)
    print(f"成功导入 {count} 条{month}月份的CPI记录")
    return count


# 快捷函数，用于导入最近几个月的CPI数据
async def import_recent_cpi(db, months: int = 12):
    """
    导入最近几个月的CPI数据
    
    参数:
        db: 数据库连接对象
        months: 月数
        
    返回:
        导入的记录数
    """
    # 计算开始月份
    import datetime
    current_date = datetime.datetime.now()
    start_date = (current_date - datetime.timedelta(days=30 * months)).strftime("%Y%m")
    
    service = CnCpiService(db)
    count = await service.import_cpi_data(start_date=start_date)
    print(f"成功导入 {count} 条最近{months}个月的CPI记录")
    return count


# 快捷函数，用于分析CPI趋势
async def analyze_cpi(db, months: int = 12):
    """
    分析中国CPI趋势
    
    参数:
        db: 数据库连接对象
        months: 分析的月数
        
    返回:
        分析结果
    """
    service = CnCpiService(db)
    result = await service.analyze_cpi_trend(months=months)
    
    if result["success"]:
        print(f"中国CPI分析结果:")
        print(f"- 最新月份: {result['latest_month']}")
        print(f"- 最新CPI: {result['latest_cpi']}")
        print(f"- 最新同比: {result['latest_yoy']:.2f}%")
        print(f"- 最新环比: {result['latest_mom']:.2f}%")
        print(f"- {months}个月平均同比增长率: {result['avg_yoy']:.2f}%")
        print(f"- {months}个月平均环比增长率: {result['avg_mom']:.2f}%")
        print(f"- 城乡CPI差异: 城市 {result['urban_rural_comparison']['avg_urban_yoy']:.2f}%, "
              f"农村 {result['urban_rural_comparison']['avg_rural_yoy']:.2f}%, "
              f"差值 {result['urban_rural_comparison']['avg_difference']:.2f}%")
    else:
        print(result["message"])
    
    return result


# 快捷函数，用于获取最新CPI数据
async def get_latest_cpi(db) -> Optional[CnCpiData]:
    """
    获取最新的CPI数据
    
    参数:
        db: 数据库连接对象
        
    返回:
        最新的CPI数据对象
    """
    service = CnCpiService(db)
    latest_cpi = await service.get_latest_cpi()
    
    if latest_cpi:
        print(f"最新CPI数据: {latest_cpi}")
    else:
        print("未找到最新的CPI数据")
    
    return latest_cpi

# 快捷函数，用于获取特定年份的CPI数据
async def get_cpi_by_year(db, year: int) -> List[CnCpiData]:
    """
    获取特定年份的CPI数据
    
    参数:
        db: 数据库连接对象
        year: 年份，如2023
        
    返回:
        特定年份的CPI数据列表
    """
    service = CnCpiService(db)
    cpi_data = await service.get_year_cpi(year=year)
    
    if cpi_data:
        print(f"{year}年CPI数据: {cpi_data}")
    else:
        print(f"未找到{year}年的CPI数据")
    
    return cpi_data

# 快捷函数，用于获取特定月份的CPI数据
async def get_cpi_by_month(db, month: str) -> Optional[CnCpiData]:
    """
    获取特定月份的CPI数据
    
    参数:
        db: 数据库连接对象
        month: 月份，如202301
        
    返回:
        特定月份的CPI数据对象
    """
    # 验证月份格式
    pattern = r"^\d{6}$"
    if not re.match(pattern, month):
        print(f"无效的月份格式: {month}，正确格式应为'YYYYMM'，如'202301'")
        return None
    
    service = CnCpiService(db)
    cpi_data = await service.get_cpi_by_month(month=month)
    
    if cpi_data:
        print(f"{month}月份CPI数据: {cpi_data}")
    else:
        print(f"未找到{month}月份的CPI数据")
    
    return cpi_data

# 快捷函数，用于获取CPI数据范围
async def get_cpi_range(db, start_month: str, end_month: str) -> List[CnCpiData]:
    """
    获取特定月份范围的CPI数据
    
    参数:
        db: 数据库连接对象
        start_month: 开始月份，如202301
        end_month: 结束月份，如202312
        
    返回:
        特定月份范围的CPI数据列表
    """
    service = CnCpiService(db)
    cpi_data = await service.get_cpi_range(start_month=start_month, end_month=end_month)
    
    if cpi_data:
        print(f"{start_month}到{end_month}月份的CPI数据: {cpi_data}")
    else:
        print(f"未找到{start_month}到{end_month}月份的CPI数据")
    
    return cpi_data

