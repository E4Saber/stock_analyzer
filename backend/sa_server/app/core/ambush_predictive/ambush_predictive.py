"""
资金埋伏股分析系统主程序入口
"""

import os
import sys
import logging
import argparse
import pandas as pd
import json
from datetime import datetime

# 设置项目根目录到系统路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# 导入核心模块
from fund_burying_analyzer.core.analyzer import FundBuryingAnalyzer
from fund_burying_analyzer.core.data_models import StockMeta, MarketContext

# 导入分析模块
from fund_burying_analyzer.modules.fund_flow_module import FundFlowModule
from fund_burying_analyzer.modules.share_structure_module import ShareStructureModule
from fund_burying_analyzer.modules.technical_pattern_module import TechnicalPatternModule
from fund_burying_analyzer.modules.main_force_module import MainForceModule
from fund_burying_analyzer.modules.market_environment_module import MarketEnvironmentModule

# 导入工具模块
from fund_burying_analyzer.utils.data_loader import load_stock_data, load_market_context

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(BASE_DIR, 'logs', 'analyzer.log'), encoding='utf-8')
    ]
)

logger = logging.getLogger('fund_burying_analyzer')


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='资金埋伏股分析系统')
    
    parser.add_argument('--stock_code', type=str, required=True, help='股票代码')
    parser.add_argument('--data_file', type=str, help='股票数据文件路径')
    parser.add_argument('--market_file', type=str, help='市场环境数据文件路径')
    parser.add_argument('--config_file', type=str, default='config/default_config.json', help='配置文件路径')
    parser.add_argument('--output_file', type=str, help='结果输出文件路径')
    parser.add_argument('--disable_modules', type=str, help='禁用的模块列表，用逗号分隔')
    parser.add_argument('--only_modules', type=str, help='仅启用的模块列表，用逗号分隔')
    parser.add_argument('--adjust_weights', type=str, help='调整模块权重，格式为module_name:weight,module_name:weight')
    
    return parser.parse_args()


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 创建输出目录
    os.makedirs(os.path.join(BASE_DIR, 'output'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
    
    # 记录开始时间
    start_time = datetime.now()
    logger.info(f"开始分析股票: {args.stock_code}")
    
    try:
        # 加载数据
        if args.data_file:
            stock_data = pd.read_csv(args.data_file)
            # 转换日期列
            if 'date' in stock_data.columns:
                stock_data['date'] = pd.to_datetime(stock_data['date'])
        else:
            stock_data = load_stock_data(args.stock_code)
        
        # 加载市场环境
        if args.market_file:
            with open(args.market_file, 'r', encoding='utf-8') as f:
                market_data = json.load(f)
                market_context = MarketContext.from_dict(market_data)
        else:
            market_context = load_market_context()
        
        # 创建股票元信息
        stock_meta = create_stock_meta_from_data(stock_data, args.stock_code)