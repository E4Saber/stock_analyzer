"""
数据加载模块: 负责从AKShare获取各类金融数据
添加了详细的调试信息以便排查问题
"""
import akshare as ak
import pandas as pd
import datetime
import traceback
import numpy as np

def get_stock_list(test_mode=False):
    """获取A股股票列表"""
    try:
        print("开始获取股票列表...")
        stock_info = ak.stock_info_a_code_name()
        print(f"成功获取股票列表，共 {len(stock_info)} 条记录")
        return stock_info
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        print(traceback.format_exc())
        return pd.DataFrame()

def get_stock_data(symbol, start_date, end_date, adjust="qfq"):
    """获取个股历史数据
    
    参数:
        symbol (str): 股票代码，如 "600000"
        start_date (str): 开始日期，格式为 "YYYYMMDD"
        end_date (str): 结束日期，格式为 "YYYYMMDD"
        adjust (str): 复权类型，qfq=前复权, hfq=后复权, 默认为前复权
        
    返回:
        pandas.DataFrame: 股票历史数据
    """
    try:
        print(f"开始获取股票 {symbol} 的历史数据...")
        print(f"日期范围: {start_date} 至 {end_date}")
        
        # 根据股票代码确定交易所
        if symbol.startswith('6'):
            full_symbol = f"sh{symbol}"
        else:
            full_symbol = f"sz{symbol}"
        
        print(f"完整股票代码: {full_symbol}")
        
        # 获取股票数据
        stock_data = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date, adjust=adjust)
        
        print(f"成功获取股票数据，共 {len(stock_data)} 条记录")
        print(f"数据列: {stock_data.columns.tolist()}")
        print(f"数据预览:\n{stock_data.head(2)}")
        
        return stock_data
    except Exception as e:
        print(f"获取股票数据失败: {e}")
        print(traceback.format_exc())
        return pd.DataFrame()

# 在data_loader.py中的get_index_data函数中添加日期处理逻辑
def get_index_data(symbol, start_date, end_date, test_mode=False):
    """获取指数数据"""
    try:
        print(f"开始获取指数 {symbol} 的历史数据...")
        print(f"日期范围: {start_date} 至 {end_date}")
        
        # 获取原始数据，不要先过滤
        df = ak.stock_zh_index_daily(symbol=symbol)
        print(f"原始指数数据获取结果: {'成功' if not df.empty else '失败'}")
        print(f"原始数据行数: {len(df)}")
        print(f"原始数据列: {df.columns.tolist()}")
        print("原始数据预览:")
        print(df.head(2))
        
        # 确保日期列正确设置为索引
        if 'date' in df.columns:
            # 先转换为标准格式，避免解析错误
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        
        # 打印日期范围，检查是否匹配
        print(f"数据日期范围: {df.index.min()} 至 {df.index.max()}")
        
        # 将输入日期字符串转换为datetime对象
        start_dt = pd.to_datetime(start_date, format='%Y%m%d')
        end_dt = pd.to_datetime(end_date, format='%Y%m%d')
        
        print(f"筛选日期范围: {start_dt} 至 {end_dt}")
        
        # 用loc进行日期范围过滤，确保包含边界值
        filtered_df = df.loc[start_dt:end_dt]
        
        print(f"过滤后数据行数: {len(filtered_df)}")
        
        return filtered_df
    except Exception as e:
        print(f"获取指数数据时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def get_sector_data(test_mode=False):
    """获取行业板块数据"""
    if test_mode:
        print("测试模式：生成示例行业板块数据")
        return get_sample_sector_data()
    try:
        print("开始获取行业板块数据...")
        
        # 获取行业板块涨跌幅数据
        sector_data = ak.stock_sector_spot()
        
        print(f"行业板块数据获取结果: {'成功' if not sector_data.empty else '失败，返回了空数据'}")
        if not sector_data.empty:
            print(f"行业板块数据行数: {len(sector_data)}")
            print(f"行业板块数据列: {sector_data.columns.tolist()}")
            print(f"行业板块数据预览:\n{sector_data.head(2)}")
        
        return sector_data
    except Exception as e:
        print(f"获取行业板块数据失败: {e}")
        print(traceback.format_exc())
        return pd.DataFrame()

def get_market_news(limit=50):
    """获取市场最新资讯
    
    参数:
        limit (int): 获取的新闻条数
        
    返回:
        pandas.DataFrame: 市场资讯
    """
    try:
        print("开始获取市场资讯...")
        
        # 获取东方财富网新闻
        stock_news = ak.stock_news_em()
        
        print(f"市场资讯获取结果: {'成功' if not stock_news.empty else '失败，返回了空数据'}")
        if not stock_news.empty:
            print(f"市场资讯数据行数: {len(stock_news)}")
            print(f"市场资讯数据列: {stock_news.columns.tolist()}")
            print(f"市场资讯数据预览:\n{stock_news.head(2)}")
            
            # 检查必要的列是否存在
            required_columns = ["日期", "标题", "链接"]
            for col in required_columns:
                if col not in stock_news.columns:
                    print(f"警告: 市场资讯数据缺少必要的列 '{col}'")
        
        return stock_news.head(limit)
    except Exception as e:
        print(f"获取市场资讯失败: {e}")
        print(traceback.format_exc())
        return pd.DataFrame(columns=["日期", "标题", "链接"])

def get_sample_index_data():
    """生成示例指数数据，用于测试模式"""
    # 创建日期范围
    dates = pd.date_range(start='2023-01-01', end='2024-03-15', freq='B')
    
    # 创建初始价格和随机变动
    initial_price = 3000
    np.random.seed(42)  # 确保可重现性
    price_changes = np.random.normal(0.0005, 0.015, size=len(dates))
    
    # 计算价格序列
    prices = initial_price * (1 + price_changes).cumprod()
    
    # 创建开盘价、最高价、最低价
    opens = prices * (1 + np.random.normal(0, 0.003, size=len(dates)))
    highs = np.maximum(prices * (1 + np.random.normal(0.005, 0.005, size=len(dates))), opens)
    lows = np.minimum(prices * (1 + np.random.normal(-0.005, 0.005, size=len(dates))), opens)
    
    # 创建成交量
    volumes = np.random.randint(500000000, 2000000000, size=len(dates))
    
    # 创建DataFrame
    df = pd.DataFrame({
        'open': opens,
        'high': highs,
        'low': lows,
        'close': prices,
        'volume': volumes
    }, index=dates)
    
    return df

def get_sample_sector_data():
    """生成示例行业板块数据，用于测试模式"""
    # 创建行业板块列表
    sectors = [
        "电子技术", "房地产", "医药制造", "食品饮料", "银行金融", 
        "汽车制造", "通信设备", "计算机应用", "化工行业", "机械设备",
        "建筑建材", "家用电器", "钢铁行业", "煤炭采选", "石油石化"
    ]
    
    # 创建涨跌幅
    np.random.seed(42)
    changes = np.random.normal(0, 2.5, size=len(sectors))
    
    # 生成其他数据
    companies = np.random.randint(10, 100, size=len(sectors))
    avg_prices = np.random.uniform(5, 30, size=len(sectors))
    volumes = np.random.randint(1000000, 10000000, size=len(sectors)) * 100
    amounts = volumes * avg_prices
    
    # 创建示例股票代码和名称
    stock_codes = [f"sh60{i:04d}" for i in range(len(sectors))]
    stock_names = [f"示例股票{i}" for i in range(len(sectors))]
    stock_changes = np.random.normal(0, 4, size=len(sectors))
    stock_prices = np.random.uniform(5, 50, size=len(sectors))
    stock_changes_amount = stock_prices * stock_changes / 100
    
    # 创建DataFrame
    df = pd.DataFrame({
        'label': [f"new_{i}" for i in range(len(sectors))],
        '板块': sectors,
        '公司家数': companies,
        '平均价格': avg_prices,
        '涨跌额': changes / 20,
        '涨跌幅': changes,
        '总成交量': volumes,
        '总成交额': amounts,
        '股票代码': stock_codes,
        '个股-涨跌幅': stock_changes,
        '个股-当前价': stock_prices,
        '个股-涨跌额': stock_changes_amount,
        '股票名称': stock_names
    })
    
    return df