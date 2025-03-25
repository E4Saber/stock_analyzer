import pandas as pd
from typing import List, Dict, Any, Optional
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators
from app.external.tushare_api.stock_info_api import get_bak_basic
from app.data.db_modules.stock_modules.stock_basic.bak_basic import StockBakBasicData


class StockBakBasicService:
    """股票历史列表数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_bak_basic_data(self, trade_date: Optional[str] = None, 
                                    ts_code: Optional[str] = None,
                                    batch_size: int = 1000) -> int:
        """
        从Tushare获取指定交易日或指定股票的历史列表数据并高效导入数据库
        
        参数:
            trade_date: 可选，交易日期，格式YYYYMMDD
            ts_code: 可选，TS代码
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 至少需要提供一个参数
        if not trade_date and not ts_code:
            print("必须提供至少一个参数: trade_date 或 ts_code")
            return 0
            
        # 从Tushare获取数据
        df_result = get_bak_basic(trade_date=trade_date, ts_code=ts_code)
        
        if df_result is None or df_result.empty:
            query_params = []
            if trade_date:
                query_params.append(f"交易日 {trade_date}")
            if ts_code:
                query_params.append(f"TS代码 {ts_code}")
            
            print(f"未找到符合条件的股票历史列表数据: {', '.join(query_params)}")
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
            
            # 确保trade_date字段存在且格式正确
            if 'trade_date' not in record or not record['trade_date']:
                if trade_date:
                    record['trade_date'] = trade_date
                else:
                    print(f"跳过缺少trade_date字段的记录: {record}")
                    continue
                
            # 处理日期字段
            for date_field in ['trade_date', 'list_date']:
                if date_field in record:
                    record[date_field] = DateValidators.to_date(record[date_field])
            
            # 处理数值字段
            for numeric_field in ['pe', 'float_share', 'total_share', 'total_assets', 
                                 'liquid_assets', 'fixed_assets', 'reserved', 
                                 'reserved_pershare', 'eps', 'bvps', 'pb', 'undp', 
                                 'per_undp', 'rev_yoy', 'profit_yoy', 'gpr', 'npr']:
                if numeric_field in record:
                    record[numeric_field] = NumericValidators.to_decimal(record[numeric_field])
            
            # 处理整数字段
            if 'holder_num' in record:
                if record['holder_num'] is None or (isinstance(record['holder_num'], float) and 
                                                 (pd.isna(record['holder_num']) or 
                                                  pd.isinf(record['holder_num']))):
                    record['holder_num'] = None
                else:
                    try:
                        record['holder_num'] = int(record['holder_num'])
                    except (ValueError, TypeError):
                        record['holder_num'] = None
            
            valid_records.append(record)
        
        # 分批处理
        batches = [valid_records[i:i + batch_size] for i in range(0, len(valid_records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为StockBakBasicData对象
                bak_basic_list = []
                for record in batch:
                    try:
                        bak_basic = StockBakBasicData(**record)
                        bak_basic_list.append(bak_basic)
                    except Exception as e:
                        print(f"创建StockBakBasicData对象失败 {record.get('ts_code', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if bak_basic_list:
                    inserted = await self.batch_upsert_bak_basic(bak_basic_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_bak_basic(self, bak_basic_list: List[StockBakBasicData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            bak_basic_list: 要插入或更新的股票历史列表数据列表
            
        返回:
            处理的记录数
        """
        if not bak_basic_list:
            return 0
        
        # 获取字段列表
        columns = list(bak_basic_list[0].model_dump().keys())
        
        # 准备数据
        records = []
        for bak_basic in bak_basic_list:
            bak_basic_dict = bak_basic.model_dump()
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = bak_basic_dict[col]
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
                    await conn.execute('CREATE TEMP TABLE temp_bak_basic (LIKE bak_basic) ON COMMIT DROP')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_bak_basic', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（除了主键外的所有字段）
                    update_fields = [col for col in columns if col not in ['trade_date', 'ts_code']]
                    update_sets = [f"{field} = EXCLUDED.{field}" for field in update_fields]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO bak_basic
                        SELECT * FROM temp_bak_basic
                        ON CONFLICT (trade_date, ts_code) DO UPDATE SET {update_clause}
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
                
    async def get_market_overview(self, trade_date: str) -> Dict[str, Any]:
        """
        获取指定交易日的市场概览数据
        
        参数:
            trade_date: 交易日期，格式YYYYMMDD
            
        返回:
            包含市场概览信息的字典
        """
        query = """
            SELECT 
                COUNT(*) as total_stocks,
                AVG(pe) as avg_pe,
                AVG(pb) as avg_pb,
                SUM(total_share) as total_market_share,
                SUM(float_share) as total_float_share,
                COUNT(DISTINCT industry) as industry_count,
                COUNT(DISTINCT area) as area_count
            FROM bak_basic
            WHERE trade_date = $1
        """
        
        async with self.db.pool.acquire() as conn:
            row = await conn.fetchrow(query,  DateValidators.to_date(trade_date))
            if row:
                # 将数值结果转换为字典并格式化
                result = dict(row)
                # 确保小数位数合理
                for key in ['avg_pe', 'avg_pb']:
                    if result[key] is not None:
                        result[key] = round(result[key], 2)
                
                # 添加日期
                result['trade_date'] = trade_date
                
                return result
            
            return {
                'trade_date': trade_date,
                'total_stocks': 0,
                'avg_pe': None,
                'avg_pb': None,
                'total_market_share': None,
                'total_float_share': None,
                'industry_count': 0,
                'area_count': 0
            }
    
    async def get_industry_statistics(self, trade_date: str) -> List[Dict[str, Any]]:
        """
        获取指定交易日的行业统计数据
        
        参数:
            trade_date: 交易日期，格式YYYY-MM-DD
            
        返回:
            行业统计信息列表
        """
        query = """
            SELECT 
                industry,
                COUNT(*) as stock_count,
                AVG(pe) as avg_pe,
                AVG(pb) as avg_pb,
                SUM(total_share) as total_share,
                SUM(float_share) as float_share,
                AVG(eps) as avg_eps,
                AVG(gpr) as avg_gpr,
                AVG(npr) as avg_npr
            FROM bak_basic
            WHERE trade_date = $1 AND industry IS NOT NULL
            GROUP BY industry
            ORDER BY stock_count DESC
        """
        
        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch(query, trade_date)
            results = []
            
            for row in rows:
                industry_data = dict(row)
                # 格式化数值
                for key in ['avg_pe', 'avg_pb', 'avg_eps', 'avg_gpr', 'avg_npr']:
                    if industry_data[key] is not None:
                        industry_data[key] = round(industry_data[key], 2)
                
                # 添加日期
                industry_data['trade_date'] = trade_date
                results.append(industry_data)
            
            return results


# 快捷函数，用于导入指定交易日的股票历史列表数据
async def import_bak_basic(db, trade_date: str, batch_size: int = 1000):
    """
    导入指定交易日的股票历史列表数据
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期，格式YYYYMMDD
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StockBakBasicService(db)
    count = await service.import_bak_basic_data(trade_date=trade_date, batch_size=batch_size)
    
    # 格式化日期显示
    formatted_date = trade_date
    try:
        date_obj = DateValidators.to_date(trade_date)
        if date_obj:
            formatted_date = date_obj.strftime('%Y-%m-%d')
    except:
        pass
        
    print(f"成功导入 {count} 条股票历史列表记录 (交易日: {formatted_date})")
    return count


# 快捷函数，用于导入特定股票的历史列表数据
async def import_stock_bak_data(db, ts_code: str, batch_size: int = 1000):
    """
    导入特定股票的历史列表数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StockBakBasicService(db)
    count = await service.import_bak_basic_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条 {ts_code} 的历史列表记录")
    return count


# 快捷函数，用于导入一段时间内的股票历史列表数据
async def import_bak_basic_range(db, start_date: str, end_date: str, batch_size: int = 1000):
    """
    导入一段时间内的股票历史列表数据
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期，格式YYYYMMDD
        end_date: 结束日期，格式YYYYMMDD
        batch_size: 批量处理大小
        
    返回:
        总导入的记录数
    """
    from app.utils.date_utils import get_trade_dates  # 假设有获取交易日的工具函数
    
    # 获取指定时间范围内的所有交易日
    trade_dates = get_trade_dates(start_date, end_date)
    
    service = StockBakBasicService(db)
    total_count = 0
    
    for trade_date in trade_dates:
        count = await service.import_bak_basic_data(trade_date=trade_date, batch_size=batch_size)
        total_count += count
        
        # 格式化日期显示
        formatted_date = trade_date
        try:
            date_obj = DateValidators.to_date(trade_date)
            if date_obj:
                formatted_date = date_obj.strftime('%Y-%m-%d')
        except:
            pass
            
        print(f"成功导入 {count} 条股票历史列表记录 (交易日: {formatted_date})")
    
    print(f"总共导入 {total_count} 条股票历史列表记录")
    return total_count


# 快捷函数，用于获取市场概览
async def get_market_overview(db, trade_date: str):
    """
    获取市场概览数据
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期，格式YYYY-MM-DD
        
    返回:
        包含市场概览信息的字典
    """
    service = StockBakBasicService(db)
    overview = await service.get_market_overview(trade_date)
    
    print(f"市场概览 ({overview['trade_date']}):")
    print(f"股票总数: {overview['total_stocks']}")
    print(f"平均市盈率: {overview['avg_pe']}")
    print(f"平均市净率: {overview['avg_pb']}")
    print(f"总股本: {overview['total_market_share']} 亿股")
    print(f"流通股本: {overview['total_float_share']} 亿股")
    print(f"行业数量: {overview['industry_count']}")
    print(f"地区数量: {overview['area_count']}")
    
    return overview