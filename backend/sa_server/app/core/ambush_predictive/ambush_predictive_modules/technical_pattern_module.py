"""
技术形态特征模块
分析股票的技术形态，包括底部形态、波动收敛、洗盘信号和突破前兆
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import logging
import talib as ta

from ..core.base_module import AnalysisModule
from ..core.data_models import StockMeta, MarketContext, AnalysisResult

logger = logging.getLogger('fund_burying_system')


class TechnicalPatternModule(AnalysisModule):
    """技术形态特征模块"""
    
    def __init__(self, weight: float = 0.20):
        """
        初始化模块
        
        Args:
            weight: 模块权重，默认为20%
        """
        super().__init__(name="technical_pattern_module", weight=weight)
        self.description = "分析股票技术形态特征，包括底部形态、波动收敛、洗盘信号和突破前兆"
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            # 底部形态配置
            "price_volatility_decrease_min": 25.0,  # 最小价格波动性降低(%)
            "bollinger_width_decrease_min": 25.0,  # 最小布林带宽度收窄(%)
            "support_level_increase_min": 3.0,  # 最小支撑位抬高(%)
            "resistance_level_change_max": 1.0,  # 最大阻力位变化(%)
            "bottom_consolidation_days_min": 15,  # 最小底部整理天数
            
            # 洗盘信号配置
            "long_lower_shadow_min_ratio": 1.5,  # 最小长下影线比例(影线/实体)
            "long_lower_shadow_min_count": 4,  # 最小长下影线次数
            "false_breakout_min_count": 2,  # 最小假突破回落次数
            "false_breakout_recovery_max": 1.0,  # 最大假突破回落幅度(%)
            "intraday_shakeout_min_count": 2,  # 最小盘中震仓次数
            "closing_rally_min": 0.8,  # 最小尾盘拉升幅度(%)
            
            # 突破前兆配置
            "key_resistance_test_min_count": 4,  # 最小关键压力位测试次数
            "resistance_test_interval_decrease_min": 20.0,  # 最小测试间隔缩短(%)
            "volume_increase_at_resistance_min": 30.0,  # 最小压力位测试量能增加(%)
            "moving_average_convergence_max": 1.0,  # 最大均线收敛夹角(度)
            "macd_divergence_min": 15.0,  # 最小MACD底背离程度(%)
            
            # 指标权重配置
            "indicator_weights": {
                # 底部形态 (45%)
                "price_volatility_score": 10,  # 价格波动性
                "bollinger_width_score": 10,  # 布林带宽度
                "support_resistance_score": 10,  # 支撑阻力位
                "consolidation_pattern_score": 15,  # 整理形态
                
                # 洗盘信号 (35%)
                "long_lower_shadow_score": 10,  # 长下影线
                "false_breakout_score": 10,  # 假突破回落
                "intraday_shakeout_score": 5,  # 盘中震仓
                "closing_rally_score": 10,  # 尾盘拉升
                
                # 突破前兆 (20%)
                "resistance_test_score": 8,  # 压力位测试
                "moving_average_score": 6,  # 均线系统
                "macd_divergence_score": 6  # MACD底背离
            }
        }
    
    def analyze(self, 
                stock_data: pd.DataFrame, 
                stock_meta: StockMeta, 
                market_context: MarketContext,
                **kwargs) -> AnalysisResult:
        """
        分析股票技术形态特征
        
        Args:
            stock_data: 包含交易数据的DataFrame
            stock_meta: 股票元信息
            market_context: 市场环境上下文
            
        Returns:
            分析结果
        """
        logger.info(f"开始分析 {stock_meta.code} 的技术形态特征")
        
        # 确保数据按日期排序
        stock_data = stock_data.sort_values('date').reset_index(drop=True)
        
        # 确保必要的列存在
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        
        missing_cols = [col for col in required_columns if col not in stock_data.columns]
        if missing_cols:
            logger.error(f"缺少必要的列: {missing_cols}")
            raise ValueError(f"数据缺少必要的列: {missing_cols}")
        
        # 扩展数据，添加技术指标
        data = self._add_technical_indicators(stock_data)
        
        # 计算各项指标
        # 1. 底部形态分析 (45%)
        self._analyze_bottom_pattern(data)
        
        # 2. 洗盘信号分析 (35%)
        self._analyze_shakeout_signals(data)
        
        # 3. 突破前兆分析 (20%)
        self._analyze_breakthrough_signals(data)
        
        # 计算总分
        self.score = self._calculate_weighted_score()
        
        # 生成分析描述
        self._generate_description()
        
        # 生成详细分析信息
        self._generate_detail_info(data)
        
        # 生成图表数据
        self._generate_charts_data(data)
        
        return self.get_result()
    
    