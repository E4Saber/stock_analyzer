import numpy as np
import pandas as pd
import talib

"""
技术分析模块: 实现各种技术指标的计算和分析
"""

def calculate_indicators(df):
    """计算常用技术指标"""
    if df.empty:
        return df
    
    # 确保数据类型正确
    df = df.copy()
    
    # 提取价格数据
    close_prices = df['收盘'].values
    high_prices = df['最高'].values
    low_prices = df['最低'].values
    volume = df['成交量'].values
    
    # 移动平均线
    df['MA5'] = talib.SMA(close_prices, timeperiod=5)
    df['MA10'] = talib.SMA(close_prices, timeperiod=10)
    df['MA20'] = talib.SMA(close_prices, timeperiod=20)
    df['MA60'] = talib.SMA(close_prices, timeperiod=60)
    
    # MACD指标
    df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = talib.MACD(
        close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
    
    # RSI指标
    df['RSI6'] = talib.RSI(close_prices, timeperiod=6)
    df['RSI12'] = talib.RSI(close_prices, timeperiod=12)
    df['RSI24'] = talib.RSI(close_prices, timeperiod=24)
    
    # 布林带指标
    df['Upper_Band'], df['Middle_Band'], df['Lower_Band'] = talib.BBANDS(
        close_prices, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    
    # KDJ指标
    df['K'], df['D'] = talib.STOCH(
        high_prices, low_prices, close_prices, 
        fastk_period=9, slowk_period=3, slowk_matype=0, 
        slowd_period=3, slowd_matype=0)
    df['J'] = 3 * df['K'] - 2 * df['D']
    
    return df

def generate_trading_signals(df):
    """根据技术指标生成交易信号"""
    if df.empty or 'MA5' not in df.columns:
        return df
    
    df = df.copy()
    
    # 初始化信号列
    df['Signal'] = 0  # 0表示无信号，1表示买入信号，-1表示卖出信号
    
    # 均线金叉死叉信号
    df['MA5_Cross_MA20'] = np.where((df['MA5'].shift(1) < df['MA20'].shift(1)) & 
                                   (df['MA5'] > df['MA20']), 1, 0)
    df['MA5_Cross_MA20'] = np.where((df['MA5'].shift(1) > df['MA20'].shift(1)) & 
                                   (df['MA5'] < df['MA20']), -1, df['MA5_Cross_MA20'])
    
    # MACD金叉死叉信号
    df['MACD_Cross'] = np.where((df['MACD'].shift(1) < df['MACD_Signal'].shift(1)) & 
                                (df['MACD'] > df['MACD_Signal']), 1, 0)
    df['MACD_Cross'] = np.where((df['MACD'].shift(1) > df['MACD_Signal'].shift(1)) & 
                                (df['MACD'] < df['MACD_Signal']), -1, df['MACD_Cross'])
    
    # 综合信号
    df['Signal'] = df[['MA5_Cross_MA20', 'MACD_Cross']].sum(axis=1)
    df['Signal'] = np.where(df['Signal'] > 0, 1, np.where(df['Signal'] < 0, -1, 0))
    
    return df
