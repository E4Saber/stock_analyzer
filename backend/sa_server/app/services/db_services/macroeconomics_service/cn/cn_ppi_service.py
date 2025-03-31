import pandas as pd
import re
from typing import List, Optional, Dict, Any
from app.data.db_modules.macroeconomics_modules.cn.cn_ppi import CnPpiData
from app.external.tushare_api.macroeconomics_api import get_cn_ppi


class CnPpiService:
    """中国PPI数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_ppi_data(self, m: Optional[str] = None,
                              start_date: Optional[str] = None,
                              end_date: Optional[str] = None,
                              batch_size: int = 100) -> int:
        """
        从Tushare获取中国PPI数据并高效导入数据库
        
        参数:
            m: 可选，指定月份(如202301)，支持多个月份同时输入，逗号分隔
            start_date: 可选，开始月份
            end_date: 可选，结束月份
            batch_size: 批量处理的记录数，默认100条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_cn_ppi(m=m, start_date=start_date, end_date=end_date)
        
        if df_result is None or df_result.empty:
            if m:
                print(f"未找到中国PPI数据: m={m}")
            else:
                print(f"未找到中国PPI数据: start_date={start_date}, end_date={end_date}")
            return 0
        
        # 确保所有必要的列都存在
        required_columns = [
            'month', 'ppi_yoy', 'ppi_mp_yoy', 'ppi_mp_qm_yoy', 'ppi_mp_rm_yoy', 
            'ppi_mp_p_yoy', 'ppi_cg_yoy', 'ppi_cg_f_yoy', 'ppi_cg_c_yoy', 'ppi_cg_adu_yoy', 
            'ppi_cg_dcg_yoy', 'ppi_mom', 'ppi_mp_mom', 'ppi_mp_qm_mom', 'ppi_mp_rm_mom',
            'ppi_mp_p_mom', 'ppi_cg_mom', 'ppi_cg_f_mom', 'ppi_cg_c_mom', 'ppi_cg_adu_mom',
            'ppi_cg_dcg_mom', 'ppi_accu', 'ppi_mp_accu', 'ppi_mp_qm_accu', 'ppi_mp_rm_accu',
            'ppi_mp_p_accu', 'ppi_cg_accu', 'ppi_cg_f_accu', 'ppi_cg_c_accu', 'ppi_cg_adu_accu',
            'ppi_cg_dcg_accu'
        ]
        
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
                # 将批次数据转换为CnPpiData对象
                ppi_data_list = []
                for record in batch:
                    try:
                        ppi_data = CnPpiData(**record)
                        ppi_data_list.append(ppi_data)
                    except Exception as e:
                        print(f"创建CnPpiData对象失败 {record.get('month', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if ppi_data_list:
                    inserted = await self.batch_upsert_ppi(ppi_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_ppi(self, ppi_list: List[CnPpiData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            ppi_list: 要插入或更新的PPI数据列表
            
        返回:
            处理的记录数
        """
        if not ppi_list:
            return 0
        
        # 获取字段列表
        columns = list(ppi_list[0].model_dump().keys())
        
        # 准备数据
        records = []
        for ppi in ppi_list:
            ppi_dict = ppi.model_dump()
            # 正确处理None值
            record = [ppi_dict[col] for col in columns]
            records.append(record)
        
        # 使用COPY命令批量导入数据
        async with self.db.pool.acquire() as conn:
            try:
                # 开始事务
                async with conn.transaction():
                    # 创建临时表，结构与目标表相同
                    await conn.execute('CREATE TEMP TABLE temp_cn_ppi (LIKE cn_ppi) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_cn_ppi', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（除了主键外的所有字段）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col != 'month']
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO cn_ppi 
                        SELECT * FROM temp_cn_ppi
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
    
    async def analyze_ppi_trend(self, months: int = 12) -> Dict[str, Any]:
        """
        分析中国PPI变化趋势
        
        参数:
            months: 分析的月数
            
        返回:
            包含趋势分析的字典
        """
        # 查询数据
        query = """
            SELECT month, ppi_yoy, ppi_mom, ppi_accu, 
                  ppi_mp_yoy, ppi_cg_yoy,
                  ppi_mp_qm_yoy, ppi_mp_rm_yoy, ppi_mp_p_yoy,
                  ppi_cg_f_yoy, ppi_cg_c_yoy
            FROM cn_ppi 
            ORDER BY month DESC
            LIMIT $1
        """
        rows = await self.db.fetch(query, months)
        
        if not rows:
            return {
                "success": False,
                "message": f"无法找到最近{months}个月的PPI数据"
            }
        
        # 转换为DataFrame进行分析
        df = pd.DataFrame(rows)
        df = df.sort_values(by='month')
        
        # 提取年份和月份
        df['year'] = df['month'].apply(lambda x: x[:4])
        df['month_num'] = df['month'].apply(lambda x: x[4:6])
        
        # 按年份分组计算年度平均PPI
        yearly_avg = df.groupby('year').agg({
            'ppi_yoy': 'mean',
            'ppi_mp_yoy': 'mean',
            'ppi_cg_yoy': 'mean'
        }).reset_index()
        
        # 计算生产资料与生活资料PPI差异
        df['mp_cg_diff'] = df['ppi_mp_yoy'] - df['ppi_cg_yoy']
        avg_mp_cg_diff = df['mp_cg_diff'].mean()
        
        # 计算子分类PPI的相对贡献
        # 生产资料子类
        mp_subtypes = ['ppi_mp_qm_yoy', 'ppi_mp_rm_yoy', 'ppi_mp_p_yoy']
        # 生活资料子类
        cg_subtypes = ['ppi_cg_f_yoy', 'ppi_cg_c_yoy']
        
        # 获取最新月份数据
        latest_month = max(df['month'])
        latest_data = df[df['month'] == latest_month].iloc[0].to_dict()
        
        # 计算PPI加速度（二阶导数近似）
        if len(df) >= 3:
            df['ppi_yoy_accel'] = df['ppi_yoy'].diff().diff()
            df['ppi_mom_accel'] = df['ppi_mom'].diff()
            avg_yoy_accel = df['ppi_yoy_accel'].mean()
            avg_mom_accel = df['ppi_mom_accel'].mean()
        else:
            avg_yoy_accel = None
            avg_mom_accel = None
        
        # 将月度数据转换为列表
        monthly_trend = df[['month', 'ppi_yoy', 'ppi_mom', 'ppi_accu']].to_dict('records')
        
        # 计算子分类PPI的平均值
        mp_subtype_avgs = {subtype: df[subtype].mean() for subtype in mp_subtypes if subtype in df.columns}
        cg_subtype_avgs = {subtype: df[subtype].mean() for subtype in cg_subtypes if subtype in df.columns}
        
        return {
            "success": True,
            "months_analyzed": months,
            "latest_month": latest_month,
            "latest_ppi": latest_data.get('ppi_yoy'),
            "latest_ppi_mom": latest_data.get('ppi_mom'),
            "latest_ppi_accu": latest_data.get('ppi_accu'),
            "avg_ppi_yoy": df['ppi_yoy'].mean(),
            "avg_ppi_mom": df['ppi_mom'].mean(),
            "avg_ppi_accu": df['ppi_accu'].mean() if 'ppi_accu' in df.columns else None,
            "avg_yoy_acceleration": avg_yoy_accel,
            "avg_mom_acceleration": avg_mom_accel,
            "production_consumer_comparison": {
                "avg_production_yoy": df['ppi_mp_yoy'].mean(),
                "avg_consumer_yoy": df['ppi_cg_yoy'].mean(),
                "avg_difference": avg_mp_cg_diff
            },
            "production_subtypes": mp_subtype_avgs,
            "consumer_subtypes": cg_subtype_avgs,
            "yearly_averages": yearly_avg.to_dict('records'),
            "monthly_trend": monthly_trend
        }


# 快捷函数，用于导入PPI数据
async def import_ppi(db, m: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    导入中国PPI数据
    
    参数:
        db: 数据库连接对象
        m: 可选，指定月份，支持多个月份同时输入，逗号分隔
        start_date: 可选，开始月份
        end_date: 可选，结束月份
        
    返回:
        导入的记录数
    """
    service = CnPpiService(db)
    count = await service.import_ppi_data(m=m, start_date=start_date, end_date=end_date)
    print(f"成功导入 {count} 条中国PPI记录")
    return count


# 快捷函数，用于导入所有PPI数据
async def import_all_ppi(db, batch_size: int = 100):
    """
    导入所有可用的中国PPI数据
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = CnPpiService(db)
    count = await service.import_ppi_data(batch_size=batch_size)
    print(f"成功导入 {count} 条中国PPI记录")
    return count


# 快捷函数，用于导入特定年份的PPI数据
async def import_ppi_by_year(db, year: int):
    """
    导入特定年份的PPI数据
    
    参数:
        db: 数据库连接对象
        year: 年份，如2023
        
    返回:
        导入的记录数
    """
    start_date = f"{year}01"
    end_date = f"{year}12"
    
    service = CnPpiService(db)
    count = await service.import_ppi_data(start_date=start_date, end_date=end_date)
    print(f"成功导入 {count} 条{year}年的PPI记录")
    return count


# 快捷函数，用于导入特定月份的PPI数据
async def import_ppi_by_month(db, month: str):
    """
    导入特定月份的PPI数据
    
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
    
    service = CnPpiService(db)
    count = await service.import_ppi_data(m=month)
    print(f"成功导入 {count} 条{month}月份的PPI记录")
    return count


# 快捷函数，用于导入最近几个月的PPI数据
async def import_recent_ppi(db, months: int = 12):
    """
    导入最近几个月的PPI数据
    
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
    
    service = CnPpiService(db)
    count = await service.import_ppi_data(start_date=start_date)
    print(f"成功导入 {count} 条最近{months}个月的PPI记录")
    return count


# 快捷函数，用于分析PPI趋势
async def analyze_ppi(db, months: int = 12):
    """
    分析中国PPI趋势
    
    参数:
        db: 数据库连接对象
        months: 分析的月数
        
    返回:
        分析结果
    """
    service = CnPpiService(db)
    result = await service.analyze_ppi_trend(months=months)
    
    if result["success"]:
        print(f"中国PPI分析结果:")
        print(f"- 最新月份: {result['latest_month']}")
        print(f"- 最新同比PPI: {result['latest_ppi']:.2f}%")
        print(f"- 最新环比PPI: {result['latest_ppi_mom']:.2f}%")
        print(f"- {months}个月平均同比PPI: {result['avg_ppi_yoy']:.2f}%")
        print(f"- {months}个月平均环比PPI: {result['avg_ppi_mom']:.2f}%")
        print(f"- 生产资料与生活资料PPI差异: 生产资料 {result['production_consumer_comparison']['avg_production_yoy']:.2f}%, "
              f"生活资料 {result['production_consumer_comparison']['avg_consumer_yoy']:.2f}%, "
              f"差值 {result['production_consumer_comparison']['avg_difference']:.2f}%")
    else:
        print(result["message"])
    
    return result


# 快捷函数，用于导入并分析PPI数据
async def import_and_analyze_ppi(db, months: int = 12):
    """
    导入并分析PPI数据
    
    参数:
        db: 数据库连接对象
        months: 分析的月数
        
    返回:
        包含导入数量和分析结果的字典
    """
    # 首先导入数据
    import_count = await import_recent_ppi(db, months)
    
    # 然后进行分析
    analysis = await analyze_ppi(db, months)
    
    return {
        "import_count": import_count,
        "analysis": analysis
    }