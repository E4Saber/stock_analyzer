# app/external/tushare_client.py
import tushare as ts
import pandas as pd
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv
from app.utils.data_formater import ensure_serializable
from app.data.modules.cn_index_data import CNIndexBaseData, CNIndexData

from app.utils.data_tpye_checker import data_check
from app.utils.data_formater import dataframe_to_cn_model_instances

# 加载环境变量
load_dotenv()

# 初始化Tushare
try:
    ts.set_token(os.getenv("TUSHARE_TOKEN", ""))
    pro = ts.pro_api()
except Exception as e:
    print(f"Tushare初始化错误: {str(e)}")
    # 使用空的API实例，后续会进行错误处理
    pro = None

def get_index_data() -> List[Dict[str, Any]]:
    """
    获取主要指数实时数据
    返回上证指数、深证成指、创业板指等主要指数
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取指数列表
        index_codes = ["000001.SH", "399001.SZ", "399006.SZ"]
        index_data = []
        
        # 获取指数基本信息
        df_basic = pro.index_basic(index_code=",".join(index_codes))

        # 获取最新行情
        # df_quote = pro.index_daily(ts_code=",".join(index_codes))

        # 整合数据
        for code in index_codes:
            basic_info = df_basic[df_basic['ts_code'] == code].iloc[0] if not df_basic.empty else None
            quote_info = pro.index_daily(ts_code=code)

            if basic_info is not None and quote_info is not None:
                cn_index_base_data = CNIndexBaseData(**basic_info)
                cn_index_data = dataframe_to_cn_model_instances(quote_info, CNIndexData)
        
        return {
            "cn_index_base_data": cn_index_base_data,
            "cn_index_data": cn_index_data
        }
    except Exception as e:
        print(f"获取指数数据错误: {str(e)}")
        raise Exception(f"获取指数数据错误: {str(e)}")

def get_stock_basic(stock_code: str) -> Dict[str, Any]:
    """
    获取单只股票的基本信息
    """
    if not pro:
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 格式化股票代码
        if '.' not in stock_code:
            if stock_code.startswith('6'):
                ts_code = f"{stock_code}.SH"
            else:
                ts_code = f"{stock_code}.SZ"
        else:
            ts_code = stock_code
        
        # 获取股票基本信息
        df_basic = pro.stock_basic(ts_code=ts_code, fields='ts_code,name,area,industry,list_date')
        
        # 获取最新行情
        df_quote = pro.daily(ts_code=ts_code)
        
        if not df_basic.empty and not df_quote.empty:
            basic_info = df_basic.iloc[0]
            quote_info = df_quote.iloc[0]
            
            return {
                "code": ts_code,
                "name": basic_info['name'],
                "current": quote_info['close'],
                "change": quote_info['close'] - quote_info['pre_close'],
                "change_pct": (quote_info['close'] - quote_info['pre_close']) / quote_info['pre_close'] * 100,
                "open": quote_info['open'],
                "high": quote_info['high'],
                "low": quote_info['low'],
                "volume": quote_info['vol'],
                "amount": quote_info['amount'],
                "industry": basic_info['industry'],
                "area": basic_info['area'],
                "list_date": basic_info['list_date']
            }
        else:
            raise Exception("未找到股票数据")
    except Exception as e:
        print(f"获取股票基本信息错误: {str(e)}")
        raise Exception(f"获取股票基本信息错误: {str(e)}")

def get_stock_kline(stock_code: str, period: str = '1d') -> List[Dict[str, Any]]:
    """
    获取股票K线数据
    """
    if not pro:
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 格式化股票代码
        if '.' not in stock_code:
            if stock_code.startswith('6'):
                ts_code = f"{stock_code}.SH"
            else:
                ts_code = f"{stock_code}.SZ"
        else:
            ts_code = stock_code
        
        # 计算日期范围
        end_date = pd.Timestamp.now().strftime('%Y%m%d')
        
        days = 30  # 默认返回30天数据
        if period == '5d':
            days = 5
        elif period == '1mo':
            days = 30
        elif period == '3mo':
            days = 90
        elif period == '6mo':
            days = 180
        elif period == '1y':
            days = 365
        
        start_date = (pd.Timestamp.now() - pd.Timedelta(days=days)).strftime('%Y%m%d')
        
        # 获取日线数据
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        
        if not df.empty:
            # 转换为列表格式
            df = df.sort_values('trade_date')  # 按日期排序
            kline_data = []
            
            for _, row in df.iterrows():
                kline_data.append({
                    "date": pd.to_datetime(row['trade_date']).strftime('%Y-%m-%d'),
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "volume": float(row['vol'])
                })
            
            return kline_data
        else:
            raise Exception("未找到K线数据")
    except Exception as e:
        print(f"获取K线数据错误: {str(e)}")
        raise Exception(f"获取K线数据错误: {str(e)}")
# app/external/yfinance_client.py