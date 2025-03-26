"""
数据加载工具
用于从数据源加载股票数据和市场环境数据
"""

import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, List, Any, Optional, Union

from ..core.data_models import MarketContext

logger = logging.getLogger('fund_burying_system.data_loader')


def load_stock_data(stock_code: str, 
                   start_date: Optional[str] = None, 
                   end_date: Optional[str] = None) -> pd.DataFrame:
    """
    加载股票数据
    
    Args:
        stock_code: 股票代码
        start_date: 开始日期，格式：YYYY-MM-DD，默认为90天前
        end_date: 结束日期，格式：YYYY-MM-DD，默认为今天
        
    Returns:
        股票数据DataFrame
    """
    # 设置默认日期范围
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    if not start_date:
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    
    logger.info(f"加载股票 {stock_code} 的数据，时间范围：{start_date} 至 {end_date}")
    
    # 首先尝试从本地文件加载
    data = _load_from_local_file(stock_code)
    if data is not None:
        logger.info(f"从本地文件加载了 {stock_code} 的数据，包含 {len(data)} 条记录")
        return data
    
    # 从远程API加载
    try:
        data = _load_from_api(stock_code, start_date, end_date)
        logger.info(f"从API加载了 {stock_code} 的数据，包含 {len(data)} 条记录")
        return data
    except Exception as e:
        logger.error(f"从API加载数据失败: {e}")
        # 加载失败时使用模拟数据
        logger.warning(f"使用模拟数据代替")
        return _generate_mock_data(stock_code, start_date, end_date)


def load_market_context() -> MarketContext:
    """
    加载市场环境上下文
    
    Returns:
        市场环境上下文对象
    """
    logger.info("加载市场环境上下文")
    
    # 首先尝试从本地文件加载
    context = _load_market_context_from_local()
    if context is not None:
        logger.info("从本地文件加载了市场环境上下文")
        return context
    
    # 从远程API加载
    try:
        context = _load_market_context_from_api()
        logger.info("从API加载了市场环境上下文")
        return context
    except Exception as e:
        logger.error(f"从API加载市场环境上下文失败: {e}")
        # 加载失败时使用模拟数据
        logger.warning("使用模拟市场环境上下文")
        return _generate_mock_market_context()


def _load_from_local_file(stock_code: str) -> Optional[pd.DataFrame]:
    """
    从本地文件加载股票数据
    
    Args:
        stock_code: 股票代码
        
    Returns:
        股票数据DataFrame，如果文件不存在则返回None
    """
    # 定义可能的文件路径
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    possible_paths = [
        os.path.join(base_dir, 'data', f"{stock_code}.csv"),
        os.path.join(base_dir, 'data', 'stocks', f"{stock_code}.csv"),
        os.path.join(os.path.expanduser('~'), 'stock_data', f"{stock_code}.csv")
    ]
    
    # 尝试加载每个路径
    for path in possible_paths:
        if os.path.exists(path):
            try:
                data = pd.read_csv(path)
                
                # 确保日期列格式正确
                if 'date' in data.columns:
                    data['date'] = pd.to_datetime(data['date'])
                
                return data
            except Exception as e:
                logger.error(f"加载本地文件 {path} 失败: {e}")
    
    return None


def _load_from_api(stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    从API加载股票数据
    
    Args:
        stock_code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        股票数据DataFrame
    """
    # 注意：实际应用中，这里需要实现与特定API的集成
    # 由于API可能需要密钥等敏感信息，这里只提供框架
    
    # 示例：这里假设有一个虚构的API
    """
    api_key = os.environ.get('STOCK_API_KEY', '')
    url = f"https://api.example.com/stock/{stock_code}"
    params = {
        'start_date': start_date,
        'end_date': end_date,
        'api_key': api_key
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data['data'])
    else:
        raise Exception(f"API请求失败，状态码: {response.status_code}, 响应: {response.text}")
    """
    
    # 由于没有实际API，这里抛出异常，让系统回退到使用模拟数据
    raise Exception("未实现实际API调用")


def _generate_mock_data(stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    生成模拟股票数据
    
    Args:
        stock_code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        模拟的股票数据DataFrame
    """
    # 转换日期
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    # 生成日期序列（跳过周末）
    dates = []
    current = start
    while current <= end:
        if current.weekday() < 5:  # 0-4 表示周一到周五
            dates.append(current)
        current += timedelta(days=1)
    
    # 生成价格序列（随机游走）
    base_price = 10.0
    prices = [base_price]
    for i in range(1, len(dates)):
        # 每日价格变动在-2%到2%之间
        change = np.random.normal(0, 0.01)
        new_price = prices[-1] * (1 + change)
        prices.append(new_price)
    
    # 生成其他数据列
    data = {
        'date': dates,
        'open': [price * (1 + np.random.normal(0, 0.005)) for price in prices],
        'high': [price * (1 + abs(np.random.normal(0, 0.01))) for price in prices],
        'low': [price * (1 - abs(np.random.normal(0, 0.01))) for price in prices],
        'close': prices,
        'volume': [np.random.randint(1000000, 10000000) for _ in prices],
        'amount': [price * np.random.randint(1000000, 10000000) for price in prices],
        'turnover_rate': [np.random.uniform(1.0, 3.0) for _ in prices],
    }
    
    # 生成资金流向数据
    fund_flow = []
    large_order_buy = []
    large_order_sell = []
    closing_fund_flow = []
    
    # 模拟资金埋伏特征：最近20天有持续资金流入
    for i in range(len(dates)):
        if i >= len(dates) - 20:
            # 最近20天大单持续净流入
            daily_buy = data['amount'][i] * np.random.uniform(0.3, 0.5)
            daily_sell = data['amount'][i] * np.random.uniform(0.2, 0.4)
            daily_flow = daily_buy - daily_sell
        else:
            # 之前的日子随机流入流出
            daily_buy = data['amount'][i] * np.random.uniform(0.2, 0.4)
            daily_sell = data['amount'][i] * np.random.uniform(0.2, 0.4)
            daily_flow = daily_buy - daily_sell
        
        fund_flow.append(daily_flow)
        large_order_buy.append(daily_buy)
        large_order_sell.append(daily_sell)
        closing_fund_flow.append(daily_flow * np.random.uniform(0.3, 0.5))  # 尾盘资金占比30-50%
    
    data['fund_flow'] = fund_flow
    data['large_order_buy'] = large_order_buy
    data['large_order_sell'] = large_order_sell
    data['large_order_net_inflow'] = [buy - sell for buy, sell in zip(large_order_buy, large_order_sell)]
    data['closing_fund_flow'] = closing_fund_flow
    
    # 添加股票基本信息
    data['name'] = f"模拟股票{stock_code}"
    data['industry'] = "模拟行业"
    data['market_cap'] = base_price * 10000000 / 100000000  # 模拟市值10亿元
    data['pe_ratio'] = 20.0  # 模拟PE
    data['pb_ratio'] = 2.0   # 模拟PB
    
    return pd.DataFrame(data)


def _load_market_context_from_local() -> Optional[MarketContext]:
    """
    从本地文件加载市场环境上下文
    
    Returns:
        市场环境上下文对象，如果文件不存在则返回None
    """
    # 定义可能的文件路径
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    possible_paths = [
        os.path.join(base_dir, 'data', 'market_context.json'),
        os.path.join(base_dir, 'data', 'market', 'context.json'),
        os.path.join(os.path.expanduser('~'), 'stock_data', 'market_context.json')
    ]
    
    # 尝试加载每个路径
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return MarketContext.from_dict(data)
            except Exception as e:
                logger.error(f"加载本地市场环境文件 {path} 失败: {e}")
    
    return None


def _load_market_context_from_api() -> MarketContext:
    """
    从API加载市场环境上下文
    
    Returns:
        市场环境上下文对象
    """
    # 注意：实际应用中，这里需要实现与特定API的集成
    # 示例：这里假设有一个虚构的API
    """
    api_key = os.environ.get('STOCK_API_KEY', '')
    url = "https://api.example.com/market/context"
    params = {
        'api_key': api_key
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return MarketContext.from_dict(data)
    else:
        raise Exception(f"API请求失败，状态码: {response.status_code}, 响应: {response.text}")
    """
    
    # 由于没有实际API，这里抛出异常，让系统回退到使用模拟数据
    raise Exception("未实现实际API调用")


def _generate_mock_market_context() -> MarketContext:
    """
    生成模拟市场环境上下文
    
    Returns:
        模拟的市场环境上下文对象
    """
    # 随机选择市场状态
    market_status_options = ['bull', 'bear', 'shock']
    weights = [0.3, 0.3, 0.4]  # 概率权重
    market_status = np.random.choice(market_status_options, p=weights)
    
    # 根据市场状态设置其他参数
    if market_status == 'bull':
        index_price_change = np.random.uniform(0.5, 2.0)
        industry_price_change = np.random.uniform(0.0, 3.0)
        market_turnover = np.random.uniform(1.0, 2.0)
        market_money_flow = np.random.uniform(100, 500)  # 亿元
        northbound_flow = np.random.uniform(10, 50)  # 亿元
        market_sentiment_index = np.random.uniform(70, 90)
    elif market_status == 'bear':
        index_price_change = np.random.uniform(-2.0, -0.2)
        industry_price_change = np.random.uniform(-3.0, 0.0)
        market_turnover = np.random.uniform(0.5, 1.2)
        market_money_flow = np.random.uniform(-300, -50)  # 亿元
        northbound_flow = np.random.uniform(-30, 0)  # 亿元
        market_sentiment_index = np.random.uniform(10, 30)
    else:  # shock
        index_price_change = np.random.uniform(-0.8, 0.8)
        industry_price_change = np.random.uniform(-1.5, 1.5)
        market_turnover = np.random.uniform(0.8, 1.5)
        market_money_flow = np.random.uniform(-100, 100)  # 亿元
        northbound_flow = np.random.uniform(-10, 10)  # 亿元
        market_sentiment_index = np.random.uniform(40, 60)
    
    # 创建市场环境上下文
    return MarketContext(
        date=datetime.now(),
        market_status=market_status,
        index_price_change=index_price_change,
        industry_price_change=industry_price_change,
        market_turnover=market_turnover,
        market_money_flow=market_money_flow,
        northbound_flow=northbound_flow,
        industry_fund_flow=market_money_flow * np.random.uniform(0.01, 0.05),  # 行业资金流为市场的1-5%
        industry_valuation={'pe': 20.0, 'pb': 2.0},  # 示例行业估值数据
        market_sentiment_index=market_sentiment_index
    )