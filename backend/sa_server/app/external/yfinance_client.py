# app/external/yfinance_client.py
import yfinance as yf
import pandas as pd
from typing import Dict, List, Any, Optional
import datetime
from app.data.modules.global_index_data import GlobalIndexData

def get_global_indices(index_codes: List, period="1d", interval="1d",
                start=None, end=None, prepost=False, actions=True,
                auto_adjust=True, back_adjust=False, repair=False, keepna=False,
                proxy=None, rounding=False, timeout=10,
                raise_errors=False) -> List[Dict[str, Any]]:
    """
    获取全球主要指数数据
    包括美股、港股主要指数

    Args:

        | 参数 | 类型 | 默认值 | 说明 |
        |------|------|--------|------|
        | `period` | str | "1mo" | 获取数据的时间范围。选项包括: "1d"(一天), "5d"(五天), "1mo"(一个月), "3mo"(三个月), "6mo"(六个月), "1y"(一年), "2y"(两年), "5y"(五年), "10y"(十年), "ytd"(年初至今), "max"(最大可获取范围) |
        | `interval` | str | "1d" | 数据间隔。选项: "1m"(一分钟), "2m", "5m", "15m", "30m", "60m", "90m", "1h"(一小时), "1d"(一天), "5d", "1wk"(一周), "1mo"(一个月), "3mo" |
        | `start` | str/datetime | None | 开始日期，格式为 "YYYY-MM-DD" 或 datetime 对象。如果指定，会覆盖 `period` 参数 |
        | `end` | str/datetime | None | 结束日期，格式为 "YYYY-MM-DD" 或 datetime 对象 |
        | `prepost` | bool | False | 是否包含盘前和盘后交易数据 |
        | `actions` | bool | True | 是否调整股息和拆分 |
        | `auto_adjust` | bool | True | 是否使用OHLC调整收盘价 |
        | `back_adjust` | bool | False | 是否使用收盘价调整OHLC。仅当 `auto_adjust=False` 时有效 |
        | `repair` | bool | False | 是否尝试修复和清理数据异常 |
        | `keepna` | bool | False | 是否保留NaN值，False会删除包含NaN的行 |
        | `proxy` | str | None | 使用代理服务器的URL |
        | `rounding` | bool | False | 是否对价格进行舍入处理 |
        | `timeout` | int | 10 | 连接超时时间（秒） |
        | `raise_errors` | bool | False | 是否在出错时抛出异常，False时会返回空DataFrame |

        ## 补充说明

        1. **时间周期与时间间隔限制**：
        - 间隔为 "1m" 时，只能获取最近 7 天的数据
        - 间隔为 "2m", "5m", "15m", "30m", "60m", "90m", "1h" 时，只能获取最近 60 天的数据
        - 间隔为 "1d" 及以上时，可以获取更长时间范围的数据

        2. **auto_adjust 与 back_adjust**：
        - `auto_adjust=True`：使用调整后的收盘价来调整开盘价、最高价和最低价
        - `back_adjust=True`：基于最近的价格水平，向后调整所有数据

        3. **返回值**：
        - 返回一个 pandas DataFrame，包含以下列：Open, High, Low, Close, Volume，以及可能的 Dividends, Stock Splits (取决于 actions 参数)

        4. **数据源**：
        - 数据来自 Yahoo Finance API，可能受到访问限制或数据可用性的影响

    """
    try:
        
        result = []
        
        for code, name in index_codes.items():
            try:
                # 获取指数数据
                index_data = yf.Ticker(code)
                info = index_data.history(period=period, interval=interval,
                                            start=start, end=end, prepost=prepost, actions=actions,
                                            auto_adjust=auto_adjust, back_adjust=back_adjust, repair=repair, keepna=keepna,
                                            proxy=proxy, rounding=rounding, timeout=timeout,
                                            raise_errors=raise_errors)
                
                if not info.empty:
                    result.append({
                        "code": code,
                        "name": name,
                        "global_index_data": info
                    })
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
    from datetime import datetime, timedelta
    # 获取当前日期
    today = datetime.now()
    # 计算昨天的日期
    yesterday = today - timedelta(days=1)
    indices = get_global_indices(interval="1d", start=yesterday, end=yesterday)
    print(indices[0]["global_index_data"][0].close)