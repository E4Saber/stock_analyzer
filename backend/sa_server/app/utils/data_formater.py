import pandas as pd
from typing import List, Type, Dict, Any
from pydantic import TypeAdapter
from app.data.db_modules.index_data import IndexData


def tushare_data_to_index_data(df: pd.DataFrame, model: Type) -> List:
    """
    将DataFrame转换为模型实例列表
    """
    # 将DataFrame转换为字典列表
    records = df.to_dict('records')

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


def yahoo_finance_data_to_index_data(
    info: pd.DataFrame,
    code: str,
    name: str = None
) -> List[IndexData]:
    """
    将Yahoo Finance的DataFrame数据转换为单个GlobalIndexData实例
    只返回最新的一条记录(第二条)，但使用前一条记录(第一条)的收盘价作为pre_close
    
    Args:
        info: 通过yf.Ticker(code).history()获取的DataFrame
        code: Yahoo Finance的股票/指数代码
        name: 指数名称
        
    Returns:
        List[GlobalIndexData]: 包含单个模型实例的列表
    """
    # 输入检查
    if not isinstance(info, pd.DataFrame):
        print(f"警告: 输入不是有效的DataFrame")
        return []
    
    # 检查DataFrame是否至少有两行
    if len(info) < 2:
        print(f"警告: DataFrame记录数不足，至少需要两条记录")
        return []
        
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
    
    # 只保留最后一行（最新数据）
    latest_record = df.iloc[-1].copy()
    
    # 获取前一条记录的收盘价
    if len(df) >= 2:
        previous_close = df.iloc[-2]['close']
    else:
        previous_close = None
    
    # 构建单条记录的字典
    record = latest_record.to_dict()
    
    # 添加ts_code和name
    record['ts_code'] = code
    record['name'] = name
    
    # 使用前一条记录的收盘价作为pre_close
    record['pre_close'] = previous_close
    
    # 计算其他字段
    # 计算涨跌点 (change)
    if ('close' in record and pd.notna(record['close']) and 
        'pre_close' in record and pd.notna(record['pre_close'])):
        record['change'] = record['close'] - record['pre_close']
    else:
        record['change'] = None
    
    # 计算涨跌幅 (pct_chg)
    if ('close' in record and pd.notna(record['close']) and 
        'pre_close' in record and pd.notna(record['pre_close']) and record['pre_close'] != 0):
        record['pct_chg'] = (record['close'] - record['pre_close']) / record['pre_close'] * 100
    else:
        record['pct_chg'] = None
    
    # 处理成交量，Yahoo Finance返回的通常是股数
    if 'volume' in record and pd.notna(record['volume']):
        # 假设vol是以手为单位，一手=100股
        record['vol'] = record['volume'] / 100
    else:
        record['vol'] = None
    
    # 计算成交额 (amount)
    if ('volume' in record and pd.notna(record['volume']) and 
        all(pd.notna(record.get(k, None)) for k in ['open', 'high', 'low', 'close'])):
        # 使用当日均价估算
        avg_price = (record['open'] + record['high'] + record['low'] + record['close']) / 4
        record['amount'] = record['volume'] * avg_price
    else:
        record['amount'] = None
    
    # 确保所有字段中没有NaN值
    for key, value in list(record.items()):
        if pd.isna(value):
            record[key] = None
    
    # 使用TypeAdapter转换为模型实例
    ta = TypeAdapter(List[IndexData])
    model_instances = ta.validate_python([record])
    
    return model_instances

def get_minimal_global_indices(indices_data: List[Dict[str, Any]]) -> List[IndexData]:
    """
    获取全球指数数据
    返回一个包含GlobalIndexData模型实例的列表
    """
    global_indices_data = []
    
    # 遍历数据列表
    for record in indices_data:
        # 检查记录结构
        if isinstance(record, dict) and "code" in record and "name" in record and "global_index_data" in record:
            code = record["code"]
            name = record["name"]
            global_index_data = record["global_index_data"]
            
            # 确保global_index_data是DataFrame
            if isinstance(global_index_data, pd.DataFrame):
                # 调用函数处理数据
                try:
                    rs = yahoo_finance_data_to_global_index_data(global_index_data, code, name)
                    global_indices_data.extend(rs)
                except Exception as e:
                    print(f"处理时出错: {e}")
            else:
                print(f"警告: {code} 的global_index_data不是DataFrame，而是 {type(global_index_data)}")
        else:
            print(f"警告: 记录格式不正确: {record}")
    
    return global_indices_data


if __name__ == "__main__":
    data = get_minimal_global_indices()
    print(f"处理成功，结果: {data}")