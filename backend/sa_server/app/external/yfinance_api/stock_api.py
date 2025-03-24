import pandas as pd
import yfinance as yf
from typing import List
from pandas import Series


def get_isin(ts_code: str) -> str | None:
    """
    yfinance.Ticker.isin
        获取某只股票或金融资产的 ISIN（国际证券识别码，International Securities Identification Number）代码
    """
    try:
        # 获取ISIN代码
        isin = yf.Ticker(ts_code).isin
        
        return isin
    except Exception as e:
        print(f"获取ISIN代码错误: {str(e)}")
        return None


def get_history(ts_code: str, period: str = "1mo", interval: str = "1d",
                start: str = None, end: str = None, prepost: bool = False, actions: bool = True,
                auto_adjust: bool = True, back_adjust: bool = False, repair: bool = False, keepna: bool = False,
                proxy: str = None, rounding: bool = False, timeout: int = 10,
                raise_errors: bool = False) -> pd.DataFrame:
    """
    yfinance.Ticker.history
        

    输入参数：
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

    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        | 参数         | 类型         | 默认值 | 说明 |
        |-------------|-------------|--------|------|
        | `Date`      | `datetime64` | `None`  | 时间戳，表示该数据所属的日期或时间 |
        | `Open`      | `float64`    | `None`  | 开盘价 |
        | `High`      | `float64`    | `None`  | 最高价 |
        | `Low`       | `float64`    | `None`  | 最低价 |
        | `Close`     | `float64`    | `None`  | 收盘价（未调整） |
        | `Adj Close` | `float64`    | `None`  | **调整后收盘价**，考虑了拆股和股息影响 |
        | `Volume`    | `int64`      | `None`  | 成交量（交易的股票数量） |
        | `Dividends` | `float64`    | `0.0`   | 每股派发的股息 |
        | `Stock Splits` | `float64` | `0.0`   | 股票拆分比例，未拆分则为 `0.0` |
    """
    try:
        # 获取历史数据
        yfinance_ticker = yf.Ticker(ts_code)
        history = yfinance_ticker.history(period=period, interval=interval,
                                            start=start, end=end, prepost=prepost, actions=actions,
                                            auto_adjust=auto_adjust, back_adjust=back_adjust, repair=repair, keepna=keepna,
                                            proxy=proxy, rounding=rounding, timeout=timeout,
                                            raise_errors=raise_errors)

        
        return history
    except Exception as e:
        print(f"获取历史数据错误: {str(e)}")
        raise Exception(f"获取历史数据错误: {str(e)}")


def get_histories(ts_code_list: List, period: str = "1mo", interval: str = "1d",
                start: str = None, end: str = None, prepost: bool = False, actions: bool = True,
                auto_adjust: bool = True, repair: bool = False, proxy: str = None,
                threads: bool = False, group_by: str = 'column', progress: bool = True,
                timeout: int = 10, raise_errors: bool = False) -> pd.DataFrame:
    """
    yfinance.Tickers.history
    """
    try:
        # 获取历史数据
        yfinance_ticker = yf.Tickers(ts_code_list)
        histories = yfinance_ticker.history(period=period, interval=interval,
                                            start=start, end=end, prepost=prepost, actions=actions,
                                            auto_adjust=auto_adjust, repair=repair, proxy=proxy,
                                            threads=threads, group_by=group_by, progress=progress,
                                            timeout=timeout)

        
        return histories
    except Exception as e:
        print(f"获取历史数据错误: {str(e)}")
        if raise_errors:  # 手动处理 raise_errors 参数
            raise Exception(f"获取历史数据错误: {str(e)}")
        return pd.DataFrame()  # 如果不抛出异常，返回空DataFrame


def get_history_metadata(ts_code: str) -> dict:
    """
    yfinance.Ticker.history_metadata
        获取某只股票的历史数据元信息
    """
    try:
        # 获取元数据信息
        metadata = yf.Ticker(ts_code).get_history_metadata()
        
        return metadata
    except Exception as e:
        print(f"获取元数据信息错误: {str(e)}")
        return {}


def get_dividends(ts_code: str, period: str = 'max') -> pd.DataFrame:
    """
    yfinance.Ticker.dividends
        获取某只股票或金融资产的股息数据
    """
    try:
        # 获取股息数据
        dividends = yf.Ticker(ts_code).get_dividends(period=period)
        
        return dividends
    except Exception as e:
        print(f"获取股息数据错误: {str(e)}")
        return pd.DataFrame()


def dividends(ts_code: str) -> Series:
    """
    yfinance.Ticker.dividends
        获取某只股票或金融资产的股息数据
    """
    try:
        # 获取股息数据
        dividends = yf.Ticker(ts_code).dividends
        
        return dividends
    except Exception as e:
        print(f"获取股息数据错误: {str(e)}")
        return Series()


def get_splits(ts_code: str, period: str = 'max') -> Series:
    """
    yfinance.Ticker.get_splits
        获取某只股票的历史拆股数据
    """
    try:
        # 获取拆分数据
        splits = yf.Ticker(ts_code).get_splits(period=period)
        
        return splits
    except Exception as e:
        print(f"获取拆分数据错误: {str(e)}")
        return Series()

def splits(ts_code: str) -> Series:
    """
    yfinance.Ticker.splits
        获取某只股票的历史拆股数据
    """
    try:
        # 获取拆分数据
        splits = yf.Ticker(ts_code).splits
        
        return splits
    except Exception as e:
        print(f"获取拆分数据错误: {str(e)}")
        return Series()

def get_actions(ts_code: str, period: str = 'max') -> Series:
    """
    yfinance.Ticker.get_actions
        获取股票的历史公司行为（corporate actions）数据，主要包括股息（dividends）和股票拆分（stock splits）的综合信息。
        这个方法实际上是将 get_dividends() 和 get_splits() 的结果合并到一个 DataFrame 中
    """
    try:
        # 获取股息和拆分数据
        actions = yf.Ticker(ts_code).get_actions(period=period)
        
        return actions
    except Exception as e:
        print(f"获取股息和拆分数据错误: {str(e)}")
        return Series()

def actions(ts_code: str) -> pd.DataFrame:
    """
    yfinance.Ticker.actions
        获取股票的历史公司行为（corporate actions）数据，主要包括股息（dividends）和股票拆分（stock splits）的综合信息。
        这个方法实际上是将 dividends() 和 splits() 的结果合并到一个 DataFrame 中
    """
    try:
        # 获取股息和拆分数据
        actions = yf.Ticker(ts_code).actions
        
        return actions
    except Exception as e:
        print(f"获取股息和拆分数据错误: {str(e)}")
        return pd.DataFrame()

def get_capital_gains(ts_code: str, peroid: str = 'max') -> Series:
    """
    yfinance.Ticker.capital_gains
        获取基金或ETF的资本利得分配（capital gains distributions）历史数据。
        资本利得分配是基金或ETF在卖出投资组合中的证券并实现利润时，向投资者分配的收益。
    """
    try:
        # 获取资本收益数据
        capital_gains = yf.Ticker(ts_code).get_capital_gains(peroid=peroid)
        
        return capital_gains
    except Exception as e:
        print(f"获取资本收益数据错误: {str(e)}")
        return Series()

def capital_gains(ts_code: str) -> Series:
    """
    yfinance.Ticker.capital_gains
        获取基金或ETF的资本利得分配（capital gains distributions）历史数据。
        资本利得分配是基金或ETF在卖出投资组合中的证券并实现利润时，向投资者分配的收益。
    """
    try:
        # 获取资本收益数据
        capital_gains = yf.Ticker(ts_code).capital_gains
        
        return capital_gains
    except Exception as e:
        print(f"获取资本收益数据错误: {str(e)}")
        return Series()

def get_shares_full(ts_code: str, start: str = None, end: str = None) -> Series:
    """
    yfinance.Ticker.get_shares_full
        获取某只股票的流通股数量的完整历史数据
    """
    try:
        # 获取股本数据
        shares_full = yf.Ticker(ts_code).get_shares_full(start=start, end=end)
        
        return shares_full
    except Exception as e:
        print(f"获取股本数据错误: {str(e)}")
        return Series()

def get_info(ts_code: str) -> dict:
    """
    yfinance.Ticker.get_info
        获取某只股票或金融资产的基本信息
    """
    try:
        # 获取基本信息
        info = yf.Ticker(ts_code).get_info()
        
        return info
    except Exception as e:
        print(f"获取基本信息错误: {str(e)}")
        return {}

def info(ts_code: str) -> dict:
    """
    yfinance.Ticker.info
        获取某只股票或金融资产的基本信息
    """
    try:
        # 获取基本信息
        info = yf.Ticker(ts_code).info
        
        return info
    except Exception as e:
        print(f"获取基本信息错误: {str(e)}")
        return {}

def get_fast_info(ts_code: str) -> dict:
    """
    yfinance.Ticker.get_fast_info
        获取某只股票或金融资产的快速基本信息
        与 `get_info()` 相比，`get_fast_info()` 的主要特点是:
            1. 更快速 - 它获取数据的速度比 `get_info()` 更快
            2. 更轻量级 - 它返回的数据集更小，只包含核心市场数据
            3. 更可靠 - 它往往比 `get_info()` 更少出现连接问题

        - 当前股价
        - 今日最高/最低价
        - 交易量
        - 市值
        - 52周最高/最低价
        - 前收盘价
        - 开盘价
    """
    try:
        # 获取快速基本信息
        fast_info = yf.Ticker(ts_code).get_fast_info()
        
        return fast_info
    except Exception as e:
        print(f"获取快速基本信息错误: {str(e)}")
        return {}

def fast_info(ts_code: str) -> dict:
    """
    yfinance.Ticker.fast_info
        获取某只股票或金融资产的快速基本信息
    """
    try:
        # 获取快速基本信息
        fast_info = yf.Ticker(ts_code).fast_info
        
        return fast_info
    except Exception as e:
        print(f"获取快速基本信息错误: {str(e)}")
        return {}

def get_news(ts_code: str, count: int = 10, tab: str = 'news') -> List[dict]:
    """
    yfinance.Ticker.get_news
        获取某只股票或金融资产相关的新闻报道

        返回一个包含最近新闻文章的列表，每篇文章通常包含以下信息：
        - 标题 (title)
        - 发布者 (publisher)
        - 链接 (link)
        - 发布时间 (providerPublishTime)
        - 类型 (type)
        - 相关股票 (relatedTickers)
        - 摘要 (summary) - 在某些情况下
        
        这个方法对于以下场景非常有用：
        - 进行情绪分析
        - 监控特定公司的新闻动态
        - 构建新闻提醒系统
        - 研究新闻事件对股价的影响

    """
    try:
        # 获取新闻数据
        news = yf.Ticker(ts_code).get_news(count=count, tab=tab)
        
        return news
    except Exception as e:
        print(f"获取新闻数据错误: {str(e)}")
        return []

def news(ts_code: str) -> List[dict]:
    """
    yfinance.Ticker.news
        获取某只股票或金融资产相关的新闻报道
    """
    try:
        # 获取新闻数据
        news = yf.Ticker(ts_code).news
        
        return news
    except Exception as e:
        print(f"获取新闻数据错误: {str(e)}")
        return []