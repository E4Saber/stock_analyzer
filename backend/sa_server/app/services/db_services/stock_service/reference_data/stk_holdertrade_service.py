import pandas as pd
from decimal import Decimal
from typing import List, Optional, Dict, Any
from app.external.tushare_api.stock.reference_data_api import get_stk_holdertrade
from app.data.db_modules.stock_modules.reference_data.stk_holdertrade import StkHoldertradeData

class StkHoldertradeService:
    """股东增减持数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_stk_holdertrade_data(self, ts_code: Optional[str] = None, 
                                       ann_date: Optional[str] = None,
                                       start_date: Optional[str] = None, 
                                       end_date: Optional[str] = None,
                                       trade_type: Optional[str] = None,
                                       holder_type: Optional[str] = None,
                                       batch_size: int = 1000) -> int:
        """
        从Tushare获取股东增减持数据并高效导入数据库
        
        参数:
            ts_code: 股票代码
            ann_date: 公告日期（YYYYMMDD格式）
            start_date: 公告开始日期，格式YYYYMMDD
            end_date: 公告结束日期，格式YYYYMMDD
            trade_type: 交易类型IN增持DE减持
            holder_type: 股东类型C公司P个人G高管
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_stk_holdertrade(ts_code=ts_code, ann_date=ann_date, 
                                      start_date=start_date, end_date=end_date,
                                      trade_type=trade_type, holder_type=holder_type)
        
        if df_result is None or df_result.empty:
            print(f"未找到股东增减持数据: ts_code={ts_code}, ann_date={ann_date}, trade_type={trade_type}, holder_type={holder_type}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 定义必填字段及默认值
        required_fields = {
            'ts_code': '',
            'holder_name': '',
            'ann_date': None,
        }
        
        # 处理数据并确保所有必填字段都有值
        valid_records = []
        for record in records:
            # 确保必填字段存在且有值
            for field, default_value in required_fields.items():
                if field not in record or record[field] is None or (isinstance(record[field], str) and record[field] == ''):
                    record[field] = default_value
            
            # 如果缺少关键字段，跳过该记录
            if record['ts_code'] == '' or record['holder_name'] == '' or record['ann_date'] is None:
                continue
            
            # 处理日期格式，确保是YYYYMMDD格式
            date_fields = ['ann_date', 'begin_date', 'close_date']
            for date_field in date_fields:
                if date_field in record and record[date_field] is not None:
                    # 如果是pandas Timestamp对象，转换为YYYYMMDD格式字符串
                    if hasattr(record[date_field], 'strftime'):
                        record[date_field] = record[date_field].strftime('%Y%m%d')
                    # 如果已经是字符串但带有连字符（如"2023-12-31"），转换为YYYYMMDD
                    elif isinstance(record[date_field], str) and '-' in record[date_field]:
                        date_parts = record[date_field].split('-')
                        if len(date_parts) == 3:
                            record[date_field] = ''.join(date_parts)
                
            valid_records.append(record)
        
        # 分批处理
        batches = [valid_records[i:i + batch_size] for i in range(0, len(valid_records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为StkHoldertradeData对象
                holder_data_list = []
                for record in batch:
                    try:
                        # 处理数字字段，确保它们是Decimal类型
                        for key, value in record.items():
                            if isinstance(value, (float, int)) and key not in ['id']:
                                record[key] = Decimal(str(value))
                        
                        holder_data = StkHoldertradeData(**record)
                        holder_data_list.append(holder_data)
                    except Exception as e:
                        print(f"创建StkHoldertradeData对象失败 {record.get('ts_code', '未知')}, {record.get('ann_date', '未知')}, {record.get('holder_name', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if holder_data_list:
                    inserted = await self.batch_upsert_stk_holdertrade(holder_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条股东增减持记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_stk_holdertrade(self, holders_list: List[StkHoldertradeData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            holders_list: 要插入或更新的股东增减持数据列表
            
        返回:
            处理的记录数
        """
        if not holders_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = holders_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 使用字典来存储记录，如果有重复键，保留最新记录
        unique_records = {}
        
        for holder in holders_list:
            # 创建唯一键
            key = (holder.ts_code, str(holder.ann_date), holder.holder_name, holder.in_de or '')
            unique_records[key] = holder
        
        # 提取最终的唯一记录列表
        unique_holders_list = list(unique_records.values())
        
        # 准备数据
        records = []
        for holder in unique_holders_list:
            holder_dict = holder.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = holder_dict[col]
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
                    # 手动创建临时表，明确指定列类型，不包含id列
                    # 首先获取原表的列信息
                    column_types = await self._get_column_type(conn, 'stk_holdertrade', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_stk_holdertrade (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_stk_holdertrade', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'ann_date', 'holder_name', 'in_de']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO stk_holdertrade ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_stk_holdertrade
                        ON CONFLICT (ts_code, ann_date, holder_name, in_de) DO UPDATE SET {update_clause}
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

    async def _get_column_type(self, conn, table_name, columns):
        """
        获取表中指定列的数据类型
        
        参数:
            conn: 数据库连接
            table_name: 表名
            columns: 列名列表
            
        返回:
            字典，键为列名，值为数据类型
        """
        column_types = {}
        for column in columns:
            # 查询PostgreSQL系统表获取列的数据类型
            data_type = await conn.fetchval("""
                SELECT pg_catalog.format_type(a.atttypid, a.atttypmod)
                FROM pg_catalog.pg_attribute a
                JOIN pg_catalog.pg_class c ON a.attrelid = c.oid
                JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
                WHERE c.relname = $1
                AND a.attname = $2
                AND a.attnum > 0
                AND NOT a.attisdropped
            """, table_name, column)
            
            if data_type:
                column_types[column] = data_type
            else:
                # 如果找不到类型，使用通用类型
                column_types[column] = 'TEXT'
        
        return column_types


# 快捷函数，用于导入特定股票的股东增减持数据
async def import_stock_stk_holdertrade(db, ts_code: str, batch_size: int = 1000):
    """
    导入特定股票的股东增减持数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StkHoldertradeService(db)
    count = await service.import_stk_holdertrade_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条股票 {ts_code} 的股东增减持记录")
    return count


# 快捷函数，用于导入特定公告日期的股东增减持数据
async def import_ann_date_stk_holdertrade(db, ann_date: str, batch_size: int = 1000):
    """
    导入特定公告日期的股东增减持数据
    
    参数:
        db: 数据库连接对象
        ann_date: 公告日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StkHoldertradeService(db)
    count = await service.import_stk_holdertrade_data(ann_date=ann_date, batch_size=batch_size)
    print(f"成功导入 {count} 条公告日期为 {ann_date} 的股东增减持记录")
    return count


# 快捷函数，用于导入特定日期范围的股东增减持数据
async def import_date_range_stk_holdertrade(db, start_date: str, end_date: str, batch_size: int = 1000):
    """
    导入特定日期范围的股东增减持数据
    
    参数:
        db: 数据库连接对象
        start_date: 公告开始日期（YYYYMMDD格式）
        end_date: 公告结束日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StkHoldertradeService(db)
    count = await service.import_stk_holdertrade_data(start_date=start_date, end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条公告日期范围为 {start_date} 至 {end_date} 的股东增减持记录")
    return count


# 快捷函数，用于导入特定交易类型的股东增减持数据
async def import_trade_type_stk_holdertrade(db, trade_type: str, batch_size: int = 1000):
    """
    导入特定交易类型的股东增减持数据
    
    参数:
        db: 数据库连接对象
        trade_type: 交易类型（IN增持、DE减持）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StkHoldertradeService(db)
    count = await service.import_stk_holdertrade_data(trade_type=trade_type, batch_size=batch_size)
    
    trade_type_desc = "增持" if trade_type == "IN" else "减持" if trade_type == "DE" else trade_type
    print(f"成功导入 {count} 条交易类型为 {trade_type_desc} 的股东增减持记录")
    return count


# 快捷函数，用于导入特定股东类型的股东增减持数据
async def import_holder_type_stk_holdertrade(db, holder_type: str, batch_size: int = 1000):
    """
    导入特定股东类型的股东增减持数据
    
    参数:
        db: 数据库连接对象
        holder_type: 股东类型（C公司、P个人、G高管）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = StkHoldertradeService(db)
    count = await service.import_stk_holdertrade_data(holder_type=holder_type, batch_size=batch_size)
    
    holder_type_desc = ""
    if holder_type == "C":
        holder_type_desc = "公司"
    elif holder_type == "P":
        holder_type_desc = "个人"
    elif holder_type == "G":
        holder_type_desc = "高管"
    else:
        holder_type_desc = holder_type
    
    print(f"成功导入 {count} 条股东类型为 {holder_type_desc} 的股东增减持记录")
    return count


# 综合导入函数，支持多种参数组合
async def import_stk_holdertrade_with_params(db, **kwargs):
    """
    根据提供的参数导入股东增减持数据
    
    参数:
        db: 数据库连接对象
        **kwargs: 可包含 ts_code, ann_date, start_date, end_date, trade_type, holder_type, batch_size 等参数
        
    返回:
        导入的记录数
    """
    service = StkHoldertradeService(db)
    batch_size = kwargs.pop('batch_size', 1000)  # 提取并移除batch_size参数
    
    # 构建参数描述
    param_desc = []
    for key, value in kwargs.items():
        if value:
            param_desc.append(f"{key}={value}")
    
    params_info = ", ".join(param_desc) if param_desc else "所有可用参数"
    
    # 导入数据
    count = await service.import_stk_holdertrade_data(batch_size=batch_size, **kwargs)
    print(f"成功导入 {count} 条股东增减持记录 ({params_info})")
    return count


# 导入所有股东增减持数据
async def import_all_stk_holdertrade(db, batch_size: int = 1000):
    """
    导入所有可获取的股东增减持数据
    
    注意: 这可能会请求大量数据，请确保有足够的网络带宽和系统资源。
    根据数据量大小，此操作可能需要较长时间完成。
    
    参数:
        db: 数据库连接对象
        batch_size: 批量处理大小，默认1000条
        
    返回:
        导入的记录总数
    """
    service = StkHoldertradeService(db)
    
    print("开始导入所有股东增减持数据，此操作可能需要较长时间...")
    count = await service.import_stk_holdertrade_data(batch_size=batch_size)
    
    print(f"成功导入所有股东增减持数据，共 {count} 条记录")
    return count


# 动态查询股东增减持数据
async def query_stk_holdertrade_data(db, 
                                  filters: Optional[Dict[str, Any]] = None, 
                                  order_by: Optional[List[str]] = None,
                                  limit: Optional[int] = None,
                                  offset: Optional[int] = None):
    """
    动态查询股东增减持数据，支持任意字段过滤和自定义排序
    
    参数:
        db: 数据库连接对象
        filters: 过滤条件字典，支持以下操作符后缀:
                 - __eq: 等于 (默认)
                 - __ne: 不等于
                 - __gt: 大于
                 - __ge: 大于等于
                 - __lt: 小于
                 - __le: 小于等于
                 - __like: LIKE模糊查询
                 - __ilike: ILIKE不区分大小写模糊查询
                 - __in: IN包含查询
                 例如: {'ts_code__like': '600%', 'change_ratio__gt': 1, 'in_de': 'IN'}
        order_by: 排序字段列表，字段前加"-"表示降序，例如['-ann_date', '-change_vol']
        limit: 最大返回记录数
        offset: 跳过前面的记录数（用于分页）
        
    返回:
        List[StkHoldertradeData]: 符合条件的股东增减持数据列表
    
    示例:
        # 查询某股票的最近增持记录
        data = await query_stk_holdertrade_data(
            db,
            filters={'ts_code': '000001.SZ', 'in_de': 'IN'},
            order_by=['-ann_date'],
            limit=10
        )
        
        # 分页查询大额减持记录
        data = await query_stk_holdertrade_data(
            db,
            filters={'in_de': 'DE', 'change_ratio__gt': 1},
            order_by=['-change_ratio', '-ann_date'],
            limit=20,
            offset=0
        )
    """
    from app.db.crud.stock_crud.reference_data.stk_holdertrade_crud import StkHoldertradeCRUD
    
    crud = StkHoldertradeCRUD(db)
    results = await crud.get_stk_holdertrade(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 分析股东增减持活动
async def analyze_stk_holdertrade_activity(db, ts_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    分析特定股票的股东增减持活动，统计总体增减持变化
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        start_date: 开始日期，格式YYYYMMDD，默认为最近一年
        end_date: 结束日期，格式YYYYMMDD，默认为当前日期
        
    返回:
        Dict: 包含增减持活动的统计和分析数据
    """
    # 构建查询条件
    filters = {'ts_code': ts_code}
    
    if start_date:
        filters['ann_date__ge'] = start_date
    
    if end_date:
        filters['ann_date__le'] = end_date
    
    # 获取增减持数据
    trade_data = await query_stk_holdertrade_data(
        db,
        filters=filters,
        order_by=['-ann_date']
    )
    
    if not trade_data:
        return {"error": f"未找到股票 {ts_code} 的增减持数据"}
    
    # 分开增持和减持记录
    increase_records = [record for record in trade_data if record.in_de == 'IN']
    decrease_records = [record for record in trade_data if record.in_de == 'DE']
    
    # 统计增持数据
    increase_stats = {
        "count": len(increase_records),
        "total_volume": sum(float(r.change_vol) for r in increase_records if r.change_vol is not None),
        "avg_ratio": sum(float(r.change_ratio) for r in increase_records if r.change_ratio is not None) / len(increase_records) if increase_records else 0,
        "max_ratio": max((float(r.change_ratio) for r in increase_records if r.change_ratio is not None), default=0),
        "max_volume": max((float(r.change_vol) for r in increase_records if r.change_vol is not None), default=0),
    }
    
    # 统计减持数据
    decrease_stats = {
        "count": len(decrease_records),
        "total_volume": sum(float(r.change_vol) for r in decrease_records if r.change_vol is not None),
        "avg_ratio": sum(float(r.change_ratio) for r in decrease_records if r.change_ratio is not None) / len(decrease_records) if decrease_records else 0,
        "max_ratio": max((float(r.change_ratio) for r in decrease_records if r.change_ratio is not None), default=0),
        "max_volume": max((float(r.change_vol) for r in decrease_records if r.change_vol is not None), default=0),
    }
    
    # 按股东类型分组统计
    holder_type_stats = {}
    for record in trade_data:
        holder_type = record.holder_type or 'Unknown'
        if holder_type not in holder_type_stats:
            holder_type_stats[holder_type] = {"IN": 0, "DE": 0}
        
        trade_type = record.in_de or 'Unknown'
        holder_type_stats[holder_type][trade_type] += 1
    
    # 按交易时间分析趋势
    trade_data.sort(key=lambda x: x.ann_date if x.ann_date else "")
    
    # 整理结果
    result = {
        "ts_code": ts_code,
        "period_start": start_date,
        "period_end": end_date,
        "total_records": len(trade_data),
        "increase_stats": increase_stats,
        "decrease_stats": decrease_stats,
        "holder_type_stats": holder_type_stats,
        "net_change": increase_stats["total_volume"] - decrease_stats["total_volume"],
        "trend": "净增持" if increase_stats["total_volume"] > decrease_stats["total_volume"] else "净减持",
        "recent_records": [record.model_dump() for record in trade_data[:10]]  # 最近10条记录
    }
    
    return result


# 跟踪特定股东的增减持活动
async def track_holder_trade_activity(db, holder_name: str, limit: int = 100):
    """
    跟踪特定股东的增减持活动
    
    参数:
        db: 数据库连接对象
        holder_name: 股东名称（支持模糊匹配）
        limit: 最大返回记录数
        
    返回:
        List[StkHoldertradeData]: 该股东的增减持记录
    """
    return await query_stk_holdertrade_data(
        db,
        filters={'holder_name__ilike': f'%{holder_name}%'},
        order_by=['-ann_date'],
        limit=limit
    )