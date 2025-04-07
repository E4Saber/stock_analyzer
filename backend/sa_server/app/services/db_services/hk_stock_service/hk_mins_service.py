import pandas as pd
from typing import List, Optional, Dict, Any
from app.external.tushare_api.hk_stock_api import get_hk_mins
from app.data.db_modules.hk_stock_modules.hk_mins import HkMinsData

class HkMinsService:
    """香港股票分钟行情数据导入服务，实现高效批量导入和数据管理"""
    
    def __init__(self, db):
        """
        初始化服务
        
        参数:
            db: 数据库连接对象，需要支持asyncpg连接池
        """
        self.db = db
    
    async def import_hk_mins_data(self, 
                                ts_code: str, 
                                freq: str,
                                start_date: Optional[str] = None,
                                end_date: Optional[str] = None,
                                batch_size: int = 1000) -> int:
        """
        从Tushare获取香港股票分钟行情数据并高效导入数据库
        
        参数:
            ts_code: 股票代码
            freq: 分钟频度（1min/5min/15min/30min/60min）
            start_date: 开始日期时间 格式：2023-03-13 09:00:00
            end_date: 结束日期时间 格式：2023-03-13 19:00:00
            batch_size: 批量处理的记录数，默认1000条
            
        返回:
            导入的记录数量
        """
        # 构建参数说明用于日志
        params = [f"ts_code={ts_code}", f"freq={freq}"]
        if start_date:
            params.append(f"start_date={start_date}")
        if end_date:
            params.append(f"end_date={end_date}")
        
        param_desc = ", ".join(params)
        print(f"正在获取香港股票分钟行情数据: {param_desc}")
        
        # 从Tushare获取数据
        try:
            df_result = get_hk_mins(
                ts_code=ts_code, 
                freq=freq, 
                start_date=start_date,
                end_date=end_date
            )
            
            if df_result is None or df_result.empty:
                print(f"未找到香港股票分钟行情数据: {param_desc}")
                return 0
                
            print(f"获取到 {len(df_result)} 条香港股票分钟行情数据")
        except Exception as e:
            print(f"获取香港股票分钟行情数据失败: {str(e)}")
            return 0
        
        # 转换为列表并处理可能的NaN值
        records = df_result.replace({pd.NA: None}).to_dict('records')
        
        # 数据预处理和验证
        valid_records = await self._preprocess_records(records, freq)
        
        if not valid_records:
            print("没有有效的香港股票分钟行情数据记录可导入")
            return 0
            
        # 分批处理
        batches = [valid_records[i:i + batch_size] for i in range(0, len(valid_records), batch_size)]
        total_count = 0
        
        for batch_idx, batch in enumerate(batches):
            try:
                # 将批次数据转换为HkMinsData对象
                mins_data_list = []
                for record in batch:
                    try:
                        # 为了确保数据类型正确，显式处理数值字段
                        # 处理浮点数字段
                        float_fields = ['open', 'high', 'low', 'close', 'amount']
                        for field in float_fields:
                            if field in record and record[field] is not None:
                                if isinstance(record[field], str) and record[field].strip() == '':
                                    record[field] = None
                                elif record[field] is not None:
                                    try:
                                        record[field] = float(record[field])
                                    except (ValueError, TypeError):
                                        record[field] = None
                        
                        # 处理整数字段
                        if 'vol' in record and record['vol'] is not None:
                            if isinstance(record['vol'], str) and record['vol'].strip() == '':
                                record['vol'] = None
                            elif record['vol'] is not None:
                                try:
                                    record['vol'] = int(float(record['vol']))
                                except (ValueError, TypeError):
                                    record['vol'] = None
                        
                        # 确保包含频率字段
                        if 'freq' not in record:
                            record['freq'] = freq
                        
                        mins_data = HkMinsData(**record)
                        mins_data_list.append(mins_data)
                    except Exception as e:
                        print(f"创建HkMinsData对象失败 {record.get('ts_code', '未知')}, {record.get('trade_time', '未知')}: {str(e)}")
                
                # 使用COPY命令批量导入
                if mins_data_list:
                    inserted = await self.batch_upsert_hk_mins(mins_data_list)
                    total_count += inserted
                    print(f"批次 {batch_idx + 1}/{len(batches)} 导入成功: {inserted} 条香港股票分钟行情数据")
            except Exception as e:
                print(f"批次 {batch_idx + 1}/{len(batches)} 导入失败: {str(e)}")
        
        print(f"总共成功导入 {total_count} 条香港股票分钟行情数据")
        return total_count
    
    async def _preprocess_records(self, records: List[Dict[str, Any]], freq: str) -> List[Dict[str, Any]]:
        """
        预处理和验证数据记录
        
        参数:
            records: 原始数据记录列表
            freq: 分钟频度
            
        返回:
            处理后的有效记录列表
        """
        # 定义必填字段及默认值
        required_fields = {
            'ts_code': '',
            'trade_time': None,
        }
        
        valid_records = []
        invalid_count = 0
        
        for record in records:
            # 确保必填字段存在且有值
            for field, default_value in required_fields.items():
                if field not in record or record[field] is None or (isinstance(record[field], str) and record[field].strip() == ''):
                    record[field] = default_value
            
            # 如果缺少关键字段，跳过该记录
            if record['ts_code'] == '' or record['trade_time'] is None:
                invalid_count += 1
                continue
            
            # 添加频率字段
            record['freq'] = freq
            
            valid_records.append(record)
        
        if invalid_count > 0:
            print(f"警告: 跳过了 {invalid_count} 条无效记录")
            
        return valid_records
    
    async def batch_upsert_hk_mins(self, mins_list: List[HkMinsData]) -> int:
        """
        使用PostgreSQL的COPY命令进行高效批量插入或更新
        
        参数:
            mins_list: 要插入或更新的香港股票分钟行情数据列表
            
        返回:
            处理的记录数
        """
        if not mins_list:
            return 0
        
        # 获取字段列表，排除id字段
        sample_dict = mins_list[0].model_dump(exclude={'id'})
        columns = list(sample_dict.keys())
        
        # 使用字典来存储记录，如果有重复键，保留最新记录
        unique_records = {}
        
        for mins in mins_list:
            # 创建唯一键 (ts_code, trade_time, freq)
            key = (mins.ts_code, str(mins.trade_time), mins.freq)
            unique_records[key] = mins
        
        # 提取最终的唯一记录列表
        unique_mins_list = list(unique_records.values())
        
        # 准备数据
        records = []
        for mins in unique_mins_list:
            mins_dict = mins.model_dump(exclude={'id'})
            # 正确处理日期时间类型和None值
            record = []
            for col in columns:
                val = mins_dict[col]
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
                    column_types = await self._get_column_type(conn, 'hk_mins', columns)
                    
                    # 构建临时表的列定义
                    column_defs = []
                    for col in columns:
                        col_type = column_types.get(col, 'TEXT')
                        column_defs.append(f"{col} {col_type}")
                    
                    # 创建临时表，显式指定列定义，不包含id列和任何约束
                    await conn.execute(f'''
                        CREATE TEMP TABLE temp_hk_mins (
                            {', '.join(column_defs)}
                        ) ON COMMIT DROP
                    ''')
                    
                    # 使用COPY命令将数据复制到临时表
                    await conn.copy_records_to_table('temp_hk_mins', records=records, columns=columns)
                    
                    # 构建更新语句中的SET部分（排除主键）
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col not in ['ts_code', 'trade_time', 'freq']]
                    update_clause = ', '.join(update_sets)
                    
                    # 从临时表插入到目标表，有冲突则更新
                    result = await conn.execute(f'''
                        INSERT INTO hk_mins ({', '.join(columns)})
                        SELECT {', '.join(columns)} FROM temp_hk_mins
                        ON CONFLICT (ts_code, trade_time, freq) DO UPDATE SET {update_clause}
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


# 快捷函数，用于导入特定股票代码和频率的分钟行情数据
async def import_hk_mins_by_ts_code_and_freq(db, ts_code: str, freq: str, start_date: Optional[str] = None, end_date: Optional[str] = None, batch_size: int = 1000) -> int:
    """
    导入特定股票代码和频率的香港股票分钟行情数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        freq: 分钟频度（1min/5min/15min/30min/60min）
        start_date: 开始日期时间 格式：2023-03-13 09:00:00
        end_date: 结束日期时间 格式：2023-03-13 19:00:00
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    service = HkMinsService(db)
    count = await service.import_hk_mins_data(
        ts_code=ts_code,
        freq=freq,
        start_date=start_date,
        end_date=end_date,
        batch_size=batch_size
    )
    
    date_range = ""
    if start_date and end_date:
        date_range = f"从 {start_date} 到 {end_date} 的"
    elif start_date:
        date_range = f"从 {start_date} 开始的"
    elif end_date:
        date_range = f"截止到 {end_date} 的"
    
    print(f"成功导入 {count} 条{date_range}股票 {ts_code} 的 {freq} 频度分钟行情数据")
    return count


# 快捷函数，用于导入特定股票代码在特定日期的分钟行情数据
async def import_hk_mins_by_date(db, ts_code: str, freq: str, date: str, batch_size: int = 1000) -> int:
    """
    导入特定股票代码在特定日期的香港股票分钟行情数据
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        freq: 分钟频度（1min/5min/15min/30min/60min）
        date: 日期 格式：2023-03-13
        batch_size: 批量处理大小
        
    返回:
        导入的记录数
    """
    # 构建当天的开始和结束时间
    start_date = f"{date} 00:00:00"
    end_date = f"{date} 23:59:59"
    
    service = HkMinsService(db)
    count = await service.import_hk_mins_data(
        ts_code=ts_code,
        freq=freq,
        start_date=start_date,
        end_date=end_date,
        batch_size=batch_size
    )
    
    print(f"成功导入 {count} 条股票 {ts_code} 在 {date} 的 {freq} 频度分钟行情数据")
    return count


# 快捷函数，用于导入多个股票代码的分钟行情数据
async def import_hk_mins_for_multiple_stocks(db, ts_codes: List[str], freq: str, start_date: Optional[str] = None, end_date: Optional[str] = None, batch_size: int = 1000) -> Dict[str, int]:
    """
    导入多个股票代码的香港股票分钟行情数据
    
    参数:
        db: 数据库连接对象
        ts_codes: 股票代码列表
        freq: 分钟频度（1min/5min/15min/30min/60min）
        start_date: 开始日期时间 格式：2023-03-13 09:00:00
        end_date: 结束日期时间 格式：2023-03-13 19:00:00
        batch_size: 批量处理大小
        
    返回:
        Dict[str, int]: 字典，键为股票代码，值为导入的记录数
    """
    result = {}
    
    for ts_code in ts_codes:
        try:
            count = await import_hk_mins_by_ts_code_and_freq(
                db, 
                ts_code=ts_code, 
                freq=freq, 
                start_date=start_date, 
                end_date=end_date, 
                batch_size=batch_size
            )
            result[ts_code] = count
        except Exception as e:
            print(f"导入股票 {ts_code} 的分钟行情数据失败: {str(e)}")
            result[ts_code] = 0
    
    # 计算总导入数量
    total_count = sum(result.values())
    print(f"成功导入 {total_count} 条 {len(ts_codes)} 支股票的 {freq} 频度分钟行情数据")
    
    return result


# 从数据库中查询香港股票分钟行情数据
async def query_hk_mins_data(db, 
                          filters: Optional[Dict[str, Any]] = None, 
                          order_by: Optional[List[str]] = None,
                          limit: Optional[int] = None,
                          offset: Optional[int] = None) -> List[HkMinsData]:
    """
    动态查询香港股票分钟行情数据，支持任意字段过滤和自定义排序
    
    参数:
        db: 数据库连接对象
        filters: 过滤条件字典，支持以下操作符后缀:
                 - __eq: 等于 (默认)
                 - __ne: 不等于
                 - __gt: 大于
                 - __ge: 大于等于
                 - __lt: 小于
                 - __le: 小于等于
                 - __in: IN包含查询
                 例如: {'ts_code': '00700.HK', 'freq': '1min', 'trade_time__ge': '2023-03-13 09:00:00'}
        order_by: 排序字段列表，字段前加"-"表示降序，例如['-trade_time', 'ts_code']
        limit: 最大返回记录数
        offset: 跳过前面的记录数（用于分页）
        
    返回:
        List[HkMinsData]: 符合条件的香港股票分钟行情数据列表
    
    示例:
        # 查询腾讯控股某天的1分钟数据
        data = await query_hk_mins_data(
            db,
            filters={
                'ts_code': '00700.HK', 
                'freq': '1min',
                'trade_time__ge': '2023-03-13 09:00:00',
                'trade_time__le': '2023-03-13 16:00:00'
            },
            order_by=['trade_time'],
            limit=1000
        )
    """
    from app.db.crud.hk_stock_crud.hk_mins_crud import HkMinsCRUD
    
    crud = HkMinsCRUD(db)
    results = await crud.get_hk_mins(
        filters=filters,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    return results


# 计算VWAP（成交量加权平均价格）
async def calculate_vwap(db, ts_code: str, freq: str, date: str) -> List[Dict[str, Any]]:
    """
    计算特定股票特定日期的VWAP
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        freq: 分钟频度（1min/5min/15min/30min/60min）
        date: 日期 格式：2023-03-13
        
    返回:
        List[Dict]: 包含VWAP计算结果的数据列表
    """
    # 获取原始数据
    from app.db.crud.hk_stock_crud.hk_mins_crud import HkMinsCRUD
    
    crud = HkMinsCRUD(db)
    filters = {
        'ts_code': ts_code,
        'freq': freq,
        'trade_time__ge': f"{date} 00:00:00",
        'trade_time__le': f"{date} 23:59:59"
    }
    
    mins_data = await crud.get_hk_mins(
        filters=filters,
        order_by=['trade_time']
    )
    
    if not mins_data:
        return []
    
    # 将数据转换为pandas DataFrame便于计算
    import pandas as pd
    df = pd.DataFrame([d.model_dump() for d in mins_data])
    
    # 计算累计成交量和累计成交额
    df['cum_vol'] = df['vol'].cumsum()
    df['cum_amount'] = df['amount'].cumsum()
    
    # 计算VWAP
    df['vwap'] = df['cum_amount'] / df['cum_vol']
    
    # 保留两位小数
    df['vwap'] = df['vwap'].round(2)
    
    # 添加VWAP信息
    df['above_vwap'] = df['close'] > df['vwap']
    df['vwap_distance'] = ((df['close'] / df['vwap']) - 1) * 100
    df['vwap_distance'] = df['vwap_distance'].round(2)
    
    # 转换回字典列表
    result = df.to_dict('records')
    
    return result


# 计算技术指标 - 移动平均线
async def calculate_ma_for_mins(db, ts_code: str, freq: str, ma_periods: List[int] = [5, 10, 20, 60], start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    计算特定股票分钟数据的移动平均线
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        freq: 分钟频度（1min/5min/15min/30min/60min）
        ma_periods: 移动平均线周期列表，默认为[5, 10, 20, 60]
        start_date: 开始日期时间 格式：2023-03-13 09:00:00
        end_date: 结束日期时间 格式：2023-03-13 19:00:00
        
    返回:
        List[Dict]: 包含移动平均线计算结果的数据列表
    """
    # 获取原始数据
    from app.db.crud.hk_stock_crud.hk_mins_crud import HkMinsCRUD
    
    crud = HkMinsCRUD(db)
    filters = {
        'ts_code': ts_code,
        'freq': freq
    }
    
    if start_date:
        filters['trade_time__ge'] = start_date
    if end_date:
        filters['trade_time__le'] = end_date
    
    mins_data = await crud.get_hk_mins(
        filters=filters,
        order_by=['trade_time']
    )
    
    if not mins_data:
        return []
    
    # 将数据转换为pandas DataFrame便于计算
    import pandas as pd
    df = pd.DataFrame([d.model_dump() for d in mins_data])
    
    # 计算各周期的移动平均线
    for period in ma_periods:
        df[f'ma{period}'] = df['close'].rolling(window=period).mean().round(2)
    
    # 转换回字典列表
    result = df.to_dict('records')
    
    return result


# 计算技术指标 - RSI（相对强弱指标）
async def calculate_rsi_for_mins(db, ts_code: str, freq: str, period: int = 14, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    计算特定股票分钟数据的RSI
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        freq: 分钟频度（1min/5min/15min/30min/60min）
        period: RSI周期，默认为14
        start_date: 开始日期时间 格式：2023-03-13 09:00:00
        end_date: 结束日期时间 格式：2023-03-13 19:00:00
        
    返回:
        List[Dict]: 包含RSI计算结果的数据列表
    """
    # 获取原始数据
    from app.db.crud.hk_stock_crud.hk_mins_crud import HkMinsCRUD
    
    crud = HkMinsCRUD(db)
    filters = {
        'ts_code': ts_code,
        'freq': freq
    }
    
    if start_date:
        filters['trade_time__ge'] = start_date
    if end_date:
        filters['trade_time__le'] = end_date
    
    mins_data = await crud.get_hk_mins(
        filters=filters,
        order_by=['trade_time']
    )
    
    if not mins_data:
        return []
    
    # 将数据转换为pandas DataFrame便于计算
    import pandas as pd
    import numpy as np
    
    df = pd.DataFrame([d.model_dump() for d in mins_data])
    
    # 计算价格变化
    df['price_change'] = df['close'].diff()
    
    # 将价格变化分为上涨和下跌
    df['gain'] = np.where(df['price_change'] > 0, df['price_change'], 0)
    df['loss'] = np.where(df['price_change'] < 0, -df['price_change'], 0)
    
    # 计算RSI
    avg_gain = df['gain'].rolling(window=period).mean()
    avg_loss = df['loss'].rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    df[f'rsi{period}'] = 100 - (100 / (1 + rs))
    
    # 保留两位小数
    df[f'rsi{period}'] = df[f'rsi{period}'].round(2)
    
    # 删除中间计算列
    df = df.drop(columns=['price_change', 'gain', 'loss'])
    
    # 转换回字典列表
    result = df.to_dict('records')
    
    return result


# 合并多个时间频度的数据（如合并1min数据生成5min数据）
async def resample_mins_data(db, ts_code: str, source_freq: str, target_freq: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    将一个频度的分钟数据重新采样为另一个频度
    
    参数:
        db: 数据库连接对象
        ts_code: 股票代码
        source_freq: 源频度（如'1min'）
        target_freq: 目标频度（如'5min'）
        start_date: 开始日期时间 格式：2023-03-13 09:00:00
        end_date: 结束日期时间 格式：2023-03-13 19:00:00
        
    返回:
        List[Dict]: 重新采样后的数据列表
    """
    # 获取原始数据
    from app.db.crud.hk_stock_crud.hk_mins_crud import HkMinsCRUD
    
    crud = HkMinsCRUD(db)
    filters = {
        'ts_code': ts_code,
        'freq': source_freq
    }
    
    if start_date:
        filters['trade_time__ge'] = start_date
    if end_date:
        filters['trade_time__le'] = end_date
    
    mins_data = await crud.get_hk_mins(
        filters=filters,
        order_by=['trade_time']
    )
    
    if not mins_data:
        return []
    
    # 将数据转换为pandas DataFrame便于重新采样
    import pandas as pd
    
    df = pd.DataFrame([d.model_dump() for d in mins_data])
    
    # 设置时间索引
    df['trade_time'] = pd.to_datetime(df['trade_time'])
    df = df.set_index('trade_time')
    
    # 获取目标频度的pandas频率
    freq_map = {
        '1min': '1min',
        '5min': '5min',
        '15min': '15min',
        '30min': '30min',
        '60min': '60min'
    }
    
    target_pd_freq = freq_map.get(target_freq)
    if not target_pd_freq:
        raise ValueError(f"不支持的目标频度: {target_freq}")
    
    # 重新采样
    resampled = df.resample(target_pd_freq).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'vol': 'sum',
        'amount': 'sum'
    })
    
    # 重置索引
    resampled = resampled.reset_index()
    
    # 添加ts_code和freq字段
    resampled['ts_code'] = ts_code
    resampled['freq'] = target_freq
    
    # 处理NaN值
    resampled = resampled.dropna(subset=['open', 'high', 'low', 'close'])
    
    # 转换回字典列表
    result = resampled.to_dict('records')
    
    return result