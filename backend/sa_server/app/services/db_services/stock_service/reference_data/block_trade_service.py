import pandas as pd
from decimal import Decimal
from typing import List, Optional, Dict, Any
from app.external.tushare_api.stock.reference_data_api import get_block_trade
from app.data.db_modules.stock_modules.reference_data.block_trade import BlockTradeData

class BlockTradeService:
    """大宗交易数据导入服务，使用PostgreSQL COPY命令高效导入数据"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_block_trade_data(self, ts_code: Optional[str] = None, 
                                   trade_date: Optional[str] = None,
                                   start_date: Optional[str] = None, 
                                   end_date: Optional[str] = None,
                                   batch_size: int = 1000) -> int:
        """
        从Tushare获取大宗交易数据并高效导入数据库
        
        参数:
            ts_code: 股票代码
            trade_date: 交易日期（YYYYMMDD格式）
            start_date: 开始日期，格式YYYYMMDD
            end_date: 结束日期，格式YYYYMMDD
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 从Tushare获取数据
        df_result = get_block_trade(ts_code=ts_code, trade_date=trade_date,
                                 start_date=start_date, end_date=end_date)
        
        if df_result is None or df_result.empty:
            print(f"未找到大宗交易数据: ts_code={ts_code}, trade_date={trade_date}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 定义必填字段及默认值
        required_fields = {
            'ts_code': '',
            'trade_date': None
        }
        
        # 处理数据并确保所有必填字段都有值
        valid_records = []
        for record in records:
            # 确保必填字段存在且有值
            for field, default_value in required_fields.items():
                if field not in record or record[field] is None or (isinstance(record[field], str) and record[field] == ''):
                    record[field] = default_value
            
            # 如果缺少关键字段，跳过该记录
            if record['ts_code'] == '' or record['trade_date'] is None:
                continue
            
            # 处理日期格式，确保是YYYYMMDD格式
            if 'trade_date' in record and record['trade_date'] is not None:
                # 如果是pandas Timestamp对象，转换为YYYYMMDD格式字符串
                if hasattr(record['trade_date'], 'strftime'):
                    record['trade_date'] = record['trade_date'].strftime('%Y%m%d')
                # 如果已经是字符串但带有连字符（如"2023-12-31"），转换为YYYYMMDD
                elif isinstance(record['trade_date'], str) and '-' in record['trade_date']:
                    date_parts = record['trade_date'].split('-')
                    if len(date_parts) == 3:
                        record['trade_date'] = ''.join(date_parts)
                
            valid_records.append(record)
        
        # 分批处理
        batches = [valid_records[i:i + batch_size] for i in range(0, len(valid_records), batch_size)]
        total_count = 0
        
        for batch in batches:
            try:
                # 将批次数据转换为BlockTradeData对象
                block_trade_data_list = []
                for record in batch:
                    try:
                        # 处理数字字段，确保它们是Decimal类型
                        for key, value in record.items():
                            if isinstance(value, (float, int)) and key not in ['id']:
                                record[key] = Decimal(str(value))
                        
                        block_trade_data = BlockTradeData(**record)
                        block_trade_data_list.append(block_trade_data)
                    except Exception as e:
                        print(f"创建BlockTradeData对象失败 {record.get('ts_code', '未知')}, {record.get('trade_date', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if block_trade_data_list:
                    inserted = await self.batch_upsert_block_trade(block_trade_data_list)
                    total_count += inserted
                    print(f"批次导入成功: {inserted} 条大宗交易记录")
            except Exception as e:
                print(f"批次导入失败: {str(e)}")
        
        return total_count
    
    async def batch_upsert_block_trade(self, block_trade_list: List[BlockTradeData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            block_trade_list: 要插入或更新的大宗交易数据列表
            
        返回:
            处理的记录数
        """
        if not block_trade_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = block_trade_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 使用字典来存储记录，如果有重复键，保留最新记录
        unique_records = {}
        
        for block_trade in block_trade_list:
            # 创建唯一键 (ts_code, trade_date, buyer, seller, price, vol)
            buyer = block_trade.buyer or ''
            seller = block_trade.seller or ''
            price = str(block_trade.price or 0)
            vol = str(block_trade.vol or 0)
            key = (block_trade.ts_code, str(block_trade.trade_date), buyer, seller, price, vol)
            unique_records[key] = block_trade
        
        # 提取最终的唯一记录列表
        unique_block_trade_list = list(unique_records.values())
        
        # 准备数据
        records = []
        for block_trade in unique_block_trade_list:
            block_trade_dict = block_trade.model_dump(exclude={'id'})
            # 正确处理日期类型和None值
            record = []
            for col in columns:
                val = block_trade_dict[col]
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
                    column_types = await self._get_column_type(conn, 'block_trade', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_block_trade (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_block_trade', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'trade_date', 'buyer', 'seller', 'price', 'vol']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO block_trade ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_block_trade
                        ON CONFLICT (ts_code, trade_date, buyer, seller, price, vol) DO UPDATE SET {update_clause}
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


# 快捷函数，用于导入特定股票的大宗交易数据
async def import_stock_block_trade(db, ts_code: str, batch_size: int = 1000):
    """
    导入特定股票的大宗交易数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票TS代码
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = BlockTradeService(db)
    count = await service.import_block_trade_data(ts_code=ts_code, batch_size=batch_size)
    print(f"成功导入 {count} 条股票 {ts_code} 的大宗交易记录")
    return count


# 快捷函数，用于导入特定交易日期的大宗交易数据
async def import_trade_date_block_trade(db, trade_date: str, batch_size: int = 1000):
    """
    导入特定交易日期的大宗交易数据
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = BlockTradeService(db)
    count = await service.import_block_trade_data(trade_date=trade_date, batch_size=batch_size)
    print(f"成功导入 {count} 条交易日期为 {trade_date} 的大宗交易记录")
    return count


# 快捷函数，用于导入特定日期范围的大宗交易数据
async def import_date_range_block_trade(db, start_date: str, end_date: str, batch_size: int = 1000):
    """
    导入特定日期范围的大宗交易数据
    
    参数:
        db: 数据库连接对象
        start_date: 开始日期（YYYYMMDD格式）
        end_date: 结束日期（YYYYMMDD格式）
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = BlockTradeService(db)
    count = await service.import_block_trade_data(start_date=start_date, end_date=end_date, batch_size=batch_size)
    print(f"成功导入 {count} 条日期范围为 {start_date} 至 {end_date} 的大宗交易记录")
    return count


# 综合导入函数，支持多种参数组合
async def import_block_trade_with_params(db, **kwargs):
    """
    根据提供的参数导入大宗交易数据
    
    参数:
        db: 数据库连接对象
        **kwargs: 可包含 ts_code, trade_date, start_date, end_date, batch_size 等参数
        
    返回:
        导入的记录数
    """
    service = BlockTradeService(db)
    batch_size = kwargs.pop('batch_size', 1000)  # 提取并移除batch_size参数
    
    # 构建参数描述
    param_desc = []
    for key, value in kwargs.items():
        if value:
            param_desc.append(f"{key}={value}")
    
    params_info = ", ".join(param_desc) if param_desc else "所有可用参数"
    
    # 导入数据
    count = await service.import_block_trade_data(batch_size=batch_size, **kwargs)
    print(f"成功导入 {count} 条大宗交易记录 ({params_info})")
    return count


# 动态查询大宗交易数据
async def query_block_trade_data(db, 
                            filters: Optional[Dict[str, Any]] = None, 
                            order_by: Optional[List[str]] = None,
                            limit: Optional[int] = None,
                            offset: Optional[int] = None):
    """
    动态查询大宗交易数据，支持任意字段过滤和自定义排序
    
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
                 例如: {'ts_code__like': '600%', 'amount__gt': 10000000}
        order_by: 排序字段列表，字段前加"-"表示降序，例如['-trade_date', 'amount']
        limit: 最大返回记录数
        offset: 跳过前面的记录数（用于分页）
        
    返回:
        List[BlockTradeData]: 符合条件的大宗交易数据列表
    
    示例:
        # 查询某支股票的大宗交易记录
        data = await query_block_trade_data(
            db,
            filters={'ts_code': '000001.SZ'},
            order_by=['-trade_date'],
            limit=10
        )
        
        # 查询大金额交易记录
        data = await query_block_trade_data(
            db,
            filters={'amount__gt': 50000000},
            order_by=['-amount'],
            limit=20,
            offset=0
        )
    """
    from app.db.crud.stock_crud.reference_data.block_trade_crud import BlockTradeCRUD
    
    crud = BlockTradeCRUD(db)
    results = await crud.get_block_trades(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 获取特定营业部参与的大宗交易
async def get_branch_block_trades(db, branch_name: str, as_buyer: bool = True, as_seller: bool = True, limit: int = 100):
    """
    获取特定营业部参与的大宗交易
    
    参数:
        db: 数据库连接对象
        branch_name: 营业部名称（支持模糊匹配）
        as_buyer: 是否查询作为买方的记录
        as_seller: 是否查询作为卖方的记录
        limit: 最大返回记录数
        
    返回:
        Dict: 包含营业部大宗交易记录的字典
    """
    conditions = []
    params = [f"%{branch_name}%"]
    
    if as_buyer and as_seller:
        conditions.append("(buyer ILIKE $1 OR seller ILIKE $1)")
    elif as_buyer:
        conditions.append("buyer ILIKE $1")
    elif as_seller:
        conditions.append("seller ILIKE $1")
    else:
        return {"message": "必须至少选择查询买方或卖方记录", "count": 0}
    
    query = f"""
        SELECT * FROM block_trade
        WHERE {' AND '.join(conditions)}
        ORDER BY trade_date DESC, amount DESC
        LIMIT $2
    """
    
    rows = await db.fetch(query, *params, limit)
    
    if not rows:
        return {
            "branch_name": branch_name,
            "count": 0,
            "message": f"未找到营业部 '{branch_name}' 参与的大宗交易记录"
        }
    
    # 转换为BlockTradeData对象
    block_trades = [BlockTradeData.model_validate(dict(row)) for row in rows]
    
    # 按买卖方向分组
    as_buyer_trades = []
    as_seller_trades = []
    
    for trade in block_trades:
        trade_dict = {
            "ts_code": trade.ts_code,
            "trade_date": trade.trade_date.strftime('%Y-%m-%d'),
            "price": float(trade.price) if trade.price else 0,
            "vol": float(trade.vol) if trade.vol else 0,
            "amount": float(trade.amount) if trade.amount else 0,
            "buyer": trade.buyer,
            "seller": trade.seller
        }
        
        if trade.buyer and branch_name.lower() in trade.buyer.lower():
            as_buyer_trades.append(trade_dict)
        
        if trade.seller and branch_name.lower() in trade.seller.lower():
            as_seller_trades.append(trade_dict)
    
    # 构建结果
    result = {
        "branch_name": branch_name,
        "count": len(block_trades),
        "as_buyer_count": len(as_buyer_trades),
        "as_seller_count": len(as_seller_trades),
        "total_buy_amount": sum(trade["amount"] for trade in as_buyer_trades),
        "total_sell_amount": sum(trade["amount"] for trade in as_seller_trades),
        "as_buyer": as_buyer_trades[:10],  # 仅返回前10条
        "as_seller": as_seller_trades[:10]  # 仅返回前10条
    }
    
    return result


# 获取特定日期的大宗交易统计
async def get_daily_block_trade_stats(db, trade_date: str):
    """
    获取特定日期的大宗交易统计信息
    
    参数:
        db: 数据库连接对象
        trade_date: 交易日期（YYYYMMDD格式）
        
    返回:
        Dict: 包含当日大宗交易统计的字典
    """
    # 处理trade_date格式
    formatted_trade_date = trade_date
    if trade_date and isinstance(trade_date, str):
        if trade_date.isdigit() and len(trade_date) == 8:
            formatted_trade_date = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:8]}"
    
    # 查询当日所有大宗交易
    query = """
        SELECT * FROM block_trade
        WHERE trade_date = $1::date
        ORDER BY amount DESC
    """
    
    rows = await db.fetch(query, formatted_trade_date)
    
    if not rows:
        return {
            "trade_date": trade_date,
            "count": 0,
            "message": f"未找到 {trade_date} 的大宗交易记录"
        }
    
    # 转换为BlockTradeData对象
    block_trades = [BlockTradeData.model_validate(dict(row)) for row in rows]
    
    # 按股票分组
    stock_trades = {}
    for trade in block_trades:
        if trade.ts_code not in stock_trades:
            stock_trades[trade.ts_code] = []
        
        stock_trades[trade.ts_code].append({
            "price": float(trade.price) if trade.price else 0,
            "vol": float(trade.vol) if trade.vol else 0,
            "amount": float(trade.amount) if trade.amount else 0,
            "buyer": trade.buyer,
            "seller": trade.seller
        })
    
    # 计算各股票的交易统计
    stock_stats = []
    for ts_code, trades in stock_trades.items():
        total_vol = sum(trade["vol"] for trade in trades)
        total_amount = sum(trade["amount"] for trade in trades)
        avg_price = total_amount / total_vol if total_vol > 0 else 0
        
        stock_stats.append({
            "ts_code": ts_code,
            "trade_count": len(trades),
            "total_vol": total_vol,
            "total_amount": total_amount,
            "avg_price": avg_price,
            "trades": trades
        })
    
    # 按交易金额排序
    stock_stats.sort(key=lambda x: x["total_amount"], reverse=True)
    
    # 计算总体统计
    total_count = len(block_trades)
    total_vol = sum(float(trade.vol or 0) for trade in block_trades)
    total_amount = sum(float(trade.amount or 0) for trade in block_trades)
    
    # 构建结果
    result = {
        "trade_date": trade_date,
        "count": total_count,
        "total_vol": total_vol,
        "total_amount": total_amount,
        "stock_count": len(stock_stats),
        "by_stock": stock_stats[:10],  # 仅返回前10支股票的统计
        "top_trades": [
            {
                "ts_code": trade.ts_code,
                "price": float(trade.price) if trade.price else 0,
                "vol": float(trade.vol) if trade.vol else 0,
                "amount": float(trade.amount) if trade.amount else 0,
                "buyer": trade.buyer,
                "seller": trade.seller
            }
            for trade in sorted(block_trades, key=lambda x: float(x.amount or 0), reverse=True)[:10]  # 前10大交易
        ]
    }
    
    return result


# 分析大宗交易折价/溢价情况
async def analyze_block_trade_premium(db, ts_code: Optional[str] = None, days: int = 30, limit: int = 100):
    """
    分析大宗交易的溢价率（相对于收盘价）
    
    参数:
        db: 数据库连接对象
        ts_code: 可选的股票代码
        days: 分析的天数
        limit: 最大返回记录数
        
    返回:
        Dict: 包含溢价分析的字典
    """
    # 构建查询条件
    conditions = []
    params = []
    param_idx = 1
    
    if ts_code:
        conditions.append(f"bt.ts_code = ${param_idx}")
        params.append(ts_code)
        param_idx += 1
    
    conditions.append(f"bt.trade_date >= (CURRENT_DATE - ${param_idx}::interval)")
    params.append(f"{days} days")
    param_idx += 1
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    # 查询大宗交易并关联日线行情（假设有daily表存储日线数据）
    # 注意：实际项目中需要根据具体的数据表结构调整此查询
    query = f"""
        SELECT 
            bt.*,
            d.close as daily_close
        FROM 
            block_trade bt
        LEFT JOIN 
            daily d ON bt.ts_code = d.ts_code AND bt.trade_date = d.trade_date
        {where_clause}
        ORDER BY 
            bt.trade_date DESC, bt.amount DESC
        LIMIT ${param_idx}
    """
    
    params.append(limit)
    rows = await db.fetch(query, *params)
    
    if not rows:
        return {
            "count": 0,
            "message": f"未找到符合条件的大宗交易记录"
        }
    
    # 计算溢价率
    premium_data = []
    for row in rows:
        block_trade = BlockTradeData.model_validate(dict(row))
        daily_close = float(row['daily_close']) if row['daily_close'] else None
        
        if block_trade.price and daily_close and daily_close > 0:
            premium_rate = (float(block_trade.price) / daily_close - 1) * 100
            
            premium_data.append({
                "ts_code": block_trade.ts_code,
                "trade_date": block_trade.trade_date.strftime('%Y-%m-%d'),
                "block_price": float(block_trade.price),
                "daily_close": daily_close,
                "premium_rate": premium_rate,
                "vol": float(block_trade.vol) if block_trade.vol else 0,
                "amount": float(block_trade.amount) if block_trade.amount else 0,
                "buyer": block_trade.buyer,
                "seller": block_trade.seller
            })
    
    # 按溢价率分组
    premium_groups = {
        "high_premium": [data for data in premium_data if data["premium_rate"] > 5],
        "premium": [data for data in premium_data if 0 < data["premium_rate"] <= 5],
        "discount": [data for data in premium_data if -5 < data["premium_rate"] <= 0],
        "high_discount": [data for data in premium_data if data["premium_rate"] <= -5]
    }
    
    # 计算统计数据
    stats = {
        "count": len(premium_data),
        "avg_premium_rate": sum(data["premium_rate"] for data in premium_data) / len(premium_data) if premium_data else 0,
        "max_premium_rate": max(data["premium_rate"] for data in premium_data) if premium_data else 0,
        "min_premium_rate": min(data["premium_rate"] for data in premium_data) if premium_data else 0,
        "high_premium_count": len(premium_groups["high_premium"]),
        "premium_count": len(premium_groups["premium"]),
        "discount_count": len(premium_groups["discount"]),
        "high_discount_count": len(premium_groups["high_discount"])
    }
    
    # 构建结果
    result = {
        "analysis_period": f"最近{days}天",
        "stats": stats,
        "high_premium": sorted(premium_groups["high_premium"], key=lambda x: x["premium_rate"], reverse=True)[:5],
        "high_discount": sorted(premium_groups["high_discount"], key=lambda x: x["premium_rate"])[:5]
    }
    
    if ts_code:
        result["ts_code"] = ts_code
        result["premium_data"] = sorted(premium_data, key=lambda x: x["trade_date"], reverse=True)
    
    return result