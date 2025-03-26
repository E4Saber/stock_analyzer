"""
主力特征判断模块
分析主力类型、建仓风格和主力操作特征
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import logging

from app.core.ambush_predictive.base_module import AnalysisModule
from app.core.ambush_predictive.data_models import StockMeta, MarketContext, AnalysisResult

logger = logging.getLogger('fund_burying_system')


class MainForceModule(AnalysisModule):
    """主力特征判断模块"""
    
    def __init__(self, weight: float = 0.15):
        """
        初始化模块
        
        Args:
            weight: 模块权重，默认为15%
        """
        super().__init__(name="main_force_module", weight=weight)
        self.description = "分析主力资金特征，包括主力类型、建仓风格和操作特征"
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            # 主力类型识别配置
            "institutional_buyer_proportion_min": 50.0,  # 最小机构买入占比(%)
            "northbound_capital_holding_change_min": 0.5,  # 最小北向资金持股变化(%)
            "retail_volatility_threshold": 0.6,  # 游资波动阈值
            "retail_bid_ask_ratio_threshold": 2.0,  # 游资买卖比阈值
            
            # 建仓行为配置
            "building_position_duration_min": 10,  # 最小建仓持续天数
            "position_early_stage_proportion": 0.3,  # 建仓早期阶段比例
            "position_mid_stage_proportion": 0.5,  # 建仓中期阶段比例
            "pullback_buying_ratio_min": 1.5,  # 回调买入相对强度最小值
            
            # 模式库匹配配置
            "pattern_similarity_threshold": 0.75,  # 模式相似度阈值
            "similar_stock_match_window": 60,  # 同类股票对比窗口(天)
            "success_rate_threshold": 0.6,  # 历史成功率阈值
            
            # 指标权重配置
            "indicator_weights": {
                # 主力类型识别 (50%)
                "main_force_type_score": 15,  # 主力类型
                "institutional_buyer_score": 10,  # 机构买入
                "northbound_capital_score": 10,  # 北向资金
                "retail_characteristics_score": 10,  # 游资特征
                "insider_trading_score": 5,  # 内部交易
                
                # 建仓行为模式 (35%)
                "building_position_rhythm_score": 10,  # 建仓节奏
                "pullback_buying_score": 10,  # 回调买入
                "time_window_preference_score": 5,  # 时间窗口偏好
                "position_completion_score": 10,  # 建仓完成度
                
                # 历史操作匹配 (15%)
                "historical_pattern_score": 5,  # 历史模式
                "similar_stock_pattern_score": 5,  # 同类股票模式
                "main_force_track_record_score": 5  # 主力跟踪记录
            }
        }
    
    def analyze(self, 
                stock_data: pd.DataFrame, 
                stock_meta: StockMeta, 
                market_context: MarketContext,
                **kwargs) -> AnalysisResult:
        """
        分析主力特征
        
        Args:
            stock_data: 包含交易数据、机构席位数据的DataFrame
            stock_meta: 股票元信息
            market_context: 市场环境上下文
            
        Returns:
            分析结果
        """
        logger.info(f"开始分析 {stock_meta.code} 的主力特征")
        
        # 确保数据按日期排序
        stock_data = stock_data.sort_values('date').reset_index(drop=True)
        
        # 确保必要的列存在
        required_columns = ['date', 'close', 'volume', 'amount', 'large_order_buy', 'large_order_sell']
        
        # 检查哪些列是可选的（可能不存在）
        optional_columns = ['institutional_buy', 'institutional_sell', 'northbound_holding',
                           'insider_buy', 'insider_sell', 'top_buy_seats', 'top_sell_seats']
        
        missing_cols = [col for col in required_columns if col not in stock_data.columns]
        if missing_cols:
            logger.error(f"缺少必要的列: {missing_cols}")
            raise ValueError(f"数据缺少必要的列: {missing_cols}")
        
        # 记录哪些可选列不存在
        missing_optional_cols = [col for col in optional_columns if col not in stock_data.columns]
        if missing_optional_cols:
            logger.warning(f"缺少可选列: {missing_optional_cols}")
        
        # 计算各项指标
        # 1. 主力类型识别 (50%)
        self._analyze_main_force_type(stock_data, stock_meta, market_context)
        
        # 2. 建仓行为模式 (35%)
        self._analyze_building_position_pattern(stock_data)
        
        # 3. 历史操作匹配 (15%)
        self._analyze_historical_patterns(stock_data, stock_meta, **kwargs)
        
        # 计算总分
        self.score = self._calculate_weighted_score()
        
        # 生成分析描述
        self._generate_description()
        
        # 生成详细分析信息
        self._generate_detail_info(stock_data)
        
        # 生成图表数据
        self._generate_charts_data(stock_data)
        
        return self.get_result()
    
    def _analyze_main_force_type(self, stock_data: pd.DataFrame, stock_meta: StockMeta, market_context: MarketContext) -> None:
        """
        分析主力类型
        
        Args:
            stock_data: 股票数据
            stock_meta: 股票元信息
            market_context: 市场环境上下文
        """
        # 获取最近交易日的数据
        recent_days = min(20, len(stock_data))
        recent_data = stock_data.tail(recent_days).copy()
        
        # ----- 机构买入占比 -----
        institutional_buyer_proportion = 0
        if 'institutional_buy' in recent_data.columns and 'large_order_buy' in recent_data.columns:
            total_institutional_buy = recent_data['institutional_buy'].sum()
            total_large_buy = recent_data['large_order_buy'].sum()
            
            if total_large_buy > 0:
                institutional_buyer_proportion = total_institutional_buy / total_large_buy * 100
        else:
            # 如果没有直接的机构买入数据，尝试使用其他指标估计
            if 'top_buy_seats' in recent_data.columns:
                # 假设前5个买入席位中有机构特征的比例
                institutional_seats = recent_data['top_buy_seats'].apply(lambda x: self._estimate_institutional_seats(x) if isinstance(x, (list, str)) else 0).mean()
                institutional_buyer_proportion = institutional_seats * 100
        
        # ----- 北向资金持股变化 -----
        northbound_capital_holding_change = 0
        if 'northbound_holding' in recent_data.columns:
            # 计算北向资金持股变化
            if len(recent_data) >= 2:
                start_holding = recent_data['northbound_holding'].iloc[0]
                end_holding = recent_data['northbound_holding'].iloc[-1]
                
                if not pd.isna(start_holding) and not pd.isna(end_holding) and start_holding > 0:
                    northbound_capital_holding_change = (end_holding - start_holding) / start_holding * 100
        else:
            # 如果没有直接的北向资金数据，使用市场整体北向流入作为参考
            if hasattr(market_context, 'northbound_flow') and market_context.northbound_flow > 0:
                # 简单估计：假设该股获得的北向资金与市场整体成比例
                market_value_ratio = stock_meta.market_cap / 10000  # 假设市场总市值10000亿
                estimated_northbound_inflow = market_context.northbound_flow * market_value_ratio
                
                # 将资金流入转换为持股比例变化的粗略估计
                if stock_meta.market_cap > 0:
                    northbound_capital_holding_change = estimated_northbound_inflow / stock_meta.market_cap * 100
        
        # ----- 内部人员交易 -----
        insider_trading_active = False
        insider_trading_direction = 0  # 0:无变化, 1:增持, -1:减持
        
        if 'insider_buy' in recent_data.columns and 'insider_sell' in recent_data.columns:
            total_insider_buy = recent_data['insider_buy'].sum()
            total_insider_sell = recent_data['insider_sell'].sum()
            
            insider_trading_active = (total_insider_buy + total_insider_sell) > 0
            
            if insider_trading_active:
                if total_insider_buy > total_insider_sell:
                    insider_trading_direction = 1
                elif total_insider_sell > total_insider_buy:
                    insider_trading_direction = -1
        
        # ----- 资金波动性和买卖比 -----
        # 计算大单资金的波动系数
        if 'large_order_buy' in recent_data.columns:
            large_order_mean = recent_data['large_order_buy'].mean()
            large_order_std = recent_data['large_order_buy'].std()
            
            large_order_volatility = large_order_std / large_order_mean if large_order_mean > 0 else float('inf')
        else:
            large_order_volatility = 0.5  # 默认中等波动
        
        # 计算大单买卖比
        large_order_bid_ask_ratio = 0
        if 'large_order_buy' in recent_data.columns and 'large_order_sell' in recent_data.columns:
            total_large_buy = recent_data['large_order_buy'].sum()
            total_large_sell = recent_data['large_order_sell'].sum()
            
            if total_large_sell > 0:
                large_order_bid_ask_ratio = total_large_buy / total_large_sell
        
        # ----- 综合判断主力类型 -----
        main_force_type = "unknown"
        main_force_confidence = 0
        
        # 游资特征: 资金波动大，大单买卖比高，短期操作
        if (large_order_volatility > self.config["retail_volatility_threshold"] and 
            large_order_bid_ask_ratio > self.config["retail_bid_ask_ratio_threshold"]):
            main_force_type = "retail"
            
            # 计算游资特征置信度
            volatility_factor = min(large_order_volatility / self.config["retail_volatility_threshold"], 2.0)
            ratio_factor = min(large_order_bid_ask_ratio / self.config["retail_bid_ask_ratio_threshold"], 2.0)
            
            main_force_confidence = (volatility_factor + ratio_factor) / 2 * 100 if large_order_volatility > 0 else 60
        
        # 机构特征: 机构买入占比高，资金稳定
        elif institutional_buyer_proportion >= self.config["institutional_buyer_proportion_min"]:
            main_force_type = "institutional"
            
            # 计算机构特征置信度
            inst_factor = min(institutional_buyer_proportion / self.config["institutional_buyer_proportion_min"], 2.0)
            stab_factor = 1.0 if large_order_volatility < 0.4 else 0.5
            
            main_force_confidence = inst_factor * 70 + stab_factor * 30
        
        # 北向资金特征: 北向持股变化明显
        elif northbound_capital_holding_change >= self.config["northbound_capital_holding_change_min"]:
            main_force_type = "northbound"
            
            # 计算北向资金特征置信度
            north_factor = min(northbound_capital_holding_change / self.config["northbound_capital_holding_change_min"], 2.0)
            
            main_force_confidence = north_factor * 100
        
        # 产业资本特征: 内部人员增持
        elif insider_trading_active and insider_trading_direction == 1:
            main_force_type = "industry_capital"
            
            # 产业资本置信度固定较高
            main_force_confidence = 90
        
        # 存储指标值
        self.indicators.update({
            "institutional_buyer_proportion": institutional_buyer_proportion,
            "northbound_capital_holding_change": northbound_capital_holding_change,
            "insider_trading_active": insider_trading_active,
            "insider_trading_direction": insider_trading_direction,
            "large_order_volatility": large_order_volatility,
            "large_order_bid_ask_ratio": large_order_bid_ask_ratio,
            "main_force_type": main_force_type,
            "main_force_confidence": main_force_confidence,
        })
        
        # 计算各项指标得分
        config = self.config
        
        # 主力类型得分（基于置信度）
        if main_force_type != "unknown":
            main_force_type_score = min(main_force_confidence, 100)
        else:
            main_force_type_score = 50  # 未知类型给中等分数
        
        # 机构买入得分
        institutional_buyer_score = self._normalize_score(
            institutional_buyer_proportion,
            config["institutional_buyer_proportion_min"] * 0.5,
            config["institutional_buyer_proportion_min"] * 1.5
        )
        
        # 北向资金得分
        northbound_capital_score = self._normalize_score(
            northbound_capital_holding_change,
            config["northbound_capital_holding_change_min"] * 0.5,
            config["northbound_capital_holding_change_min"] * 1.5
        )
        
        # 游资特征得分
        if main_force_type == "retail":
            retail_characteristics_score = main_force_type_score
        else:
            # 非游资主导给较低分数
            retail_characteristics_score = 40
        
        # 内部交易得分
        if insider_trading_active:
            if insider_trading_direction == 1:
                # 增持是积极信号
                insider_trading_score = 90
            elif insider_trading_direction == -1:
                # 减持是消极信号
                insider_trading_score = 30
            else:
                # 无明显方向
                insider_trading_score = 50
        else:
            # 无内部交易活动
            insider_trading_score = 50  # 中性评分
        
        # 存储指标得分
        self.indicator_scores.update({
            "main_force_type_score": main_force_type_score,
            "institutional_buyer_score": institutional_buyer_score,
            "northbound_capital_score": northbound_capital_score,
            "retail_characteristics_score": retail_characteristics_score,
            "insider_trading_score": insider_trading_score,
        })
    
    def _analyze_building_position_pattern(self, stock_data: pd.DataFrame) -> None:
        """
        分析建仓行为模式
        
        Args:
            stock_data: 股票数据
        """
        # 获取最近交易日的数据
        recent_days = min(60, len(stock_data))  # 使用更长窗口分析建仓行为
        recent_data = stock_data.tail(recent_days).copy()
        
        # ----- 建仓节奏 -----
        # 计算累计大单净买入
        if 'large_order_buy' in recent_data.columns and 'large_order_sell' in recent_data.columns:
            recent_data['large_order_net'] = recent_data['large_order_buy'] - recent_data['large_order_sell']
            recent_data['cumulative_net'] = recent_data['large_order_net'].cumsum()
            
            # 如果累计是负值，重置为0（表示无建仓）
            if recent_data['cumulative_net'].iloc[-1] <= 0:
                recent_data['cumulative_net'] = 0
        else:
            # 如果没有大单数据，尝试使用资金流向
            if 'fund_flow' in recent_data.columns:
                recent_data['cumulative_net'] = recent_data['fund_flow'].cumsum()
                
                # 如果累计是负值，重置为0（表示无建仓）
                if recent_data['cumulative_net'].iloc[-1] <= 0:
                    recent_data['cumulative_net'] = 0
            else:
                # 无法计算建仓数据
                recent_data['cumulative_net'] = 0
        
        # 计算建仓持续天数（连续资金流入的天数）
        position_building_days = 0
        if 'large_order_net' in recent_data.columns:
            # 从最近向前查找连续净流入的天数
            for i in range(len(recent_data)-1, -1, -1):
                if recent_data['large_order_net'].iloc[i] <= 0:
                    break
                position_building_days += 1
        
        # 分析建仓阶段
        building_position_stage = "unknown"
        building_position_completion = 0
        
        if recent_data['cumulative_net'].iloc[-1] > 0:
            # 分析建仓曲线特征
            max_net = recent_data['cumulative_net'].max()
            final_net = recent_data['cumulative_net'].iloc[-1]
            
            if max_net > 0:
                # 建仓完成度估计
                building_position_completion = final_net / max_net * 100
                
                # 判断建仓阶段
                if building_position_completion < self.config["position_early_stage_proportion"] * 100:
                    building_position_stage = "early"
                elif building_position_completion < self.config["position_mid_stage_proportion"] * 100:
                    building_position_stage = "middle"
                else:
                    building_position_stage = "late"
        
        # ----- 回调买入特征 -----
        pullback_buying_ratio = 0
        
        # 识别回调日
        recent_data['is_pullback'] = False
        for i in range(2, len(recent_data)):
            # 连续两天下跌视为回调
            if (recent_data.iloc[i]['close'] < recent_data.iloc[i-1]['close'] and 
                recent_data.iloc[i-1]['close'] < recent_data.iloc[i-2]['close']):
                recent_data.loc[recent_data.index[i], 'is_pullback'] = True
        
        # 计算回调日的资金特征
        pullback_days = recent_data[recent_data['is_pullback']]
        non_pullback_days = recent_data[~recent_data['is_pullback']]
        
        if len(pullback_days) > 0 and len(non_pullback_days) > 0 and 'large_order_buy' in recent_data.columns:
            pullback_buy_avg = pullback_days['large_order_buy'].mean()
            non_pullback_buy_avg = non_pullback_days['large_order_buy'].mean()
            
            if non_pullback_buy_avg > 0:
                pullback_buying_ratio = pullback_buy_avg / non_pullback_buy_avg
        
        # ----- 时间窗口偏好 -----
        time_window_preference = "unknown"
        
        if 'closing_fund_flow' in recent_data.columns and 'fund_flow' in recent_data.columns:
            # 计算尾盘资金占比
            closing_flow_ratio = recent_data['closing_fund_flow'].sum() / recent_data['fund_flow'].sum() if recent_data['fund_flow'].sum() != 0 else 0
            
            # 判断时间窗口偏好
            if closing_flow_ratio > 0.4:
                time_window_preference = "closing"  # 偏好尾盘
            elif closing_flow_ratio < 0.2:
                time_window_preference = "opening"  # 偏好开盘
            else:
                time_window_preference = "intraday"  # 日内均衡
        
        # 存储指标值
        self.indicators.update({
            "position_building_days": position_building_days,
            "building_position_stage": building_position_stage,
            "building_position_completion": building_position_completion,
            "pullback_buying_ratio": pullback_buying_ratio,
            "time_window_preference": time_window_preference,
        })
        
        # 计算各项指标得分
        config = self.config
        
        # 建仓节奏得分
        # 根据建仓天数和建仓阶段评分
        if position_building_days >= config["building_position_duration_min"]:
            # 建仓持续时间达标
            duration_factor = min(position_building_days / config["building_position_duration_min"], 2.0)
            building_position_rhythm_score = 70 + 15 * (duration_factor - 1)
            
            # 根据建仓阶段调整
            if building_position_stage == "middle":
                # 中期阶段，正处于建仓黄金期
                building_position_rhythm_score += 10
            elif building_position_stage == "late":
                # 后期阶段，建仓接近完成
                building_position_rhythm_score += 5
        else:
            # 建仓时间不足
            if position_building_days > 0:
                building_position_rhythm_score = 50 + 20 * position_building_days / config["building_position_duration_min"]
            else:
                building_position_rhythm_score = 50  # 默认中等分数
        
        # 限制最大值
        building_position_rhythm_score = min(building_position_rhythm_score, 100)
        
        # 回调买入得分
        pullback_buying_score = self._normalize_score(
            pullback_buying_ratio,
            config["pullback_buying_ratio_min"] * 0.7,
            config["pullback_buying_ratio_min"] * 1.5
        )
        
        # 时间窗口偏好得分
        # 根据主力类型不同，偏好不同时间窗口
        time_window_preference_score = 50  # 默认中等分数
        
        main_force_type = self.indicators.get("main_force_type", "unknown")
        if main_force_type == "institutional" and time_window_preference == "closing":
            # 机构偏好尾盘，匹配度高
            time_window_preference_score = 90
        elif main_force_type == "retail" and time_window_preference == "intraday":
            # 游资偏好日内，匹配度高
            time_window_preference_score = 85
        elif main_force_type == "northbound" and time_window_preference == "closing":
            # 北向资金偏好尾盘，匹配度高
            time_window_preference_score = 90
        
        # 建仓完成度得分
        # 建仓在中期(30%-70%)时评分最高
        if 30 <= building_position_completion <= 70:
            position_completion_score = 90
        elif building_position_completion < 30:
            # 建仓初期
            position_completion_score = 70
        elif building_position_completion > 70:
            # 建仓后期，减分（可能即将结束）
            position_completion_score = 70 - (building_position_completion - 70) / 3
        else:
            # 无建仓
            position_completion_score = 50
        
        # 限制范围
        position_completion_score = max(50, min(position_completion_score, 100))
        
        # 存储指标得分
        self.indicator_scores.update({
            "building_position_rhythm_score": building_position_rhythm_score,
            "pullback_buying_score": pullback_buying_score,
            "time_window_preference_score": time_window_preference_score,
            "position_completion_score": position_completion_score,
        })
    
    def _analyze_historical_patterns(self, stock_data: pd.DataFrame, stock_meta: StockMeta, **kwargs) -> None:
        """
        分析历史操作模式匹配
        
        Args:
            stock_data: 股票数据
            stock_meta: 股票元信息
            **kwargs: 可能包含historical_patterns和similar_stocks_data
        """
        # 获取最近交易日的数据
        recent_days = min(30, len(stock_data))
        recent_data = stock_data.tail(recent_days).copy()
        
        # ----- 历史模式相似度 -----
        historical_pattern_similarity = 0
        
        # 如果提供了历史模式数据
        historical_patterns = kwargs.get('historical_patterns', None)
        if historical_patterns is not None:
            # 计算当前模式与历史模式的相似度
            current_pattern = self._extract_pattern_features(recent_data)
            
            # 寻找最相似的历史模式
            max_similarity = 0
            for pattern in historical_patterns:
                similarity = self._calculate_pattern_similarity(current_pattern, pattern)
                max_similarity = max(max_similarity, similarity)
            
            historical_pattern_similarity = max_similarity
        
        # ----- 同类股票模式匹配 -----
        similar_stock_pattern_match = False
        similar_stock_similarity = 0
        
        # 如果提供了同类股票数据
        similar_stocks_data = kwargs.get('similar_stocks_data', None)
        if similar_stocks_data is not None:
            # 计算当前股票与同类股票的模式相似度
            current_pattern = self._extract_pattern_features(recent_data)
            
            # 寻找最相似的同类股票
            max_similarity = 0
            for similar_stock in similar_stocks_data:
                similarity = self._calculate_pattern_similarity(current_pattern, similar_stock)
                max_similarity = max(max_similarity, similarity)
            
            similar_stock_similarity = max_similarity
            similar_stock_pattern_match = similar_stock_similarity >= self.config["pattern_similarity_threshold"]
        
        # ----- 主力跟踪记录 -----
        main_force_success_rate = 0
        main_force_avg_return = 0
        
        # 如果提供了主力跟踪记录
        main_force_track_record = kwargs.get('main_force_track_record', None)
        if main_force_track_record is not None:
            # 提取当前主力信息
            main_force_type = self.indicators.get("main_force_type", "unknown")
            
            # 如果能识别主力类型且跟踪记录中有该类型的记录
            if main_force_type != "unknown" and main_force_type in main_force_track_record:
                record = main_force_track_record[main_force_type]
                main_force_success_rate = record.get('success_rate', 0)
                main_force_avg_return = record.get('avg_return', 0)
        
        # 存储指标值
        self.indicators.update({
            "historical_pattern_similarity": historical_pattern_similarity,
            "similar_stock_pattern_match": similar_stock_pattern_match,
            "similar_stock_similarity": similar_stock_similarity,
            "main_force_success_rate": main_force_success_rate,
            "main_force_avg_return": main_force_avg_return,
        })
        
        # 计算各项指标得分
        config = self.config
        
        # 历史模式得分
        historical_pattern_score = self._normalize_score(
            historical_pattern_similarity,
            config["pattern_similarity_threshold"] * 0.7,
            config["pattern_similarity_threshold"] * 1.2
        )
        
        # 同类股票模式得分
        similar_stock_pattern_score = self._normalize_score(
            similar_stock_similarity,
            config["pattern_similarity_threshold"] * 0.7,
            config["pattern_similarity_threshold"] * 1.2
        )
        
        # 主力跟踪记录得分
        main_force_track_record_score = self._normalize_score(
            main_force_success_rate,
            config["success_rate_threshold"] * 0.7,
            config["success_rate_threshold"] * 1.2
        )
        
        # 考虑平均收益率的加分
        if main_force_avg_return > 20:
            main_force_track_record_score = min(100, main_force_track_record_score + 10)
        
        # 存储指标得分
        self.indicator_scores.update({
            "historical_pattern_score": historical_pattern_score,
            "similar_stock_pattern_score": similar_stock_pattern_score,
            "main_force_track_record_score": main_force_track_record_score,
        })
    
    def _extract_pattern_features(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        提取模式特征
        
        Args:
            data: 股票数据
            
        Returns:
            特征字典
        """
        features = {}
        
        # 提取资金流向特征
        if 'large_order_buy' in data.columns and 'large_order_sell' in data.columns:
            features['large_order_net_sequence'] = (data['large_order_buy'] - data['large_order_sell']).tolist()
            features['large_order_ratio'] = (data['large_order_buy'].sum() / data['large_order_sell'].sum() 
                                            if data['large_order_sell'].sum() > 0 else float('inf'))
        
        # 提取价格特征
        if 'close' in data.columns:
            features['price_sequence'] = data['close'].tolist()
            features['price_return'] = (data['close'].iloc[-1] / data['close'].iloc[0] - 1) if data['close'].iloc[0] > 0 else 0
        
        # 提取成交量特征
        if 'volume' in data.columns:
            features['volume_sequence'] = data['volume'].tolist()
            features['volume_ratio'] = data['volume'].iloc[-5:].mean() / data['volume'].iloc[:5].mean() if data['volume'].iloc[:5].mean() > 0 else 1
        
        return features
    
    def _calculate_pattern_similarity(self, pattern1: Dict[str, Any], pattern2: Dict[str, Any]) -> float:
        """
        计算两个模式的相似度
        
        Args:
            pattern1: 第一个模式特征
            pattern2: 第二个模式特征
            
        Returns:
            相似度 (0-1)
        """
        # 简化版相似度计算，实际应用需要更复杂的算法
        similarity_scores = []
        
        # 比较资金流向序列（使用DTW或简化的方法）
        if 'large_order_net_sequence' in pattern1 and 'large_order_net_sequence' in pattern2:
            # 简化为比较资金流向比例
            if 'large_order_ratio' in pattern1 and 'large_order_ratio' in pattern2:
                ratio1 = pattern1['large_order_ratio']
                ratio2 = pattern2['large_order_ratio']
                
                if ratio1 == float('inf') and ratio2 == float('inf'):
                    similarity_scores.append(1.0)
                elif ratio1 == float('inf') or ratio2 == float('inf'):
                    similarity_scores.append(0.5)
                else:
                    ratio_similarity = 1 - min(abs(ratio1 - ratio2) / max(ratio1, ratio2), 1.0)
                    similarity_scores.append(ratio_similarity)
        
        # 比较价格走势
        if 'price_return' in pattern1 and 'price_return' in pattern2:
            return1 = pattern1['price_return']
            return2 = pattern2['price_return']
            
            return_similarity = 1 - min(abs(return1 - return2) / (max(abs(return1), abs(return2)) + 0.01), 1.0)
            similarity_scores.append(return_similarity)
        
        # 比较成交量特征
        if 'volume_ratio' in pattern1 and 'volume_ratio' in pattern2:
            vratio1 = pattern1['volume_ratio']
            vratio2 = pattern2['volume_ratio']
            
            volume_similarity = 1 - min(abs(vratio1 - vratio2) / max(vratio1, vratio2), 1.0)
            similarity_scores.append(volume_similarity)
        
        # 计算平均相似度
        if similarity_scores:
            return sum(similarity_scores) / len(similarity_scores)
        else:
            return 0.0
    
    def _estimate_institutional_seats(self, seats_info: Union[List, str]) -> float:
        """
        估计机构席位比例
        
        Args:
            seats_info: 席位信息
            
        Returns:
            机构席位比例 (0-1)
        """
        # 这个函数需要根据实际数据格式进行实现
        # 简化版：假设提供的是席位列表，我们通过名称或代码判断是否为机构
        
        # 转换字符串为列表（如果是字符串）
        if isinstance(seats_info, str):
            try:
                seats_list = seats_info.split(',')
            except:
                return 0.0
        elif isinstance(seats_info, list):
            seats_list = seats_info
        else:
            return 0.0
        
        # 机构席位关键词
        institutional_keywords = ['机构', '券商', '基金', '保险', '银行', '社保', '信托']
        
        # 计数
        institutional_count = 0
        for seat in seats_list:
            if any(keyword in str(seat) for keyword in institutional_keywords):
                institutional_count += 1
        
        # 返回机构席位比例
        return institutional_count / len(seats_list) if len(seats_list) > 0 else 0.0
    
    def _generate_description(self) -> None:
        """生成模块分析描述"""
        # 根据总分确定整体评价
        if self.score >= 85:
            overall = "非常明显"
        elif self.score >= 75:
            overall = "明显"
        elif self.score >= 65:
            overall = "较为明显"
        elif self.score >= 55:
            overall = "轻微"
        else:
            overall = "不明显"
        
        # 主力类型描述
        main_force_type = self.indicators.get("main_force_type", "unknown")
        main_force_desc = self._main_force_type_to_chinese(main_force_type)
        
        # 建仓阶段描述
        building_stage = self.indicators.get("building_position_stage", "unknown")
        building_completion = self.indicators.get("building_position_completion", 0)
        
        stage_desc = ""
        if building_stage != "unknown":
            if building_stage == "early":
                stage_desc = f"处于建仓初期(完成度约{building_completion:.1f}%)"
            elif building_stage == "middle":
                stage_desc = f"处于建仓中期(完成度约{building_completion:.1f}%)"
            elif building_stage == "late":
                stage_desc = f"处于建仓后期(完成度约{building_completion:.1f}%)"
        
        # 生成最终描述
        self.description = f"该股表现出{overall}的{main_force_desc}埋伏特征"
        
        if stage_desc:
            self.description += f"，{stage_desc}。"
        else:
            self.description += "。"
        
        # 如果得分高于75，添加更多细节
        if self.score >= 75:
            # 回调买入特征
            pullback_ratio = self.indicators.get("pullback_buying_ratio", 0)
            if pullback_ratio > self.config["pullback_buying_ratio_min"]:
                self.description += f" 回调时大单买入强度为平时的{pullback_ratio:.2f}倍，表明主力积极在低位吸筹。"
            
            # 时间窗口偏好
            time_preference = self.indicators.get("time_window_preference", "unknown")
            if time_preference == "closing":
                self.description += " 主力偏好在尾盘建仓，具有典型的机构资金特征。"
            elif time_preference == "opening":
                self.description += " 主力偏好在开盘建仓，可能有短线操作倾向。"
        
        # 历史模式匹配
        similar_match = self.indicators.get("similar_stock_pattern_match", False)
        if similar_match:
            self.description += " 与同类成功案例的操作模式高度匹配，值得重点关注。"
    
    def _generate_detail_info(self, data: pd.DataFrame) -> None:
        """
        生成详细分析信息
        
        Args:
            data: 股票数据
        """
        detail_info = {}
        
        # 主力类型分析
        detail_info["主力类型分析"] = {
            "主力类型": self._main_force_type_to_chinese(self.indicators.get('main_force_type', 'unknown')),
            "主力置信度": f"{self.indicators.get('main_force_confidence', 0):.2f}%",
            "机构买入占比": f"{self.indicators.get('institutional_buyer_proportion', 0):.2f}%",
            "北向资金变化": f"{self.indicators.get('northbound_capital_holding_change', 0):.2f}%",
            "资金波动系数": f"{self.indicators.get('large_order_volatility', 0):.2f}",
            "大单买卖比": f"{self.indicators.get('large_order_bid_ask_ratio', 0):.2f}"
        }
        
        # 建仓行为分析
        detail_info["建仓行为分析"] = {
            "建仓持续天数": f"{self.indicators.get('position_building_days', 0)}天",
            "建仓阶段": self._building_stage_to_chinese(self.indicators.get('building_position_stage', 'unknown')),
            "建仓完成度": f"{self.indicators.get('building_position_completion', 0):.2f}%",
            "回调买入强度": f"{self.indicators.get('pullback_buying_ratio', 0):.2f}",
            "时间窗口偏好": self._time_preference_to_chinese(self.indicators.get('time_window_preference', 'unknown'))
        }
        
        # 历史模式匹配
        detail_info["历史模式匹配"] = {
            "历史模式相似度": f"{self.indicators.get('historical_pattern_similarity', 0):.2f}",
            "同类股匹配度": f"{self.indicators.get('similar_stock_similarity', 0):.2f}",
            "与成功案例匹配": "是" if self.indicators.get('similar_stock_pattern_match', False) else "否",
            "主力历史成功率": f"{self.indicators.get('main_force_success_rate', 0):.2f}%",
            "主力历史平均收益": f"{self.indicators.get('main_force_avg_return', 0):.2f}%"
        }
        
        # 各项指标得分
        detail_info["各项指标得分"] = {k: f"{v:.2f}" for k, v in self.indicator_scores.items()}
        
        # 建议关注点
        suggestions = []
        
        # 根据主力类型给出建议
        main_force_type = self.indicators.get("main_force_type", "unknown")
        if main_force_type == "institutional":
            suggestions.append("机构资金建仓，通常需要较长验证周期(30-60天)，可耐心持有")
        elif main_force_type == "northbound":
            suggestions.append("北向资金流入，通常代表中长期价值投资，可设置较宽止损位")
        elif main_force_type == "retail":
            suggestions.append("游资主导，短线波动较大，需设置较紧止损位(5-8%)，关注盘口变化")
        elif main_force_type == "industry_capital":
            suggestions.append("产业资本参与，通常代表长期投资，可较长持有周期")
        
        # 根据建仓阶段给出建议
        building_stage = self.indicators.get("building_position_stage", "unknown")
        if building_stage == "early":
            suggestions.append("建仓初期，可分批建仓，保留资金等待回调")
        elif building_stage == "middle":
            suggestions.append("建仓中期，主力资金活跃，可适当加仓")
        elif building_stage == "late":
            suggestions.append("建仓后期，需关注主力拉升信号，准备跟进")
        
        # 其他建议
        if self.indicators.get("pullback_buying_ratio", 0) > self.config["pullback_buying_ratio_min"]:
            suggestions.append("主力回调买入积极，可在回调时加仓")
        
        if self.indicators.get("similar_stock_pattern_match", False):
            suggestions.append("与成功案例高度匹配，建议重点关注")
        
        detail_info["建议关注点"] = suggestions if suggestions else ["暂无特别建议"]
        
        self.detail_info = detail_info
    
    def _generate_charts_data(self, data: pd.DataFrame) -> None:
        """
        生成图表数据
        
        Args:
            data: 股票数据
        """
        # 获取最近交易日的数据
        recent_days = min(60, len(data))  # 使用更长的周期绘图
        chart_data = data.tail(recent_days).copy()
        
        # 准备时间轴
        dates = chart_data['date'].dt.strftime('%Y-%m-%d').tolist()
        
        # 准备大单资金数据
        large_order_buy = []
        large_order_sell = []
        
        if 'large_order_buy' in chart_data.columns and 'large_order_sell' in chart_data.columns:
            large_order_buy = chart_data['large_order_buy'].tolist()
            large_order_sell = chart_data['large_order_sell'].tolist()
            
            # 计算净买入
            large_order_net = (chart_data['large_order_buy'] - chart_data['large_order_sell']).tolist()
            
            # 计算累计净买入
            cumulative_net = np.cumsum(large_order_net).tolist()
        else:
            large_order_net = []
            cumulative_net = []
        
        # 准备机构资金数据
        institutional_buy = []
        institutional_sell = []
        
        if 'institutional_buy' in chart_data.columns and 'institutional_sell' in chart_data.columns:
            institutional_buy = chart_data['institutional_buy'].tolist()
            institutional_sell = chart_data['institutional_sell'].tolist()
        
        # 准备北向资金数据
        northbound_holding = []
        
        if 'northbound_holding' in chart_data.columns:
            northbound_holding = chart_data['northbound_holding'].tolist()
        
        # 准备价格数据
        prices = chart_data['close'].tolist()
        
        # 打包图表数据
        self.charts_data = {
            "dates": dates,
            "large_order_buy": {
                "title": "大单买入",
                "type": "bar",
                "data": large_order_buy
            },
            "large_order_sell": {
                "title": "大单卖出",
                "type": "bar",
                "data": large_order_sell
            },
            "large_order_net": {
                "title": "大单净买入",
                "type": "bar",
                "data": large_order_net
            },
            "cumulative_net": {
                "title": "累计净买入",
                "type": "line",
                "data": cumulative_net
            },
            "prices": {
                "title": "收盘价",
                "type": "line",
                "data": prices,
                "yAxisIndex": 1
            }
        }
        
        # 添加可选数据
        if institutional_buy:
            self.charts_data["institutional_buy"] = {
                "title": "机构买入",
                "type": "bar",
                "data": institutional_buy
            }
        
        if institutional_sell:
            self.charts_data["institutional_sell"] = {
                "title": "机构卖出",
                "type": "bar",
                "data": institutional_sell
            }
        
        if northbound_holding:
            self.charts_data["northbound_holding"] = {
                "title": "北向持股",
                "type": "line",
                "data": northbound_holding,
                "yAxisIndex": 2
            }
    
    def _main_force_type_to_chinese(self, main_force_type: str) -> str:
        """
        将主力类型转换为中文描述
        
        Args:
            main_force_type: 主力类型
            
        Returns:
            中文描述
        """
        type_map = {
            "institutional": "机构资金",
            "northbound": "北向资金",
            "retail": "游资",
            "industry_capital": "产业资本",
            "unknown": "未明确"
        }
        return type_map.get(main_force_type, "未知类型")
    
    def _building_stage_to_chinese(self, building_stage: str) -> str:
        """
        将建仓阶段转换为中文描述
        
        Args:
            building_stage: 建仓阶段
            
        Returns:
            中文描述
        """
        stage_map = {
            "early": "建仓初期",
            "middle": "建仓中期",
            "late": "建仓后期",
            "unknown": "未明确"
        }
        return stage_map.get(building_stage, "未知阶段")
    
    def _time_preference_to_chinese(self, time_preference: str) -> str:
        """
        将时间窗口偏好转换为中文描述
        
        Args:
            time_preference: 时间窗口偏好
            
        Returns:
            中文描述
        """
        preference_map = {
            "opening": "偏好开盘",
            "closing": "偏好尾盘",
            "intraday": "全天均衡",
            "unknown": "未明确"
        }
        return preference_map.get(time_preference, "未知偏好")