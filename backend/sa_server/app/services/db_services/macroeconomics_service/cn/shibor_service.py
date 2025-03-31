import pandas as pd
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from app.data.db_modules.macroeconomics_modules.cn.shibor import ShiborData
from app.external.tushare_api.macroeconomics_api import get_shibor

class ShiborService:
    """上海银行间同业拆放利率数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_shibor_data(self, date: Optional[str] = None,
                                start_date: Optional[str] = None, 
                                end_date: Optional[str] = None,
                                batch_size: int = 1000) -> int:
        """
        从Tushare获取Shibor数据并高效导入数据库
        
        参数:
            date: 可选，单一日期，格式：YYYYMMDD，指定时将只获取该日数据
            start_date: 可选，开始日期，格式：YYYYMMDD
            end_date: 可选，结束日期，格式：YYYYMMDD，默认为当前日期
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 处理日期参数
        if date:
            # 如果提供了具体日期，则只获取该日的数据
            df_result = get_shibor(date=date)
            print(f"获取单一日期 {date} 的Shibor数据")
        else:
            # 处理日期范围参数
            if end_date is None:
                end_date = datetime.now().strftime('%Y%m%d')
            
            if start_date is None:
                # 默认获取最近30天的数据
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            
            # 从Tushare获取数据
            df_result = get_shibor(start_date=start_date, end_date=end_date)
            print(f"获取从 {start_date} 到 {end_date} 的Shibor数据")
        
        if df_result is None or df_result.empty:
            if date:
                print(f"未找到Shibor数据: date={date}")
            else:
                print(f"未找到Shibor数据: start_date={start_date}, end_date={end_date}")
            return 0
        
        # 确保DataFrame列名与数据库列名匹配
        column_mapping = {
            'date': 'date',
            'on': 'on_rate',  # 隔夜利率
            '1w': 'w1_rate',  # 1周利率
            '2w': 'w2_rate',  # 2周利率
            '1m': 'm1_rate',  # 1个月利率
            '3m': 'm3_rate',  # 3个月利率
            '6m': 'm6_rate',  # 6个月利率
            '9m': 'm9_rate',  # 9个月利率
            '1y': 'y1_rate'   # 1年利率
        }
        
        # 重命名列
        df_result = df_result.rename(columns=column_mapping)
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 分批处理
        batches = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为ShiborData对象
                shibor_data_list = []
                for record in batch:
                    try:
                        shibor_data = ShiborData(**record)
                        shibor_data_list.append(shibor_data)
                    except Exception as e:
                        print(f"创建ShiborData对象失败 {record.get('date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if shibor_data_list:
                    inserted = await self.batch_upsert_shibor(shibor_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_shibor(self, shibor_list: List[ShiborData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            shibor_list: 要插入或更新的Shibor数据列表
            
        返回:
            处理的记录数
        """
        if not shibor_list:
            return 0
        
        # 获取字段列表
        columns = list(shibor_list[0].model_dump().keys())
        
        # 准备数据
        records = []
        for shibor in shibor_list:
            shibor_dict = shibor.model_dump()
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = shibor_dict[col]
                # 对于None值，使用PostgreSQL的NULL而不是空字符串
                record.append(val)
            records.append(record)
        
        # 使用COPY命令批量导入数据
        async with self.db.pool.acquire() as conn:
            try:
                # 开始事务
                async with conn.transaction():
                    # 创建临时表，结构与目标表相同
                    await conn.execute('CREATE TEMP TABLE temp_shibor (LIKE shibor) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_shibor', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（除了主键外的所有字段）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col != 'date']
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO shibor 
                        SELECT * FROM temp_shibor
                        ON CONFLICT (date) DO UPDATE SET {update_clause}
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
    
    async def analyze_shibor_trend(self, rate_type: str = 'on_rate', days: int = 30) -> Dict[str, Any]:
        """
        分析Shibor利率趋势
        
        参数:
            rate_type: 利率类型 (on_rate, w1_rate, w2_rate, m1_rate, m3_rate, m6_rate, m9_rate, y1_rate)
            days: 天数范围
            
        返回:
            包含趋势分析的字典
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # 查询数据
        query = f"""
            SELECT date, {rate_type} as rate
            FROM shibor 
            WHERE date >= $1 AND date <= $2 AND {rate_type} IS NOT NULL
            ORDER BY date
        """
        rows = await self.db.fetch(query, start_date, end_date)
        
        if not rows:
            return {
                "success": False,
                "message": f"无法找到{days}天内的{rate_type}数据"
            }
        
        # 转换为DataFrame进行分析
        df = pd.DataFrame(rows)
        
        # 基本统计
        latest_rate = df['rate'].iloc[-1] if not df.empty else None
        min_rate = df['rate'].min() if not df.empty else None
        max_rate = df['rate'].max() if not df.empty else None
        avg_rate = df['rate'].mean() if not df.empty else None
        
        # 计算变化趋势
        if len(df) >= 2:
            first_rate = df['rate'].iloc[0]
            change = latest_rate - first_rate
            change_pct = (change / first_rate * 100) if first_rate != 0 else 0
        else:
            change = 0
            change_pct = 0
        
        # 简单的趋势判断
        if change > 0:
            trend = "上升"
        elif change < 0:
            trend = "下降"
        else:
            trend = "稳定"
        
        return {
            "success": True,
            "rate_type": rate_type,
            "period_days": days,
            "latest_date": df['date'].iloc[-1].strftime('%Y-%m-%d') if not df.empty else None,
            "latest_rate": latest_rate,
            "min_rate": min_rate,
            "max_rate": max_rate,
            "avg_rate": avg_rate,
            "change": change,
            "change_percentage": change_pct,
            "trend": trend,
            "data_points": len(df)
        }


# 快捷函数，用于导入Shibor数据
async def import_shibor(db, date: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    导入Shibor数据
    
    参数:
        db: 数据库连接对象
        date: 可选，单一日期，格式：YYYYMMDD，指定时将只获取该日数据
        start_date: 可选，开始日期，格式：YYYYMMDD
        end_date: 可选，结束日期，格式：YYYYMMDD，默认为当前日期
        
    返回:
        导入的记录数
    """
    service = ShiborService(db)
    count = await service.import_shibor_data(date=date, start_date=start_date, end_date=end_date)
    print(f"成功导入 {count} 条Shibor记录")
    return count


# 快捷函数，用于导入最近一周的Shibor数据
async def import_recent_shibor(db):
    """
    导入最近一周的Shibor数据
    
    参数:
        db: 数据库连接对象
        
    返回:
        导入的记录数
    """
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
    
    service = ShiborService(db)
    count = await service.import_shibor_data(start_date=start_date, end_date=end_date)
    print(f"成功导入 {count} 条最近一周的Shibor记录")
    return count


# 快捷函数，用于导入单日Shibor数据
async def import_shibor_by_date(db, date_str: str):
    """
    导入指定日期的Shibor数据
    
    参数:
        db: 数据库连接对象
        date_str: 日期字符串，格式：YYYYMMDD
        
    返回:
        导入的记录数
    """
    service = ShiborService(db)
    count = await service.import_shibor_data(date=date_str)
    print(f"成功导入 {date_str} 的Shibor记录")
    return count


# 快捷函数，用于分析Shibor趋势
async def analyze_shibor(db, rate_type: str = 'on_rate', days: int = 30):
    """
    分析Shibor利率趋势
    
    参数:
        db: 数据库连接对象
        rate_type: 利率类型 (on_rate, w1_rate, w2_rate, m1_rate, m3_rate, m6_rate, m9_rate, y1_rate)
        days: 天数范围
        
    返回:
        包含趋势分析的字典
    """
    service = ShiborService(db)
    result = await service.analyze_shibor_trend(rate_type=rate_type, days=days)
    
    if result["success"]:
        print(f"Shibor {rate_type} 分析结果:")
        print(f"- 最新利率({result['latest_date']}): {result['latest_rate']:.4f}%")
        print(f"- {days}天变化: {result['change']:.4f}% ({result['change_percentage']:.2f}%)")
        print(f"- 趋势: {result['trend']}")
        print(f"- 区间: {result['min_rate']:.4f}% - {result['max_rate']:.4f}%")
        print(f"- 平均值: {result['avg_rate']:.4f}%")
    else:
        print(result["message"])
    
    return result


# 以下是参考stock_basic_service添加的额外便捷函数

# 导入所有可用的Shibor数据（默认最近一年）
async def import_all_shibor(db, batch_size: int = 1000):
    """
    导入最近一年所有的Shibor数据
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    # 设置时间范围为一年
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
    
    service = ShiborService(db)
    count = await service.import_shibor_data(start_date=start_date, end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条Shibor记录")
    return count


# 导入特定期限的Shibor数据并分析
async def import_and_analyze_shibor(db, rate_type: str = 'on_rate', days: int = 90):
    """
    导入并分析特定期限的Shibor数据
    
    参数:
        db: 数据库连接对象
        rate_type: 利率类型 (on_rate, w1_rate, w2_rate, m1_rate, m3_rate, m6_rate, m9_rate, y1_rate)
        days: 天数范围
        
    返回:
        包含导入数量和分析结果的字典
    """
    # 首先导入数据
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
    
    service = ShiborService(db)
    count = await service.import_shibor_data(start_date=start_date, end_date=end_date)
    print(f"成功导入 {count} 条Shibor记录")
    
    # 然后进行分析
    result = await service.analyze_shibor_trend(rate_type=rate_type, days=days)
    
    # 合并结果
    return {
        "import_count": count,
        "analysis": result
    }


# 导入特定时间段的所有类型Shibor数据
async def import_shibor_by_period(db, period: str = "latest"):
    """
    导入特定时间段的Shibor数据
    
    参数:
        db: 数据库连接对象
        period: 时间段，可选值为 "latest"(最新), "week"(一周), "month"(一个月), 
                "quarter"(一季度), "half_year"(半年), "year"(一年)
        
    返回:
        导入的记录数
    """
    end_date = datetime.now().strftime('%Y%m%d')
    
    # 根据时间段确定开始日期
    period_days = {
        "latest": 1,
        "week": 7,
        "month": 30,
        "quarter": 90,
        "half_year": 180,
        "year": 365
    }
    
    if period == "latest":
        # 最新数据直接使用单日查询
        latest_date = datetime.now().strftime('%Y%m%d')
        service = ShiborService(db)
        count = await service.import_shibor_data(date=latest_date)
        print(f"成功导入 {count} 条最新Shibor记录")
        return count
    elif period in period_days:
        days = period_days[period]
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        service = ShiborService(db)
        count = await service.import_shibor_data(start_date=start_date, end_date=end_date)
        print(f"成功导入 {count} 条{period}时间段的Shibor记录")
        return count
    else:
        print(f"不支持的时间段: {period}")
        return 0


# 导入特定年份的Shibor数据
async def import_shibor_by_year(db, year: int):
    """
    导入特定年份的Shibor数据
    
    参数:
        db: 数据库连接对象
        year: 年份，如2024
        
    返回:
        导入的记录数
    """
    # 设置时间范围为指定年份的全年
    start_date = f"{year}0101"
    end_date = f"{year}1231"
    
    service = ShiborService(db)
    count = await service.import_shibor_data(start_date=start_date, end_date=end_date)
    print(f"成功导入 {count} 条{year}年的Shibor记录")
    return count


# 导入特定月份的Shibor数据
async def import_shibor_by_month(db, year: int, month: int):
    """
    导入特定月份的Shibor数据
    
    参数:
        db: 数据库连接对象
        year: 年份，如2024
        month: 月份，1-12
        
    返回:
        导入的记录数
    """
    # 验证月份
    if month < 1 or month > 12:
        print(f"无效的月份: {month}")
        return 0
        
    # 设置时间范围为指定月份的全月
    start_date = f"{year}{month:02d}01"
    
    # 计算月末日期
    if month == 12:
        end_date = f"{year}{month:02d}31"
    else:
        days_in_month = {
            1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
        }
        # 处理闰年2月
        if month == 2 and ((year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)):
            days_in_month[2] = 29
            
        end_date = f"{year}{month:02d}{days_in_month[month]}"
    
    service = ShiborService(db)
    count = await service.import_shibor_data(start_date=start_date, end_date=end_date)
    print(f"成功导入 {count} 条{year}年{month}月的Shibor记录")
    return count


# 导入特定利率类型的Shibor历史数据
async def import_shibor_by_type(db, rate_type: str, days: int = 365):
    """
    导入特定利率类型的历史Shibor数据并进行分析
    
    参数:
        db: 数据库连接对象
        rate_type: 利率类型，可选值为 "overnight"(隔夜), "1w"(1周), "2w"(2周), 
                "1m"(1个月), "3m"(3个月), "6m"(6个月), "9m"(9个月), "1y"(1年)
        days: 获取历史数据的天数
        
    返回:
        分析结果
    """
    # 利率类型映射
    rate_type_map = {
        "overnight": "on_rate",
        "1w": "w1_rate",
        "2w": "w2_rate",
        "1m": "m1_rate",
        "3m": "m3_rate",
        "6m": "m6_rate",
        "9m": "m9_rate",
        "1y": "y1_rate"
    }
    
    if rate_type not in rate_type_map:
        print(f"不支持的利率类型: {rate_type}")
        print(f"支持的类型有: {', '.join(rate_type_map.keys())}")
        return None
    
    # 导入数据
    result = await import_and_analyze_shibor(db, rate_type=rate_type_map[rate_type], days=days)
    
    return result