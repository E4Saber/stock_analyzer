# app/external/yfinance_client.py
from app.external.yfinance_api.stock_info_api import get_history, get_histories

import yfinance as yf
import pprint

# 使用pprint来美化输出
pp = pprint.PrettyPrinter(indent=2)

# 可用市场示例
markets = ["^GSPC"]

for market_code in markets:
    try:
        print(f"\n--- {market_code} 详细信息 ---\n")
        market = yf.Market(market_code)
        
        print("市场状态:")
        pp.pprint(market.status)
        
        print("\n市场摘要:")
        pp.pprint(market.summary)
        
    except Exception as e:
        print(f"获取 {market_code} 信息时出错: {e}")

# if __name__ == "__main__":
    # history = get_history("AAPL")
    # print(f"获取历史股票数据: {history}")
    # histories = get_histories(["AAPL", "MSFT"], period="1d", start="2021-01-01", end="2021-01-10")
    # print(f"获取多只股票历史数据: {histories}")
    # xs方法中的这两个参数用于在pandas多级索引DataFrame中选择数据：
    # axis=1: 指定沿着列(columns)方向进行选择。在pandas中，axis=0表示行，axis=1表示列。
    # level=1: 指定在哪个索引级别上进行选择。在您的多级列索引中：
    # level=0 是第一级索引，即数据类型（Price, Close, Dividends等）
    # level=1 是第二级索引，即股票代码（AAPL, MSFT）
    # 所以histories.xs('AAPL', axis=1, level=1)的含义是：
    # 在列方向(axis=1)
    # 在第二级索引(level=1)上
    # 选择值为'AAPL'的所有数据
    # apple_data = histories.xs('AAPL', axis=1, level=1)
    # print(f"获取苹果公司股票历史数据: {apple_data}")