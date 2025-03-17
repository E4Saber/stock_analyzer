# app/external/yfinance_client.py
import yfinance as yf
import pandas as pd
from typing import Dict, List, Any, Optional
import datetime
from app.utils.data_formater import ensure_serializable
from app.data.modules.global_index_data import GlobalIndexData
from app.utils.data_formater import yahoo_finance_data_to_global_index_data

def get_global_indices(period: str = "max") -> List[Dict[str, Any]]:
    """
    获取全球主要指数数据
    包括美股、港股主要指数

    Args:
        period可选: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max, 默认为max
    """
    try:
        # 主要指数代码
        indices = {
            # "^GSPC": "标普500指数",
            # "^IXIC": "纳斯达克综合指数",
            # "^DJI": "道琼斯工业平均指数",
            "^HSI": "恒生指数",
            "^HSTECH.HK": "恒生科技指数",
            "^.HSTECH": "恒生科技指数",
            "^HSTECH.HS": "恒生科技指数",
            # "^FTSE": "富时100指数",
            # "^N225": "日经225指数"
        }
        
        result = []
        
        for code, name in indices.items():
            try:
                # 获取指数数据
                index_data = yf.Ticker(code)
                info = index_data.history(period=period)
                
                if not info.empty:
                    # last_row = info.iloc[-1]
                    # prev_close = info.iloc[-2]['Close'] if len(info) > 1 else last_row['Open']
                    
                    # result.append({
                    #     "code": code,
                    #     "name": name,
                    #     "current": round(float(last_row['Close']), 2),
                    #     "change": round(float(last_row['Close'] - prev_close), 2),
                    #     "change_pct": round(float((last_row['Close'] - prev_close) / prev_close * 100), 2)
                    # })
                    result.append(yahoo_finance_data_to_global_index_data(info, code))
            except Exception as e:
                print(f"获取{code}数据错误: {str(e)}")
        
        return result
    except Exception as e:
        print(f"获取全球指数数据错误: {str(e)}")
        raise Exception(f"获取全球指数数据错误: {str(e)}")

def get_stock_data(stock_code: str, period: str = "1d") -> Dict[str, Any]:
    """
    获取单只股票数据
    支持美股、港股等YFinance支持的市场
    """
    try:
        # 格式化股票代码（对于港股，需要添加.HK后缀）
        if stock_code.isdigit() and len(stock_code) == 5:
            if stock_code.startswith('0') or stock_code.startswith('3'):
                formatted_code = f"{stock_code}.HK"
            else:
                formatted_code = stock_code
        else:
            formatted_code = stock_code
        
        # 获取股票数据
        stock = yf.Ticker(formatted_code)
        info = stock.info
        
        # 获取最新行情
        hist = stock.history(period="2d")
        
        if not hist.empty:
            current_data = hist.iloc[-1]
            prev_data = hist.iloc[-2] if len(hist) > 1 else current_data
            
            # 计算变化
            change = current_data['Close'] - prev_data['Close']
            change_pct = (change / prev_data['Close']) * 100
            
            # 构建返回数据
            result = {
                "code": formatted_code,
                "name": info.get('shortName', '未知'),
                "current": float(current_data['Close']),
                "change": float(change),
                "change_pct": float(change_pct),
                "open": float(current_data['Open']),
                "high": float(current_data['High']),
                "low": float(current_data['Low']),
                "volume": float(current_data['Volume']),
                "market_cap": info.get('marketCap', None),
                "sector": info.get('sector', None),
                "industry": info.get('industry', None),
                "currency": info.get('currency', 'USD')
            }
            
            return result
        else:
            raise Exception("未找到股票数据")
    except Exception as e:
        print(f"获取股票数据错误: {str(e)}")
        raise Exception(f"获取股票数据错误: {str(e)}")

def get_stock_history(stock_code: str, period: str = "1mo") -> List[Dict[str, Any]]:
    """
    获取股票历史K线数据
    period可选: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    """
    try:
        # 格式化股票代码
        if stock_code.isdigit() and len(stock_code) == 5:
            if stock_code.startswith('0') or stock_code.startswith('3'):
                formatted_code = f"{stock_code}.HK"
            else:
                formatted_code = stock_code
        else:
            formatted_code = stock_code
        
        # 获取历史数据
        stock = yf.Ticker(formatted_code)
        hist = stock.history(period=period)
        
        if not hist.empty:
            result = []
            
            for date, row in hist.iterrows():
                result.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": float(row['Volume'])
                })
            
            return result
        else:
            raise Exception("未找到历史数据")
    except Exception as e:
        print(f"获取历史数据错误: {str(e)}")
        raise Exception(f"获取历史数据错误: {str(e)}")
# Compare this snippet from app/main.py:

if __name__ == "__main__":
    # 获取全球主要指数数据
    indices = get_global_indices(period="1d")
    print(ensure_serializable(indices))