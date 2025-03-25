import pandas as pd
from typing import List, Dict, Any
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators
from app.external.tushare_api.stock_info_api import get_new_share
from app.data.db_modules.stock_modules.stock_basic.new_share import NewShareData


class NewShareService:
    """IPO新股数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_new_share_data(self, start_date: str = None, end_date: str = None, batch_size: int = 1000) -> int:
        """
        从Tushare获取IPO新股数据并高效导入数据库
        
        参数:
            start_date: 可选，开始日期，格式YYYYMMDD
            end_date: 可选，结束日期，格式YYYYMMDD
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_new_share(start_date=start_date, end_date=end_date)
        
        if df_result is None or df_result.empty:
            print(f"未找到IPO新股数据: {start_date} 至 {end_date}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 处理数据并确保所有必填字段都有值
        valid_records = []
        for record in records:
            # 检查必填字段
            if not record.get('ts_code') or not record.get('name'):
                print(f"跳过缺少必填字段的记录: {record}")
                continue
            
            # 处理日期字段
            for date_field in ['ipo_date', 'issue_date']:
                if date_field in record:
                    record[date_field] = DateValidators.to_date(record[date_field])
            
            # 处理数值字段
            for numeric_field in ['amount', 'market_amount', 'price', 'pe', 'limit_amount', 'funds', 'ballot']:
                if numeric_field in record:
                    record[numeric_field] = NumericValidators.to_decimal(record[numeric_field])
            
            valid_records.append(record)
        
        # 分批处理
        batches = [valid_records[i:i + batch_size] for i in range(0, len(valid_records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为NewShareData对象
                new_share_list = []
                for record in batch:
                    try:
                        new_share = NewShareData(**record)
                        new_share_list.append(new_share)
                    except Exception as e:
                        print(f"创建NewShareData对象失败 {record.get('ts_code', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if new_share_list:
                    inserted = await self.batch_upsert_new_shares(new_share_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_new_shares(self, new_share_list: List[NewShareData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            new_share_list: 要插入或更新的IPO新股数据列表
            
        返回:
            处理的记录数
        """
        if not new_share_list:
            return 0
        
        # 获取字段列表
        columns = list(new_share_list[0].model_dump().keys())
        
        # 准备数据
        records = []
        for new_share in new_share_list:
            new_share_dict = new_share.model_dump()
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = new_share_dict[col]
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
                    await conn.execute('CREATE TEMP TABLE temp_new_share (LIKE new_share) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_new_share', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（除了主键外的所有字段）
                    update_fields = [col for col in columns if col != 'ts_code']
                    update_sets = [f"{field} = EXCLUDED.{field}" for field in update_fields]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO new_share
                        SELECT * FROM temp_new_share
                        ON CONFLICT (ts_code) DO UPDATE SET {update_clause}
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
                
    async def get_ipo_statistics(self, year: int = None) -> Dict[str, Any]:
        """
        获取IPO统计数据
        
        参数:
            year: 可选，指定年份
            
        返回:
            包含统计信息的字典
        """
        year_condition = ""
        params = []
        
        if year is not None:
            year_condition = "WHERE EXTRACT(YEAR FROM ipo_date) = $1"
            params.append(year)
        
        query = f"""
            SELECT 
                COUNT(*) as total_ipos,
                AVG(price) as avg_price,
                MAX(price) as max_price,
                MIN(price) as min_price,
                AVG(pe) as avg_pe,
                SUM(funds) as total_funds,
                AVG(ballot) as avg_ballot
            FROM new_share
            {year_condition}
        """
        
        async with self.db.pool.acquire() as conn:
            row = await conn.fetchrow(query, *params)
            if row:
                # 将数值结果转换为字典并格式化
                result = dict(row)
                # 确保小数位数合理
                for key in ['avg_price', 'max_price', 'min_price', 'avg_pe']:
                    if result[key] is not None:
                        result[key] = round(result[key], 2)
                
                if result['avg_ballot'] is not None:
                    result['avg_ballot'] = round(result['avg_ballot'] * 100, 4)  # 转换为百分比
                
                if result['total_funds'] is not None:
                    result['total_funds'] = round(result['total_funds'], 2)  # 亿元
                
                return result
            
            return {
                'total_ipos': 0,
                'avg_price': None,
                'max_price': None,
                'min_price': None,
                'avg_pe': None,
                'total_funds': None,
                'avg_ballot': None
            }


# 快捷函数，用于导入指定时间段的IPO新股数据
async def import_new_shares(db, start_date: str = None, end_date: str = None, batch_size: int = 1000):
    """
    导入指定时间段的IPO新股数据
    
    参数:
        db: 数据库连接对象
        start_date: 可选，开始日期，格式YYYYMMDD
        end_date: 可选，结束日期，格式YYYYMMDD
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = NewShareService(db)
    count = await service.import_new_share_data(start_date, end_date, batch_size=batch_size)
    
    date_range = ""
    if start_date and end_date:
        date_range = f"{start_date} 至 {end_date}"
    elif start_date:
        date_range = f"{start_date} 之后"
    elif end_date:
        date_range = f"{end_date} 之前"
    else:
        date_range = "全部"
        
    print(f"成功导入 {count} 条IPO新股记录 ({date_range})")
    return count


# 快捷函数，用于获取年度IPO统计数据
async def get_annual_ipo_stats(db, year: int = None):
    """
    获取年度IPO统计数据
    
    参数:
        db: 数据库连接对象
        year: 可选，指定年份
        
    返回:
        包含统计信息的字典
    """
    service = NewShareService(db)
    stats = await service.get_ipo_statistics(year)
    
    year_str = str(year) if year else "所有"
    print(f"{year_str}年IPO统计:")
    print(f"总数量: {stats['total_ipos']}")
    print(f"平均发行价: {stats['avg_price']} 元")
    print(f"平均市盈率: {stats['avg_pe']}")
    print(f"募集资金总额: {stats['total_funds']} 亿元")
    print(f"平均中签率: {stats['avg_ballot']}%")
    
    return stats