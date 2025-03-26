"""
分析模块基类
定义了所有模块的通用接口和功能
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple
import pandas as pd
import numpy as np
import logging
from datetime import datetime

from .data_models import StockMeta, MarketContext, AnalysisResult

# 配置日志
logger = logging.getLogger('fund_burying_system')


class AnalysisModule(ABC):
    """分析模块抽象基类"""
    
    def __init__(self, name: str, weight: float = 0.0, enabled: bool = True):
        """
        初始化模块
        
        Args:
            name: 模块名称
            weight: 模块在总分中的权重
            enabled: 模块是否启用
        """
        self.name = name
        self.weight = weight
        self.enabled = enabled
        self.indicators: Dict[str, float] = {}  # 存储计算出的各项指标值
        self.indicator_scores: Dict[str, float] = {}  # 存储各项指标的得分
        self.score: float = 0.0  # 模块得分
        self.description: str = ""  # 模块描述
        self.detail_info: Dict[str, Any] = {}  # 详细分析信息
        self.charts_data: Dict[str, Any] = {}  # 图表数据
        
        # 配置信息，可通过config文件覆盖
        self.config: Dict[str, Any] = self._get_default_config()
    
    @abstractmethod
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        pass
    
    def load_config(self, config: Dict[str, Any]) -> None:
        """
        加载配置
        
        Args:
            config: 配置信息字典
        """
        if not config:
            return
        
        # 更新模块基本信息
        if 'weight' in config:
            self.weight = config['weight']
        if 'enabled' in config:
            self.enabled = config['enabled']
        
        # 更新模块特定配置
        if 'params' in config:
            for key, value in config['params'].items():
                if key in self.config:
                    self.config[key] = value
    
    @abstractmethod
    def analyze(self, 
                stock_data: pd.DataFrame, 
                stock_meta: StockMeta, 
                market_context: MarketContext,
                **kwargs) -> AnalysisResult:
        """
        分析股票数据
        
        Args:
            stock_data: 股票数据，包含OHLCV、资金流向等
            stock_meta: 股票元信息
            market_context: 市场环境上下文
            **kwargs: 其他参数
            
        Returns:
            分析结果
        """
        pass
    
    def get_result(self) -> AnalysisResult:
        """
        获取分析结果
        
        Returns:
            分析结果
        """
        return AnalysisResult(
            module_name=self.name,
            score=self.score,
            weight=self.weight,
            indicators=self.indicators,
            indicator_scores=self.indicator_scores,
            description=self.description,
            detail_info=self.detail_info,
            charts_data=self.charts_data
        )
    
    def is_enabled(self) -> bool:
        """
        检查模块是否启用
        
        Returns:
            是否启用
        """
        return self.enabled
    
    def set_enabled(self, enabled: bool) -> None:
        """
        设置模块是否启用
        
        Args:
            enabled: 是否启用
        """
        self.enabled = enabled
    
    def set_weight(self, weight: float) -> None:
        """
        设置模块权重
        
        Args:
            weight: 权重
        """
        self.weight = weight
    
    def _normalize_score(self, value: float, min_val: float, max_val: float) -> float:
        """
        将值标准化为0-100的分数
        
        Args:
            value: 原始值
            min_val: 最小值
            max_val: 最大值
            
        Returns:
            标准化后的分数
        """
        if max_val == min_val:
            return 50.0  # 避免除以零
        
        # 限制在0-100范围内
        score = 100 * (value - min_val) / (max_val - min_val)
        return max(0, min(100, score))
    
    def _calculate_weighted_score(self) -> float:
        """
        根据各指标得分计算模块加权得分
        
        Returns:
            加权得分
        """
        if not self.indicator_scores:
            return 0.0
        
        # 如果配置了指标权重，使用配置的权重
        if 'indicator_weights' in self.config:
            weights = self.config['indicator_weights']
            total_weight = sum(weights.get(k, 1.0) for k in self.indicator_scores.keys())
            weighted_score = sum(score * weights.get(k, 1.0) for k, score in self.indicator_scores.items()) / total_weight if total_weight > 0 else 0
        else:
            # 否则平均权重
            weighted_score = sum(self.indicator_scores.values()) / len(self.indicator_scores)
        
        return weighted_score