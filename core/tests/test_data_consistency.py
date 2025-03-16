# 创建一个简单的脚本来测试API配置一致性
import sys
import pandas as pd
import akshare as ak
import traceback

def test_data_consistency():
    """测试数据源一致性，确保web应用和测试脚本使用相同的数据源配置"""
    try:
        print("测试数据源一致性...")
        # 打印akshare版本
        print(f"AKShare版本: {ak.__version__}")
        
        # 测试获取上证指数数据
        symbol = "sh000001"
        df = ak.stock_zh_index_daily(symbol=symbol)
        print(f"获取到数据行数: {len(df)}")
        print(f"数据日期范围: {df['date'].min()} 至 {df['date'].max()}")
        print("数据样例:")
        print(df.head())
        
        # 验证能否获取最近的数据
        latest_date = pd.to_datetime(df['date']).max()
        print(f"最新数据日期: {latest_date}")
        
        # 检查路径和环境变量
        print(f"Python路径: {sys.executable}")
        print(f"模块搜索路径: {sys.path}")
        
        return True
    except Exception as e:
        print(f"测试数据源时出错: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_data_consistency()