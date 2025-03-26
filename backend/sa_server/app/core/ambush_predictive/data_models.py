"""
数据模型定义
包含系统中使用的主要数据结构
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import pandas as pd
import numpy as np


@dataclass
class StockMeta:
    """股票基础信息"""
    code: str
    name: str
    industry: str
    market_cap: float  # 流通市值（亿元）
    total_cap: float   # 总市值（亿元）
    pe_ratio: float    # 市盈率
    pb_ratio: float    # 市净率
    float_shares: float  # 流通股本（亿股）
    total_shares: float  # 总股本（亿股）
    listing_date: datetime = field(default_factory=datetime.now)  # 上市日期
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'code': self.code,
            'name': self.name,
            'industry': self.industry,
            'market_cap': self.market_cap,
            'total_cap': self.total_cap,
            'pe_ratio': self.pe_ratio,
            'pb_ratio': self.pb_ratio,
            'float_shares': self.float_shares,
            'total_shares': self.total_shares,
            'listing_date': self.listing_date.strftime('%Y-%m-%d')
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StockMeta':
        """从字典创建对象"""
        return cls(
            code=data['code'],
            name=data['name'],
            industry=data['industry'],
            market_cap=data['market_cap'],
            total_cap=data['total_cap'],
            pe_ratio=data['pe_ratio'],
            pb_ratio=data['pb_ratio'],
            float_shares=data['float_shares'],
            total_shares=data['total_shares'],
            listing_date=datetime.strptime(data['listing_date'], '%Y-%m-%d') if 'listing_date' in data else datetime.now()
        )


@dataclass
class MarketContext:
    """市场环境上下文"""
    date: datetime
    market_status: str  # 'bull', 'bear', 'shock'
    index_price_change: float  # 大盘涨跌幅
    industry_price_change: float  # 所属行业涨跌幅
    market_turnover: float  # 市场换手率
    market_money_flow: float  # 市场资金流向（亿元）
    northbound_flow: float  # 北向资金流入（亿元）
    industry_fund_flow: float = 0.0  # 行业资金流入（亿元）
    industry_valuation: Dict[str, float] = field(default_factory=dict)  # 行业估值水平 {'pe': 15.2, 'pb': 1.8}
    market_sentiment_index: float = 50.0  # 市场情绪指数(0-100)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'date': self.date.strftime('%Y-%m-%d'),
            'market_status': self.market_status,
            'index_price_change': self.index_price_change,
            'industry_price_change': self.industry_price_change,
            'market_turnover': self.market_turnover,
            'market_money_flow': self.market_money_flow,
            'northbound_flow': self.northbound_flow,
            'industry_fund_flow': self.industry_fund_flow,
            'industry_valuation': self.industry_valuation,
            'market_sentiment_index': self.market_sentiment_index
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MarketContext':
        """从字典创建对象"""
        return cls(
            date=datetime.strptime(data['date'], '%Y-%m-%d'),
            market_status=data['market_status'],
            index_price_change=data['index_price_change'],
            industry_price_change=data['industry_price_change'],
            market_turnover=data['market_turnover'],
            market_money_flow=data['market_money_flow'],
            northbound_flow=data['northbound_flow'],
            industry_fund_flow=data.get('industry_fund_flow', 0.0),
            industry_valuation=data.get('industry_valuation', {}),
            market_sentiment_index=data.get('market_sentiment_index', 50.0)
        )


@dataclass
class AnalysisResult:
    """单个分析模块结果"""
    module_name: str
    score: float
    weight: float
    indicators: Dict[str, float]
    indicator_scores: Dict[str, float]
    description: str
    detail_info: Dict[str, Any]
    charts_data: Dict[str, Any] = field(default_factory=dict)  # 图表数据
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'module_name': self.module_name,
            'score': self.score,
            'weight': self.weight,
            'indicators': self.indicators,
            'indicator_scores': self.indicator_scores,
            'description': self.description,
            'detail_info': self.detail_info,
            'charts_data': self.charts_data
        }


@dataclass
class FinalAnalysisResult:
    """综合分析结果"""
    stock_code: str
    stock_name: str
    analysis_date: datetime
    final_score: float
    is_predicted_buried: bool
    module_results: Dict[str, AnalysisResult]
    analysis_summary: str
    recommendation: str
    verification_periods: Dict[str, int]  # {'short_term': 10, 'medium_term': 30, 'long_term': 90}
    stop_loss_levels: Dict[str, float]  # {'short_term': 5.0, 'medium_term': 10.0, 'long_term': 15.0}
    entry_strategy: str  # 建仓策略建议
    threshold: float  # 使用的预测阈值
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'stock_code': self.stock_code,
            'stock_name': self.stock_name,
            'analysis_date': self.analysis_date.strftime('%Y-%m-%d'),
            'final_score': self.final_score,
            'is_predicted_buried': self.is_predicted_buried,
            'module_results': {k: v.to_dict() for k, v in self.module_results.items()},
            'analysis_summary': self.analysis_summary,
            'recommendation': self.recommendation,
            'verification_periods': self.verification_periods,
            'stop_loss_levels': self.stop_loss_levels,
            'entry_strategy': self.entry_strategy,
            'threshold': self.threshold
        }