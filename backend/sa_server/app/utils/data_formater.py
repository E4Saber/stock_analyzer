import pandas as pd
from typing import List, Type
from pydantic import TypeAdapter
from app.data.modules.global_index_data import GlobalIndexData

def ensure_serializable(data):
    """确保数据可以被序列化为JSON"""
    if pd.isna(data):  # 处理NaN/None值
        return None
    elif isinstance(data, pd.Series):
        return {k: None if pd.isna(v) else v for k, v in data.to_dict().items()}
    elif isinstance(data, pd.DataFrame):
        # 先将NaN转为None
        df_copy = data.copy()
        df_copy = df_copy.where(pd.notna(df_copy), None)
        return df_copy.to_dict('records')
    elif isinstance(data, dict):
        return {k: ensure_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [ensure_serializable(item) for item in data]
    elif hasattr(data, 'item'):  # numpy 数据类型
        return None if pd.isna(data.item()) else data.item()
    else:
        return data

def dataframe_to_cn_model_instances(df: pd.DataFrame, model: Type) -> List:
    """将DataFrame转换为模型实例列表"""
    # 先将NaN转为None，确保JSON兼容
    df_copy = df.where(pd.notna(df), None)
    
    # 将DataFrame转换为字典列表
    records = df_copy.to_dict('records')

    # 再次检查并确保没有NaN值 (DataFrame.to_dict可能不会正确处理所有NaN)
    for record in records:
        for key, value in list(record.items()):
            if pd.isna(value):
                record[key] = None
    
    # 声明一个TypeAdapter
    ta = TypeAdapter(List[model])
    
    # 批量创建模型实例
    index_data_list = ta.validate_python(records)
    
    return index_data_list

def yahoo_finance_data_to_global_index_data(
    info: pd.DataFrame,
    code: str,
    name: str
) -> List[GlobalIndexData]:
    """
    将Yahoo Finance的数据转换为GlobalIndexData实例列表
    
    Args:
        code: Yahoo Finance的股票/指数代码
        info: 通过yf.Ticker(code).history()获取的DataFrame
        
    Returns:
        List[GlobalIndexData]: 模型实例列表
    """
    # 复制DataFrame避免修改原始数据
    df = info.copy()
    
    # 重置索引，将日期列添加为普通列
    df = df.reset_index()
    
    # 重命名列以匹配GlobalIndexData的字段
    column_mapping = {
        'Date': 'trade_date',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    }
    df = df.rename(columns=column_mapping)
    
    # 格式化日期为字符串 (YYYYMMDD 格式)
    df['trade_date'] = df['trade_date'].dt.strftime('%Y%m%d')
    
    # 添加ts_code列
    df['ts_code'] = code

    # 添加name列
    df['name'] = name
    
    # 计算前收盘价 (pre_close) - 使用前一天的收盘价
    df['pre_close'] = df['close'].shift(1)
    
    # 处理所有NaN值，替换为None
    df = df.where(pd.notna(df), None)

    # 计算剩余可选字段
    def transform_and_fill(record):
        # 计算涨跌点 (change)
        if 'change' not in record or record['change'] is None:
            if 'close' in record and 'pre_close' in record and pd.notna(record['pre_close']):
                record['change'] = record['close'] - record['pre_close']
        
        # 计算涨跌幅 (pct_chg)
        if 'pct_chg' not in record or record['pct_chg'] is None:
            if 'close' in record and 'pre_close' in record and pd.notna(record['pre_close']) and record['pre_close'] != 0:
                record['pct_chg'] = (record['close'] - record['pre_close']) / record['pre_close'] * 100
        
        # 处理成交量，Yahoo Finance返回的通常是股数
        if 'vol' not in record or record['vol'] is None:
            if 'volume' in record and pd.notna(record['volume']):
                # 假设vol是以手为单位，一手=100股
                record['vol'] = record['volume'] / 100
        
        # 计算成交额 (amount)
        if 'amount' not in record:
            if 'volume' in record and 'close' in record and pd.notna(record['volume']) and pd.notna(record['close']):
                # 使用当日均价估算
                avg_price = (record['open'] + record['high'] + record['low'] + record['close']) / 4
                record['amount'] = record['volume'] * avg_price
        
        return record
    
    # 转换每条记录
    records = df.to_dict('records')
    processed_records = [transform_and_fill(record) for record in records]
    
    # 最终确保所有记录中没有NaN值
    for record in processed_records:
        for key, value in list(record.items()):
            if pd.isna(value):
                record[key] = None

    # 使用TypeAdapter转换为模型实例
    from pydantic import TypeAdapter
    from typing import List
    
    ta = TypeAdapter(List[GlobalIndexData])
    model_instances = ta.validate_python(processed_records)
    
    return model_instances