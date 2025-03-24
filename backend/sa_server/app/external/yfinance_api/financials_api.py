import pandas as pd
import yfinance as yf


def get_income_stmt(ts_code: str, as_dict: bool = False, pretty: bool = False, freq: str = 'yearly'):
    """
    yfinance.Ticker.get_income_stmt
        获取公司收入报表（损益表）
    
    输入参数：
        **as_dict: bool**（默认值：False）
        - 控制返回数据的格式
        - 默认情况下（False）返回 pandas DataFrame 对象
        - 设为 True 时，返回 Python 字典格式，方便 JSON 序列化或其他操作

        **pretty: bool**（默认值：False）
        - 控制是否美化行名称以提高可读性
        - 默认情况下（False）保持原始的行名称
        - 设为 True 时，会格式化行名称，使其更易于阅读

        **freq: str**（默认值：'yearly'）
        - 控制获取财务数据的频率
        - 可选值：
        - `'yearly'`：年度报表数据
        - `'quarterly'`：季度报表数据
        - `'trailing'`：最近12个月的滚动数据（trailing twelve months，TTM）
    返回字典内容：
        - Total Revenue（总收入）
        - Cost of Revenue（收入成本）
        - Gross Profit（毛利润）
        - Operating Expenses（运营费用）
        - Operating Income（营业利润）
        - Net Income（净利润）
        - EPS（每股收益）
    """
    try:
        # 获取收入报表信息
        income_stmt = yf.Ticker(ts_code).get_income_stmt(as_dict=as_dict, pretty=pretty, freq=freq)
        
        return income_stmt
    except Exception as e:
        print(f"获取公司收入报表（损益表）数据错误: {str(e)}")
        return None

def income_stmt(ts_code: str) -> pd.DataFrame:
    """
    yfinance.Ticker.income_stmt
        获取公司收入报表（损益表）
    """
    try:
        # 获取收入报表信息
        income_stmt = yf.Ticker(ts_code).income_stmt()
        
        return income_stmt
    except Exception as e:
        print(f"获取公司收入报表（损益表）数据错误: {str(e)}")
        return None
    




