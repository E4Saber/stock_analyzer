import pandas as pd
import yfinance as yf


def get_recommendations(ts_code: str, as_dict: bool = False) -> pd.DataFrame:
    """
    yfinance.Ticker.get_recommendations
        获取股票的分析师推荐信息
    """
    try:
        # 获取分析师推荐信息
        recommendations = yf.Ticker(ts_code).get_recommendations(as_dict=as_dict)
        
        return recommendations
    except Exception as e:
        print(f"获取公司收入报表（损益表）数据错误: {str(e)}")
        return pd.DataFrame()

