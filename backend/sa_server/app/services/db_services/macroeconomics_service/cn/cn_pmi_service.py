import pandas as pd
from typing import List, Optional, Dict, Any
from app.external.tushare_api.macroeconomics_api import get_cn_pmi
from app.data.db_modules.macroeconomics_modules.cn.cn_pmi import CnPmiData


class CnPmiService:
    """中国PMI数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_pmi_data(self, month: Optional[str] = None, 
                              start_month: Optional[str] = None,
                              end_month: Optional[str] = None) -> int:
        """
        从Tushare获取PMI数据并高效导入数据库
        
        参数:
            month: 可选，指定要导入的月份，格式为YYYYMM
            start_month: 可选，起始月份，格式为YYYYMM
            end_month: 可选，结束月份，格式为YYYYMM
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_cn_pmi(m=month, start_m=start_month, end_m=end_month)
        
        if df_result is None or df_result.empty:
            print(f"未找到PMI数据: month={month}, start_month={start_month}, end_month={end_month}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 确保每条记录都有月份字段
        valid_records = []
        for record in records:
            if 'month' in record and record['month']:
                valid_records.append(record)
            else:
                print(f"跳过无效记录: {record}")
        
        # 分批处理
        total_count = 0
        
        try:
            # 将批次数据转换为CnPmiData对象
            pmi_data_list = []
            for record in valid_records:
                try:
                    pmi_data = CnPmiData(**record)
                    pmi_data_list.append(pmi_data)
                except Exception as e:
                    print(f"创建CnPmiData对象失败 {record.get('month', '未知')}: {str(e)}")
            
            # 使用COPY命令批量导入
            if pmi_data_list:
                inserted = await self.batch_upsert_pmi(pmi_data_list)
                total_count += inserted
                print(f"PMI数据导入成功: {inserted} 条记录")
        except Exception as e:
            print(f"PMI数据导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_pmi(self, pmi_list: List[CnPmiData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            pmi_list: 要插入或更新的PMI数据列表
            
        返回:
            处理的记录数
        """
        if not pmi_list:
            return 0
        
        # 获取字段列表
        columns = list(pmi_list[0].model_dump().keys())
        
        # 准备数据
        records = []
        for pmi in pmi_list:
            pmi_dict = pmi.model_dump()
            # 正确处理None值
            record = []
            for col in columns:
                val = pmi_dict[col]
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
                    await conn.execute('CREATE TEMP TABLE temp_cn_pmi (LIKE cn_pmi) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_cn_pmi', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（除了主键外的所有字段）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col != 'month']
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO cn_pmi 
                        SELECT * FROM temp_cn_pmi
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
                print(f"PMI数据批量导入过程中发生错误: {str(e)}")
                raise
    
    async def get_pmi_dataframe(self, 
                                start_month: Optional[str] = None,
                                end_month: Optional[str] = None,
                                fields: Optional[List[str]] = None) -> pd.DataFrame:
        """
        获取PMI数据并转换为pandas DataFrame
        
        参数:
            start_month: 可选，起始月份，格式为YYYYMM
            end_month: 可选，结束月份，格式为YYYYMM
            fields: 可选，需要查询的字段列表
            
        返回:
            包含PMI数据的pandas DataFrame
        """
        async with self.db.pool.acquire() as conn:
            try:
                # 构建字段部分
                fields_str = '*'
                if fields:
                    fields_str = ', '.join(['month'] + fields)
                
                # 构建条件部分
                conditions = []
                params = []
                if start_month:
                    conditions.append(f"month >= ${len(params) + 1}")
                    params.append(start_month)
                if end_month:
                    conditions.append(f"month <= ${len(params) + 1}")
                    params.append(end_month)
                
                where_clause = ""
                if conditions:
                    where_clause = f"WHERE {' AND '.join(conditions)}"
                
                # 执行查询
                query = f"SELECT {fields_str} FROM cn_pmi {where_clause} ORDER BY month"
                rows = await conn.fetch(query, *params)
                
                # 转换为DataFrame
                records = [dict(row) for row in rows]
                return pd.DataFrame(records)
                
            except Exception as e:
                print(f"获取PMI数据发生错误: {str(e)}")
                return pd.DataFrame()
    
    async def analyze_pmi_trend(self, 
                               start_month: Optional[str] = None,
                               end_month: Optional[str] = None,
                               fields: List[str] = ['pmi010000', 'pmi020100', 'pmi030000']) -> Dict[str, Any]:
        """
        分析PMI趋势
        
        参数:
            start_month: 可选，起始月份，格式为YYYYMM
            end_month: 可选，结束月份，格式为YYYYMM
            fields: 需要分析的PMI指标字段列表，默认分析制造业PMI、非制造业PMI和综合PMI
            
        返回:
            包含趋势分析结果的字典
        """
        df = await self.get_pmi_dataframe(start_month, end_month, fields)
        
        if df.empty:
            return {"error": "未找到符合条件的PMI数据"}
        
        # 设置月份为索引
        df.set_index('month', inplace=True)
        
        # 计算基本统计指标
        stats = {}
        for field in fields:
            if field in df.columns:
                stats[field] = {
                    "mean": df[field].mean(),
                    "median": df[field].median(),
                    "max": df[field].max(),
                    "min": df[field].min(),
                    "std": df[field].std(),
                    "latest": df[field].iloc[-1],
                    "latest_month": df.index[-1]
                }
                
                # 计算同比变化
                if len(df) >= 13:
                    stats[field]["yoy_change"] = df[field].iloc[-1] - df[field].iloc[-13]
                    stats[field]["yoy_change_pct"] = (df[field].iloc[-1] / df[field].iloc[-13] - 1) * 100
                
                # 计算环比变化
                if len(df) >= 2:
                    stats[field]["mom_change"] = df[field].iloc[-1] - df[field].iloc[-2]
                    stats[field]["mom_change_pct"] = (df[field].iloc[-1] / df[field].iloc[-2] - 1) * 100
                
                # 计算趋势（近6个月平均值与前6个月平均值比较）
                if len(df) >= 12:
                    recent_6m_avg = df[field].iloc[-6:].mean()
                    prev_6m_avg = df[field].iloc[-12:-6].mean()
                    stats[field]["trend_6m"] = "上升" if recent_6m_avg > prev_6m_avg else "下降"
                    stats[field]["trend_6m_change"] = recent_6m_avg - prev_6m_avg
                    stats[field]["trend_6m_change_pct"] = (recent_6m_avg / prev_6m_avg - 1) * 100
        
        return {
            "stats": stats,
            "periods": len(df),
            "start_month": df.index[0],
            "end_month": df.index[-1]
        }


# 辅助函数，用于导入最新的PMI数据
async def import_latest_pmi(db) -> bool:
    """
    导入最新的PMI数据
    
    参数:
        db: 数据库连接对象
        
    返回:
        是否成功导入
    """
    service = CnPmiService(db)
    count = await service.import_pmi_data()
    return count > 0


# 辅助函数，用于导入指定月份的PMI数据
async def import_pmi_by_month(db, month: str) -> bool:
    """
    导入指定月份的PMI数据
    
    参数:
        db: 数据库连接对象
        month: 月份，格式为YYYYMM
        
    返回:
        是否成功导入
    """
    service = CnPmiService(db)
    count = await service.import_pmi_data(month=month)
    return count > 0


# 辅助函数，用于导入指定时间范围的PMI数据
async def import_pmi_by_range(db, start_month: str, end_month: str) -> int:
    """
    导入指定时间范围的PMI数据
    
    参数:
        db: 数据库连接对象
        start_month: 起始月份，格式为YYYYMM
        end_month: 结束月份，格式为YYYYMM
        
    返回:
        导入的记录数
    """
    service = CnPmiService(db)
    count = await service.import_pmi_data(start_month=start_month, end_month=end_month)
    return count


# 辅助函数，用于分析最近的PMI趋势
async def analyze_recent_pmi_trend(db, months: int = 24) -> Dict[str, Any]:
    """
    分析最近N个月的PMI趋势
    
    参数:
        db: 数据库连接对象
        months: 分析的月份数量，默认24个月
        
    返回:
        趋势分析结果
    """
    service = CnPmiService(db)
    
    # 获取当前日期，并计算N个月前的日期
    import datetime
    today = datetime.date.today()
    
    # 计算结束月份（当前月）
    end_month = today.strftime("%Y%m")
    
    # 计算开始月份（N个月前）
    start_date = today.replace(year=today.year - (months // 12), month=((today.month - (months % 12)) % 12) or 12)
    if start_date.month == 12 and (today.month - (months % 12)) % 12 == 0:
        start_date = start_date.replace(year=start_date.year - 1)
    start_month = start_date.strftime("%Y%m")
    
    return await service.analyze_pmi_trend(start_month=start_month, end_month=end_month)