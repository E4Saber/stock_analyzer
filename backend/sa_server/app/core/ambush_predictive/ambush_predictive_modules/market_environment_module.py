"""
市场环境匹配模块
分析市场结构、行业板块联动性和政策估值安全边际
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import logging

from ..core.base_module import AnalysisModule
from ..core.data_models import StockMeta, MarketContext, AnalysisResult

logger = logging.getLogger('fund_burying_system')


class MarketEnvironmentModule(AnalysisModule):
    """市场环境匹配模块"""
    
    def __init__(self, weight: float = 0.10):
        """
        初始化模块
        
        Args:
            weight: 模块权重，默认为10%
        """
        super().__init__(name="market_environment_module", weight=weight)
        self.description = "分析市场环境匹配度，包括市场结构、板块联动和政策估值环境"
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            # 市场结构配置
            "market_style_match_weight": 0.4,  # 市场风格匹配权重
            "market_sentiment_bull_threshold": 70.0,  # 牛市情绪阈值
            "market_sentiment_bear_threshold": 30.0,  # 熊市情绪阈值
            "fund_flow_ratio_min": 0.5,  # 最小资金流入比例
            
            # 行业板块配置
            "sector_performance_weight": 0.4,  # 行业板块表现权重
            "sector_fund_flow_positive_threshold": 0.5,  # 行业资金流入阈值(亿元)
            "sector_diffusion_min": 0.5,  # 最小扩散效应比例
            "sector_rotation_position_weight": 0.3,  # 行业轮动位置权重
            
            # 政策估值配置
            "policy_environment_weight": 0.2,  # 政策环境权重
            "valuation_percentile_low": 20.0,  # 低估值分位点
            "valuation_percentile_high": 80.0,  # 高估值分位点
            
            # 指标权重配置
            "indicator_weights": {
                # 市场结构 (40%)
                "market_style_match_score": 15,  # 市场风格匹配
                "market_sentiment_score": 10,  # 市场情绪
                "market_fund_flow_score": 15,  # 市场资金面
                
                # 行业板块联动 (40%)
                "sector_performance_score": 10,  # 行业表现
                "sector_fund_flow_score": 10,  # 行业资金流
                "sector_diffusion_score": 10,  # 板块扩散效应
                "sector_rotation_position_score": 10,  # 行业轮动位置
                
                # 政策估值安全边际 (20%)
                "policy_direction_score": 10,  # 政策方向
                "valuation_safety_score": 10  # 估值安全边际
            }
        }
    
    def _rotation_position_to_chinese(self, position: str) -> str:
        """
        将行业轮动位置转换为中文描述
        
        Args:
            position: 轮动位置
            
        Returns:
            中文描述
        """
        position_map = {
            "starting": "启动初期",
            "accelerating": "加速上行期",
            "peaking": "顶部区域",
            "declining": "下行期",
            "bottoming": "筑底期",
            "neutral": "中性位置",
            "unknown": "未知位置"
        }
        return position_map.get(position, "未知位置")
    
    def _policy_direction_to_chinese(self, direction: str) -> str:
        """
        将政策方向转换为中文描述
        
        Args:
            direction: 政策方向
            
        Returns:
            中文描述
        """
        direction_map = {
            "favorable": "有利",
            "unfavorable": "不利",
            "neutral": "中性",
            "unknown": "未知"
        }
        return direction_map.get(direction, "未知")
    
    def analyze(self, 
                stock_data: pd.DataFrame, 
                stock_meta: StockMeta, 
                market_context: MarketContext,
                **kwargs) -> AnalysisResult:
        """
        分析市场环境匹配度
        
        Args:
            stock_data: 股票数据
            stock_meta: 股票元信息
            market_context: 市场环境上下文
            **kwargs: 可能包含行业数据、市场风格数据等
            
        Returns:
            分析结果
        """
        logger.info(f"开始分析 {stock_meta.code} 的市场环境匹配度")
        
        # 确保数据按日期排序
        stock_data = stock_data.sort_values('date').reset_index(drop=True)
        
        # 确保市场上下文数据完整
        if not market_context:
            logger.error("缺少市场环境上下文数据")
            raise ValueError("市场环境上下文数据不完整")
        
        # 计算各项指标
        # 1. 市场结构分析 (40%)
        self._analyze_market_structure(stock_data, stock_meta, market_context, **kwargs)
        
        # 2. 行业板块联动性分析 (40%)
        self._analyze_sector_linkage(stock_data, stock_meta, market_context, **kwargs)
        
        # 3. 政策估值安全边际分析 (20%)
        self._analyze_policy_valuation(stock_data, stock_meta, market_context, **kwargs)
        
        # 计算总分
        self.score = self._calculate_weighted_score()
        
        # 生成分析描述
        self._generate_description()
        
        # 生成详细分析信息
        self._generate_detail_info(stock_meta, market_context)
        
        # 生成图表数据
        self._generate_charts_data(stock_data, market_context, **kwargs)
        
        return self.get_result()
    
    def _analyze_market_structure(self, 
                             stock_data: pd.DataFrame, 
                             stock_meta: StockMeta, 
                             market_context: MarketContext,
                             **kwargs) -> None:
        """
        分析市场结构
        
        Args:
            stock_data: 股票数据
            stock_meta: 股票元信息
            market_context: 市场环境上下文
            **kwargs: 其他参数，可能包含market_style_data
        """
        # ----- 市场风格匹配度 -----
        market_style_match = False
        market_style_match_degree = 0.0
        
        # 获取市场风格数据
        market_style_data = kwargs.get('market_style_data', None)
        
        if market_style_data is not None:
            # 判断当前市场风格
            current_style = market_style_data.get('current_style', 'unknown')
            
            # 判断股票特性
            stock_style = self._determine_stock_style(stock_meta)
            
            # 计算风格匹配度
            if current_style in ['large_cap', 'value', 'dividend'] and stock_style in ['large_cap', 'value', 'dividend']:
                market_style_match = True
                market_style_match_degree = 0.8
            elif current_style in ['small_cap', 'growth', 'momentum'] and stock_style in ['small_cap', 'growth', 'momentum']:
                market_style_match = True
                market_style_match_degree = 0.8
            elif current_style == 'balanced':
                # 平衡市场风格，各类型都可以
                market_style_match = True
                market_style_match_degree = 0.6
            else:
                # 风格不匹配
                market_style_match = False
                market_style_match_degree = 0.3
        else:
            # 没有风格数据，使用市场状态估计
            market_status = market_context.market_status
            
            if market_status == 'bull':
                # 牛市环境，偏向成长股
                is_growth = stock_meta.pb_ratio > 3.0 or (stock_meta.pe_ratio > 30 if stock_meta.pe_ratio > 0 else False)
                market_style_match = is_growth
                market_style_match_degree = 0.7 if is_growth else 0.4
            elif market_status == 'bear':
                # 熊市环境，偏向价值股
                is_value = stock_meta.pb_ratio < 2.0 and (stock_meta.pe_ratio < 15 if stock_meta.pe_ratio > 0 else False)
                market_style_match = is_value
                market_style_match_degree = 0.7 if is_value else 0.4
            else:
                # 震荡市场，平衡环境
                market_style_match = True
                market_style_match_degree = 0.6
        
        # ----- 市场情绪分析 -----
        market_sentiment_favorable = False
        
        # 使用市场情绪指数判断
        market_sentiment = market_context.market_sentiment_index
        
        if market_sentiment >= self.config["market_sentiment_bull_threshold"]:
            # 市场情绪乐观
            market_sentiment_favorable = True
        elif market_sentiment <= self.config["market_sentiment_bear_threshold"]:
            # 市场情绪悲观
            market_sentiment_favorable = False
        else:
            # 市场情绪中性
            market_sentiment_favorable = (market_context.market_status != 'bear')
        
        # ----- 市场资金面分析 -----
        market_fund_flow_positive = False
        fund_flow_ratio = 0.0
        
        # 判断市场整体资金流
        market_money_flow = market_context.market_money_flow
        
        # 计算该股所在行业资金流占比
        if hasattr(market_context, 'industry_fund_flow') and market_context.industry_fund_flow != 0:
            fund_flow_ratio = market_context.industry_fund_flow / abs(market_money_flow) if market_money_flow != 0 else 0
            market_fund_flow_positive = fund_flow_ratio >= self.config["fund_flow_ratio_min"]
        else:
            # 无行业资金流数据，使用市场整体判断
            market_fund_flow_positive = market_money_flow > 0
            fund_flow_ratio = 0.5  # 默认中等水平
        
        # 存储指标值
        self.indicators.update({
            "market_style_match": market_style_match,
            "market_style_match_degree": market_style_match_degree,
            "market_sentiment_favorable": market_sentiment_favorable,
            "market_sentiment_index": market_sentiment,
            "market_fund_flow_positive": market_fund_flow_positive,
            "fund_flow_ratio": fund_flow_ratio,
        })
        
        # 计算各项指标得分
        # 市场风格匹配得分
        market_style_match_score = market_style_match_degree * 100
        
        # 市场情绪得分
        if market_sentiment_favorable:
            market_sentiment_score = 70 + (market_sentiment - self.config["market_sentiment_bull_threshold"]) / (100 - self.config["market_sentiment_bull_threshold"]) * 30
        else:
            market_sentiment_score = 50 * market_sentiment / self.config["market_sentiment_bear_threshold"]
        
        # 限制范围
        market_sentiment_score = max(10, min(market_sentiment_score, 100))
        
        # 市场资金面得分
        if market_fund_flow_positive:
            market_fund_flow_score = 70 + fund_flow_ratio * 30
        else:
            market_fund_flow_score = 50 * (0.5 + fund_flow_ratio / 2)
        
        # 限制范围
        market_fund_flow_score = max(20, min(market_fund_flow_score, 100))
        
        # 存储指标得分
        self.indicator_scores.update({
            "market_style_match_score": market_style_match_score,
            "market_sentiment_score": market_sentiment_score,
            "market_fund_flow_score": market_fund_flow_score,
        })

    def _analyze_sector_linkage(self, 
                           stock_data: pd.DataFrame, 
                           stock_meta: StockMeta, 
                           market_context: MarketContext,
                           **kwargs) -> None:
        """
        分析行业板块联动性
        
        Args:
            stock_data: 股票数据
            stock_meta: 股票元信息
            market_context: 市场环境上下文
            **kwargs: 其他参数，可能包含sector_data
        """
        # ----- 行业表现 -----
        sector_performance_good = False
        
        # 判断行业涨跌幅
        industry_price_change = market_context.industry_price_change
        sector_performance_good = industry_price_change > 0
        
        # ----- 行业资金流 -----
        sector_fund_flow_positive = False
        
        # 判断行业资金流向
        if hasattr(market_context, 'industry_fund_flow'):
            industry_fund_flow = market_context.industry_fund_flow
            sector_fund_flow_positive = industry_fund_flow >= self.config["sector_fund_flow_positive_threshold"]
        else:
            # 无行业资金流数据，使用行业涨跌幅估计
            sector_fund_flow_positive = industry_price_change > 1.0  # 行业涨幅超过1%视为资金流入
        
        # ----- 板块扩散效应 -----
        sector_diffusion_good = False
        sector_diffusion_ratio = 0.0
        
        # 获取行业数据
        sector_data = kwargs.get('sector_data', None)
        
        if sector_data is not None and 'up_stocks_ratio' in sector_data:
            # 行业内上涨股票比例
            sector_diffusion_ratio = sector_data['up_stocks_ratio']
            sector_diffusion_good = sector_diffusion_ratio >= self.config["sector_diffusion_min"]
        else:
            # 无行业数据，使用行业涨跌幅估计
            sector_diffusion_good = industry_price_change > 1.5  # 行业涨幅较大视为扩散效应良好
            sector_diffusion_ratio = 0.5  # 默认中等水平
        
        # ----- 行业轮动位置 -----
        sector_rotation_favorable = False
        sector_rotation_position = "unknown"
        
        if sector_data is not None and 'rotation_position' in sector_data:
            # 直接获取轮动位置
            sector_rotation_position = sector_data['rotation_position']
            
            # 判断位置是否有利
            if sector_rotation_position in ['starting', 'accelerating']:
                sector_rotation_favorable = True
            elif sector_rotation_position == 'peaking':
                sector_rotation_favorable = False
            else:
                # 其他位置视为中性
                sector_rotation_favorable = industry_price_change > 0
        else:
            # 无行业轮动数据，使用行业涨跌幅和市场环境估计
            if market_context.market_status == 'bull' and industry_price_change > 0:
                # 牛市且行业上涨，可能处于起始或加速阶段
                sector_rotation_position = 'accelerating'
                sector_rotation_favorable = True
            elif market_context.market_status == 'bear' and industry_price_change < 0:
                # 熊市且行业下跌，可能处于下行阶段
                sector_rotation_position = 'declining'
                sector_rotation_favorable = False
            else:
                # 其他情况视为中性
                sector_rotation_position = 'neutral'
                sector_rotation_favorable = market_context.market_status != 'bear'
        
        # 存储指标值
        self.indicators.update({
            "sector_performance_good": sector_performance_good,
            "industry_price_change": industry_price_change,
            "sector_fund_flow_positive": sector_fund_flow_positive,
            "sector_diffusion_good": sector_diffusion_good,
            "sector_diffusion_ratio": sector_diffusion_ratio,
            "sector_rotation_favorable": sector_rotation_favorable,
            "sector_rotation_position": sector_rotation_position,
        })
        
        # 计算各项指标得分
        # 行业表现得分
        sector_performance_score = 50 + industry_price_change * 10
        
        # 限制范围
        sector_performance_score = max(20, min(sector_performance_score, 100))
        
        # 行业资金流得分
        if sector_fund_flow_positive:
            if hasattr(market_context, 'industry_fund_flow'):
                # 根据资金流入规模计算得分
                sector_fund_flow_score = 70 + market_context.industry_fund_flow / self.config["sector_fund_flow_positive_threshold"] * 30
                sector_fund_flow_score = min(100, sector_fund_flow_score)
            else:
                sector_fund_flow_score = 75  # 默认较高分
        else:
            sector_fund_flow_score = 30 + industry_price_change * 5
            sector_fund_flow_score = max(20, sector_fund_flow_score)
        
        # 板块扩散效应得分
        sector_diffusion_score = sector_diffusion_ratio * 100
        
        # 限制范围
        sector_diffusion_score = max(30, min(sector_diffusion_score, 100))
        
        # 行业轮动位置得分
        if sector_rotation_favorable:
            if sector_rotation_position == 'starting':
                sector_rotation_position_score = 90  # 开始轮动，高分
            elif sector_rotation_position == 'accelerating':
                sector_rotation_position_score = 80  # 加速阶段，较高分
            else:
                sector_rotation_position_score = 70  # 其他有利位置
        else:
            if sector_rotation_position == 'peaking':
                sector_rotation_position_score = 30  # 顶部，低分
            elif sector_rotation_position == 'declining':
                sector_rotation_position_score = 20  # 下行阶段，更低分
            else:
                sector_rotation_position_score = 50  # 中性位置
        
        # 存储指标得分
        self.indicator_scores.update({
            "sector_performance_score": sector_performance_score,
            "sector_fund_flow_score": sector_fund_flow_score,
            "sector_diffusion_score": sector_diffusion_score,
            "sector_rotation_position_score": sector_rotation_position_score,
        })
    
    def _analyze_policy_valuation(self, 
                             stock_data: pd.DataFrame, 
                             stock_meta: StockMeta, 
                             market_context: MarketContext,
                             **kwargs) -> None:
        """
        分析政策估值安全边际
        
        Args:
            stock_data: 股票数据
            stock_meta: 股票元信息
            market_context: 市场环境上下文
            **kwargs: 其他参数，可能包含policy_data和valuation_data
        """
        # ----- 政策方向 -----
        policy_favorable = False
        policy_direction = "neutral"
        
        # 获取政策数据
        policy_data = kwargs.get('policy_data', None)
        
        if policy_data is not None and 'direction' in policy_data:
            # 直接获取政策方向
            policy_direction = policy_data['direction']
            policy_favorable = policy_direction == 'favorable'
        else:
            # 无政策数据，使用行业和市场环境估计
            industry = stock_meta.industry
            
            # 简单判断政策友好行业
            policy_friendly_industries = ['technology', 'new_energy', 'consumer', 'healthcare',
                                        '科技', '新能源', '消费', '医疗']
            
            # 判断是否属于政策友好行业
            is_policy_friendly = any(friendly in industry for friendly in policy_friendly_industries)
            
            # 结合市场状态判断政策方向
            if is_policy_friendly and market_context.market_status != 'bear':
                policy_direction = 'favorable'
                policy_favorable = True
            elif not is_policy_friendly and market_context.market_status == 'bear':
                policy_direction = 'unfavorable'
                policy_favorable = False
            else:
                policy_direction = 'neutral'
                policy_favorable = market_context.market_status == 'bull'
        
        # ----- 估值安全边际 -----
        valuation_safe = False
        valuation_percentile = 50.0  # 默认中等估值水平
        
        # 获取估值数据
        valuation_data = kwargs.get('valuation_data', None)
        
        if valuation_data is not None and 'percentile' in valuation_data:
            # 直接获取估值分位数
            valuation_percentile = valuation_data['percentile']
            
            # 低估值为安全
            valuation_safe = valuation_percentile <= self.config["valuation_percentile_low"]
        else:
            # 无估值数据，使用PE、PB估计
            if stock_meta.pe_ratio > 0:  # 确保PE为正值
                # 根据行业不同设置阈值
                industry = stock_meta.industry
                
                # 高估值行业
                high_valuation_industries = ['technology', 'internet', 'new_energy', 
                                            '科技', '互联网', '新能源']
                
                # 低估值行业
                low_valuation_industries = ['bank', 'real_estate', 'utilities',
                                        '银行', '地产', '公用事业']
                
                # 根据行业设置阈值
                if any(high in industry for high in high_valuation_industries):
                    pe_threshold = 40
                    pb_threshold = 5
                elif any(low in industry for low in low_valuation_industries):
                    pe_threshold = 12
                    pb_threshold = 1.5
                else:
                    pe_threshold = 25
                    pb_threshold = 3
                
                # 估计估值分位数
                if stock_meta.pe_ratio < pe_threshold * 0.6:
                    valuation_percentile = 20  # 低估值
                elif stock_meta.pe_ratio < pe_threshold * 0.8:
                    valuation_percentile = 40  # 较低估值
                elif stock_meta.pe_ratio < pe_threshold:
                    valuation_percentile = 60  # 中等估值
                elif stock_meta.pe_ratio < pe_threshold * 1.5:
                    valuation_percentile = 80  # 高估值
                else:
                    valuation_percentile = 90  # 很高估值
                
                # 结合PB调整
                if stock_meta.pb_ratio < pb_threshold * 0.5:
                    valuation_percentile -= 15  # PB明显低，调低分位数
                elif stock_meta.pb_ratio > pb_threshold * 1.5:
                    valuation_percentile += 15  # PB明显高，调高分位数
                
                # 限制范围
                valuation_percentile = max(5, min(valuation_percentile, 95))
                
                # 低估值为安全
                valuation_safe = valuation_percentile <= self.config["valuation_percentile_low"]
            else:
                # PE为负或无法计算，假设估值中等
                valuation_percentile = 50
                valuation_safe = False
        
        # 存储指标值
        self.indicators.update({
            "policy_favorable": policy_favorable,
            "policy_direction": policy_direction,
            "valuation_safe": valuation_safe,
            "valuation_percentile": valuation_percentile,
        })
        
        # 计算各项指标得分
        # 政策方向得分
        if policy_direction == 'favorable':
            policy_direction_score = 85
        elif policy_direction == 'unfavorable':
            policy_direction_score = 30
        else:  # neutral
            policy_direction_score = 60
        
        # 估值安全边际得分
        if valuation_percentile <= self.config["valuation_percentile_low"]:
            # 低估值，高分
            valuation_safety_score = 100 - valuation_percentile / self.config["valuation_percentile_low"] * 20
        elif valuation_percentile >= self.config["valuation_percentile_high"]:
            # 高估值，低分
            valuation_safety_score = 30 - (valuation_percentile - self.config["valuation_percentile_high"]) / (100 - self.config["valuation_percentile_high"]) * 20
        else:
            # 中等估值，中等分
            normalized_position = (valuation_percentile - self.config["valuation_percentile_low"]) / (self.config["valuation_percentile_high"] - self.config["valuation_percentile_low"])
            valuation_safety_score = 80 - normalized_position * 50
        
        # 限制范围
        valuation_safety_score = max(10, min(valuation_safety_score, 100))
        
        # 存储指标得分
        self.indicator_scores.update({
            "policy_direction_score": policy_direction_score,
            "valuation_safety_score": valuation_safety_score,
        })


    def _generate_description(self) -> None:
        """生成模块分析描述"""
        # 根据总分确定整体评价
        if self.score >= 85:
            overall = "非常有利"
        elif self.score >= 75:
            overall = "有利"
        elif self.score >= 65:
            overall = "较为有利"
        elif self.score >= 55:
            overall = "中性"
        else:
            overall = "不够有利"
        
        # 市场结构描述
        market_style_match = self.indicators.get("market_style_match", False)
        market_sentiment_favorable = self.indicators.get("market_sentiment_favorable", False)
        market_fund_flow_positive = self.indicators.get("market_fund_flow_positive", False)
        
        structure_desc = ""
        if market_style_match and market_sentiment_favorable and market_fund_flow_positive:
            structure_desc = "市场环境整体向好，风格匹配度高，市场情绪积极，资金面充沛"
        elif market_style_match and (market_sentiment_favorable or market_fund_flow_positive):
            structure_desc = "市场风格与该股匹配，但情绪或资金面有所波动"
        else:
            structure_desc = "市场风格与该股匹配度一般，需关注市场环境变化"
        
        # 行业板块描述
        sector_performance_good = self.indicators.get("sector_performance_good", False)
        sector_fund_flow_positive = self.indicators.get("sector_fund_flow_positive", False)
        sector_rotation_position = self.indicators.get("sector_rotation_position", "unknown")
        
        sector_desc = ""
        if sector_performance_good and sector_fund_flow_positive:
            if sector_rotation_position in ['starting', 'accelerating']:
                sector_desc = "所属行业处于向上轮动初期，行业资金流向积极，具有良好发展势头"
            else:
                sector_desc = "所属行业表现良好，行业资金流入，但轮动位置需要关注"
        elif sector_performance_good or sector_fund_flow_positive:
            sector_desc = "所属行业表现一般，资金流向或行业轮动位置有待改善"
        else:
            sector_desc = "所属行业状况较弱，不是当前市场关注热点"
        
        # 政策估值描述
        policy_favorable = self.indicators.get("policy_favorable", False)
        valuation_safe = self.indicators.get("valuation_safe", False)
        valuation_percentile = self.indicators.get("valuation_percentile", 50.0)
        
        policy_val_desc = ""
        if policy_favorable and valuation_safe:
            policy_val_desc = f"政策环境有利，估值处于较低位置(行业{valuation_percentile:.0f}%分位)"
        elif policy_favorable:
            policy_val_desc = f"政策环境有利，但估值水平已经不低(行业{valuation_percentile:.0f}%分位)"
        elif valuation_safe:
            policy_val_desc = f"估值具有安全边际(行业{valuation_percentile:.0f}%分位)，但政策面一般"
        else:
            policy_val_desc = f"政策面和估值水平(行业{valuation_percentile:.0f}%分位)均需关注"
        
        # 生成最终描述
        self.description = f"当前市场环境对该股资金埋伏{overall}。{structure_desc}；{sector_desc}；{policy_val_desc}。"

    def _generate_detail_info(self, stock_meta: StockMeta, market_context: MarketContext) -> None:
        """
        生成详细分析信息
        
        Args:
            stock_meta: 股票元信息
            market_context: 市场环境上下文
        """
        detail_info = {}
        
        # 市场结构分析
        detail_info["市场结构分析"] = {
            "市场状态": market_context.market_status,
            "市场风格匹配度": f"{self.indicators.get('market_style_match_degree', 0) * 100:.1f}%",
            "市场情绪指数": f"{self.indicators.get('market_sentiment_index', 0):.1f}",
            "市场资金流向": f"{market_context.market_money_flow:.2f}亿元",
            "该股风格": self._determine_stock_style(stock_meta)
        }
        
        # 行业板块分析
        detail_info["行业板块分析"] = {
            "所属行业": stock_meta.industry,
            "行业涨跌幅": f"{self.indicators.get('industry_price_change', 0):.2f}%",
            "行业资金流向": f"{market_context.industry_fund_flow if hasattr(market_context, 'industry_fund_flow') else '未知'}亿元",
            "行业扩散效应": f"{self.indicators.get('sector_diffusion_ratio', 0) * 100:.1f}%上涨",
            "行业轮动位置": self._rotation_position_to_chinese(self.indicators.get('sector_rotation_position', 'unknown'))
        }
        
        # 政策估值分析
        detail_info["政策估值分析"] = {
            "政策方向": self._policy_direction_to_chinese(self.indicators.get('policy_direction', 'neutral')),
            "估值分位数": f"{self.indicators.get('valuation_percentile', 50):.1f}%",
            "估值安全边际": "有" if self.indicators.get('valuation_safe', False) else "无",
            "PE/PB": f"{stock_meta.pe_ratio:.2f}/{stock_meta.pb_ratio:.2f}"
        }
        
        # 环境匹配建议
        suggestions = []
        
        # 根据市场环境提供建议
        if market_context.market_status == 'bull':
            suggestions.append("牛市环境有利于资金操作，可积极把握机会")
        elif market_context.market_status == 'bear':
            suggestions.append("熊市环境下需谨慎操作，严格执行止损策略")
        else:
            suggestions.append("震荡市场需关注热点切换，做好板块轮动")
        
        # 根据行业状况提供建议
        if self.indicators.get('sector_performance_good', False) and self.indicators.get('sector_rotation_favorable', False):
            suggestions.append("所属行业处于良好位置，可适当提高仓位")
        elif not self.indicators.get('sector_performance_good', False):
            suggestions.append("行业表现不佳，建议等待行业企稳或转向其他强势行业")
        
        # 根据政策估值提供建议
        if self.indicators.get('policy_favorable', False) and not self.indicators.get('valuation_safe', False):
            suggestions.append("政策有利但估值偏高，建议逢低关注")
        elif not self.indicators.get('policy_favorable', False) and self.indicators.get('valuation_safe', False):
            suggestions.append("估值具备安全边际，可等待政策面改善")
        
        detail_info["环境匹配建议"] = suggestions if suggestions else ["暂无特别建议"]
        
        # 各项指标得分
        detail_info["各项指标得分"] = {k: f"{v:.2f}" for k, v in self.indicator_scores.items()}
        
        self.detail_info = detail_info

    def _generate_charts_data(self, 
                         stock_data: pd.DataFrame, 
                         market_context: MarketContext,
                         **kwargs) -> None:
        """
        生成图表数据
        
        Args:
            stock_data: 股票数据
            market_context: 市场环境上下文
            **kwargs: 其他参数
        """
        # 获取行业和市场指数数据
        market_index_data = kwargs.get('market_index_data', None)
        industry_index_data = kwargs.get('industry_index_data', None)
        
        # 如果没有提供指数数据，使用模拟数据
        if market_index_data is None or industry_index_data is None:
            # 生成最近60天的数据
            recent_days = min(60, len(stock_data))
            dates = stock_data.tail(recent_days)['date'].dt.strftime('%Y-%m-%d').tolist()
            
            # 生成模拟市场指数数据
            if market_index_data is None:
                # 使用随机波动模拟市场指数
                base_index = 3000  # 基准指数点位
                market_index = [base_index]
                
                # 生成与股票相关的指数走势
                close_prices = stock_data.tail(recent_days)['close'].tolist()
                
                for i in range(1, len(close_prices)):
                    # 指数涨跌幅有50%与个股同向，50%随机
                    stock_change = close_prices[i] / close_prices[i-1] - 1
                    if np.random.random() < 0.5:
                        # 与个股同向，但波动较小
                        index_change = stock_change * 0.5 + np.random.normal(0, 0.005)
                    else:
                        # 随机波动
                        index_change = np.random.normal(0, 0.01)
                    
                    new_index = market_index[-1] * (1 + index_change)
                    market_index.append(new_index)
                
                market_index_data = {
                    'dates': dates,
                    'values': market_index
                }
            
            # 生成模拟行业指数数据
            if industry_index_data is None:
                # 使用随机波动模拟行业指数
                base_index = 5000  # 基准行业指数点位
                industry_index = [base_index]
                
                # 生成与股票更相关的行业指数走势
                close_prices = stock_data.tail(recent_days)['close'].tolist()
                
                for i in range(1, len(close_prices)):
                    # 行业指数涨跌幅有70%与个股同向
                    stock_change = close_prices[i] / close_prices[i-1] - 1
                    if np.random.random() < 0.7:
                        # 与个股同向，相关性更高
                        index_change = stock_change * 0.7 + np.random.normal(0, 0.003)
                    else:
                        # 随机波动
                        index_change = np.random.normal(0, 0.008)
                    
                    new_index = industry_index[-1] * (1 + index_change)
                    industry_index.append(new_index)
                
                industry_index_data = {
                    'dates': dates,
                    'values': industry_index
                }
        
        # 准备股票价格数据
        recent_days = min(60, len(stock_data))
        dates = stock_data.tail(recent_days)['date'].dt.strftime('%Y-%m-%d').tolist()
        prices = stock_data.tail(recent_days)['close'].tolist()
        
        # 平衡基准点，计算相对表现
        # 将起始点归一化为100
        normalized_prices = [price / prices[0] * 100 for price in prices]
        normalized_market = [value / market_index_data['values'][0] * 100 for value in market_index_data['values']]
        normalized_industry = [value / industry_index_data['values'][0] * 100 for value in industry_index_data['values']]
        
        # 打包图表数据
        self.charts_data = {
            "dates": dates,
            "stock_prices": {
                "title": "股价表现",
                "type": "line",
                "data": prices
            },
            "market_index": {
                "title": "大盘指数",
                "type": "line",
                "data": market_index_data['values']
            },
            "industry_index": {
                "title": "行业指数",
                "type": "line",
                "data": industry_index_data['values']
            },
            "relative_performance": {
                "title": "相对表现(归一化)",
                "type": "line",
                "series": [
                    {
                        "name": "个股",
                        "data": normalized_prices
                    },
                    {
                        "name": "大盘",
                        "data": normalized_market
                    },
                    {
                        "name": "行业",
                        "data": normalized_industry
                    }
                ]
            }
        }
