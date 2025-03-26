"""
筹码结构特征模块
分析股票筹码分布、集中度、股东结构等特征
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import logging

from ..core.base_module import AnalysisModule
from ..core.data_models import StockMeta, MarketContext, AnalysisResult

logger = logging.getLogger('fund_burying_system')


class ShareStructureModule(AnalysisModule):
    """筹码结构特征模块"""
    
    def __init__(self, weight: float = 0.25):
        """
        初始化模块
        
        Args:
            weight: 模块权重，默认为25%
        """
        super().__init__(name="share_structure_module", weight=weight)
        self.description = "分析股票筹码结构特征，包括换手特征、筹码集中度和成交结构"
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            # 换手特征配置
            "turnover_rate_min": 1.0,  # 最小换手率
            "turnover_rate_max": 3.0,  # 最大换手率
            "turnover_stability_max": 0.3,  # 最大换手率波动系数
            "closing_turnover_ratio_min": 0.25,  # 最小尾盘换手占比
            
            # 筹码集中度配置
            "shareholders_decrease_min": 6.5,  # 最小股东户数减少率(%)
            "avg_holding_increase_min": 10.0,  # 最小户均持股增加率(%)
            "institution_holding_increase_min": 0.6,  # 最小机构持股增加率(%)
            "gini_coefficient_increase_min": 0.035,  # 最小基尼系数增加
            "locked_chips_ratio_min": 0.45,  # 最小筹码锁定率
            
            # 成交结构配置
            "large_order_bid_ask_ratio_min": 1.5,  # 最小大单买卖比
            "large_order_proportion_increase_min": 5.0,  # 最小大单占比增长(%)
            "block_trade_discount_max": 5.0,  # 最大大宗交易折价率(%)
            
            # 指标权重配置
            "indicator_weights": {
                # 换手特征 (35%)
                "turnover_rate_range_score": 10,  # 换手率范围
                "turnover_stability_score": 10,  # 换手率稳定性
                "turnover_trend_score": 5,  # 换手率趋势
                "closing_turnover_ratio_score": 10,  # 尾盘换手占比
                
                # 筹码集中度 (40%)
                "shareholders_decrease_score": 8,  # 股东户数减少
                "avg_holding_increase_score": 7,  # 户均持股增加
                "institution_holding_score": 8,  # 机构持股变化
                "gini_coefficient_score": 10,  # 基尼系数
                "locked_chips_ratio_score": 7,  # 筹码锁定率
                
                # 成交结构 (25%)
                "large_order_bid_ask_ratio_score": 10,  # 大单买卖比
                "large_order_proportion_score": 8,  # 大单占比
                "block_trade_characteristics_score": 7  # 大宗交易特征
            }
        }
    def analyze(self, 
                stock_data: pd.DataFrame, 
                stock_meta: StockMeta, 
                market_context: MarketContext,
                **kwargs) -> AnalysisResult:
        """
        分析股票筹码结构特征
        
        Args:
            stock_data: 包含交易数据、筹码数据的DataFrame
            stock_meta: 股票元信息
            market_context: 市场环境上下文
            
        Returns:
            分析结果
        """
        logger.info(f"开始分析 {stock_meta.code} 的筹码结构特征")
        
        # 确保数据按日期排序
        stock_data = stock_data.sort_values('date').reset_index(drop=True)
        
        # 确保必要的列存在
        required_columns = ['date', 'close', 'volume', 'amount', 'turnover_rate', 
                           'large_order_buy', 'large_order_sell']
        
        # 检查哪些列是可选的（可能不存在）
        optional_columns = ['shareholders_count', 'institution_holding_ratio',
                           'gini_coefficient', 'locked_chips_ratio', 'closing_turnover',
                           'block_trade_amount', 'block_trade_discount']
        
        missing_cols = [col for col in required_columns if col not in stock_data.columns]
        if missing_cols:
            logger.error(f"缺少必要的列: {missing_cols}")
            raise ValueError(f"数据缺少必要的列: {missing_cols}")
        
        # 记录哪些可选列不存在，用于后续逻辑判断
        missing_optional_cols = [col for col in optional_columns if col not in stock_data.columns]
        if missing_optional_cols:
            logger.warning(f"缺少可选列: {missing_optional_cols}")
        
        # 计算各项指标
        # 1. 换手特征分析 (35%)
        self._analyze_turnover_features(stock_data)
        
        # 2. 筹码集中度分析 (40%)
        self._analyze_chip_concentration(stock_data, stock_meta)
        
        # 3. 成交结构分析 (25%)
        self._analyze_trading_structure(stock_data)
        
        # 计算总分
        self.score = self._calculate_weighted_score()
        
        # 生成分析描述
        self._generate_description()
        
        # 生成详细分析信息
        self._generate_detail_info(stock_data, stock_meta)
        
        # 生成图表数据
        self._generate_charts_data(stock_data)
        
        return self.get_result()
    
    def _analyze_turnover_features(self, stock_data: pd.DataFrame) -> None:
        """
        分析换手特征
        
        Args:
            stock_data: 股票数据
        """
        # 获取最近交易日的数据
        recent_days = min(20, len(stock_data))
        recent_data = stock_data.tail(recent_days).copy()
        
        # ----- 换手率范围评估 -----
        # 计算最近交易日的平均换手率
        avg_turnover_rate = recent_data['turnover_rate'].mean()
        
        # 判断换手率是否在理想范围内
        turnover_in_range = (self.config["turnover_rate_min"] <= avg_turnover_rate <= self.config["turnover_rate_max"])
        
        # ----- 换手率稳定性评估 -----
        # 计算换手率的波动系数（标准差/均值）
        turnover_std = recent_data['turnover_rate'].std()
        turnover_stability = turnover_std / avg_turnover_rate if avg_turnover_rate > 0 else float('inf')
        
        # 判断换手率稳定性是否良好
        turnover_stable = turnover_stability <= self.config["turnover_stability_max"]
        
        # ----- 换手率趋势评估 -----
        # 计算换手率的趋势（使用简单的线性回归）
        x = np.arange(len(recent_data))
        y = recent_data['turnover_rate'].values
        
        if len(x) > 1:  # 确保有足够的数据进行回归
            turnover_slope = np.polyfit(x, y, 1)[0]
        else:
            turnover_slope = 0
        
        # 判断换手率趋势，正斜率为上升趋势，负斜率为下降趋势
        turnover_trend = 'increasing' if turnover_slope > 0.01 else ('decreasing' if turnover_slope < -0.01 else 'stable')
        
        # ----- 尾盘换手占比 -----
        closing_turnover_ratio = 0.0
        
        if 'closing_turnover' in recent_data.columns:
            # 如果有尾盘换手数据，直接计算占比
            closing_turnover_sum = recent_data['closing_turnover'].sum()
            total_turnover_sum = recent_data['turnover_rate'].sum()
            
            if total_turnover_sum > 0:
                closing_turnover_ratio = closing_turnover_sum / total_turnover_sum
        else:
            # 如果没有尾盘换手数据，可以通过尾盘成交量/总成交量估算
            if 'closing_volume' in recent_data.columns:
                closing_volume_sum = recent_data['closing_volume'].sum()
                total_volume_sum = recent_data['volume'].sum()
                
                if total_volume_sum > 0:
                    closing_turnover_ratio = closing_volume_sum / total_volume_sum
            else:
                # 如果没有尾盘成交量数据，则根据资金流向估算
                if 'closing_fund_flow' in recent_data.columns and 'fund_flow' in recent_data.columns:
                    closing_flow_sum = recent_data['closing_fund_flow'].abs().sum()
                    total_flow_sum = recent_data['fund_flow'].abs().sum()
                    
                    if total_flow_sum > 0:
                        closing_turnover_ratio = closing_flow_sum / total_flow_sum
                else:
                    # 没有任何相关数据，使用中等估计值
                    closing_turnover_ratio = 0.2  # 默认尾盘占全天20%
        
        # 判断尾盘换手占比是否达标
        closing_turnover_good = closing_turnover_ratio >= self.config["closing_turnover_ratio_min"]
        
        # 存储指标值
        self.indicators.update({
            "avg_turnover_rate": avg_turnover_rate,
            "turnover_in_range": turnover_in_range,
            "turnover_stability": turnover_stability,
            "turnover_stable": turnover_stable,
            "turnover_trend": turnover_trend,
            "closing_turnover_ratio": closing_turnover_ratio,
            "closing_turnover_good": closing_turnover_good,
        })
        
        # 计算各项指标得分
        # 换手率范围得分
        if turnover_in_range:
            # 在理想范围内，接近中间值得分更高
            mid_turnover = (self.config["turnover_rate_min"] + self.config["turnover_rate_max"]) / 2
            distance_from_mid = abs(avg_turnover_rate - mid_turnover) / (self.config["turnover_rate_max"] - self.config["turnover_rate_min"]) * 2
            turnover_rate_range_score = 80 + (1 - distance_from_mid) * 20
        elif avg_turnover_rate < self.config["turnover_rate_min"]:
            # 换手率过低，按比例计分
            turnover_rate_range_score = 50 * avg_turnover_rate / self.config["turnover_rate_min"]
        else:
            # 换手率过高，按比例扣分
            excess_ratio = (avg_turnover_rate - self.config["turnover_rate_max"]) / self.config["turnover_rate_max"]
            turnover_rate_range_score = 70 - excess_ratio * 40
        
        # 限制范围
        turnover_rate_range_score = max(0, min(turnover_rate_range_score, 100))
        
        # 换手率稳定性得分
        if turnover_stability <= self.config["turnover_stability_max"]:
            # 稳定性好，按比例得分
            stability_ratio = turnover_stability / self.config["turnover_stability_max"]
            turnover_stability_score = 70 + (1 - stability_ratio) * 30
        else:
            # 稳定性差，按超出倍数扣分
            excess_ratio = (turnover_stability - self.config["turnover_stability_max"]) / self.config["turnover_stability_max"]
            turnover_stability_score = 70 - excess_ratio * 50
        
        # 限制范围
        turnover_stability_score = max(0, min(turnover_stability_score, 100))
        
        # 换手率趋势得分
        if turnover_trend == 'increasing':
            # 上升趋势不太理想
            turnover_trend_score = 50 - turnover_slope * 500  # 假设斜率不会太大
        elif turnover_trend == 'decreasing':
            # 下降趋势较好
            turnover_trend_score = 70 - turnover_slope * 300  # 为负值，所以是加分
        else:
            # 稳定趋势最好
            turnover_trend_score = 85
        
        # 限制范围
        turnover_trend_score = max(30, min(turnover_trend_score, 100))
        
        # 尾盘换手占比得分
        if closing_turnover_ratio >= self.config["closing_turnover_ratio_min"]:
            # 尾盘换手占比好，按超出比例得分
            excess_ratio = (closing_turnover_ratio - self.config["closing_turnover_ratio_min"]) / self.config["closing_turnover_ratio_min"]
            closing_turnover_ratio_score = 70 + excess_ratio * 30
        else:
            # 尾盘换手占比低，按差距比例扣分
            gap_ratio = (self.config["closing_turnover_ratio_min"] - closing_turnover_ratio) / self.config["closing_turnover_ratio_min"]
            closing_turnover_ratio_score = 70 - gap_ratio * 50
        
        # 限制范围
        closing_turnover_ratio_score = max(0, min(closing_turnover_ratio_score, 100))
        
        # 存储指标得分
        self.indicator_scores.update({
            "turnover_rate_range_score": turnover_rate_range_score,
            "turnover_stability_score": turnover_stability_score,
            "turnover_trend_score": turnover_trend_score,
            "closing_turnover_ratio_score": closing_turnover_ratio_score,
        })
    
    def _analyze_chip_concentration(self, stock_data: pd.DataFrame, stock_meta: StockMeta) -> None:
        """
        分析筹码集中度
        
        Args:
            stock_data: 股票数据
            stock_meta: 股票元信息
        """
        # 获取最近交易日的数据
        recent_days = min(60, len(stock_data))  # 使用较长时间窗口分析筹码变化
        recent_data = stock_data.tail(recent_days).copy()
        
        # ----- 股东户数变化 -----
        shareholders_decrease = 0.0
        
        if 'shareholders_count' in recent_data.columns:
            # 如果有股东户数数据，计算变化率
            if len(recent_data) >= 2:
                start_count = recent_data['shareholders_count'].iloc[0]
                end_count = recent_data['shareholders_count'].iloc[-1]
                
                if start_count > 0:
                    shareholders_decrease = (start_count - end_count) / start_count * 100
            
            # 判断股东户数是否显著减少
            significant_decrease = shareholders_decrease >= self.config["shareholders_decrease_min"]
        else:
            # 没有股东户数数据，使用其他指标估计
            significant_decrease = False
        
        # ----- 户均持股变化 -----
        avg_holding_increase = 0.0
        
        if 'shareholders_count' in recent_data.columns and stock_meta.float_shares > 0:
            # 如果有股东户数数据，计算户均持股变化
            if len(recent_data) >= 2:
                start_count = recent_data['shareholders_count'].iloc[0]
                end_count = recent_data['shareholders_count'].iloc[-1]
                
                if start_count > 0 and end_count > 0:
                    start_avg_holding = stock_meta.float_shares * 100000000 / start_count  # 转换为股
                    end_avg_holding = stock_meta.float_shares * 100000000 / end_count
                    
                    avg_holding_increase = (end_avg_holding - start_avg_holding) / start_avg_holding * 100
            
            # 判断户均持股是否显著增加
            significant_increase = avg_holding_increase >= self.config["avg_holding_increase_min"]
        else:
            # 没有足够数据，使用其他指标估计
            significant_increase = False
        
        # ----- 机构持股变化 -----
        institution_holding_increase = 0.0
        
        if 'institution_holding_ratio' in recent_data.columns:
            # 如果有机构持股数据，计算变化
            if len(recent_data) >= 2:
                start_ratio = recent_data['institution_holding_ratio'].iloc[0]
                end_ratio = recent_data['institution_holding_ratio'].iloc[-1]
                
                institution_holding_increase = end_ratio - start_ratio  # 百分比变化
            
            # 判断机构持股是否显著增加
            institution_increase = institution_holding_increase >= self.config["institution_holding_increase_min"]
        else:
            # 没有机构持股数据，使用其他指标估计
            # 可以通过大单净流入、北向资金等间接估计
            if 'large_order_net_inflow' in recent_data.columns:
                net_inflow_sum = recent_data['large_order_net_inflow'].sum()
                if net_inflow_sum > 0:
                    # 大单净流入为正，可能有机构增持
                    institution_increase = True
                else:
                    institution_increase = False
            else:
                # 无法估计
                institution_increase = False
        
        # ----- 基尼系数变化 -----
        gini_coefficient_increase = 0.0
        
        if 'gini_coefficient' in recent_data.columns:
            # 如果有基尼系数数据，计算变化
            if len(recent_data) >= 2:
                start_gini = recent_data['gini_coefficient'].iloc[0]
                end_gini = recent_data['gini_coefficient'].iloc[-1]
                
                gini_coefficient_increase = end_gini - start_gini
            
            # 判断基尼系数是否显著增加（筹码集中度提高）
            gini_increase = gini_coefficient_increase >= self.config["gini_coefficient_increase_min"]
        else:
            # 没有基尼系数数据，使用股东户数和大单数据估计
            if significant_decrease and 'large_order_net_inflow' in recent_data.columns:
                net_inflow_sum = recent_data['large_order_net_inflow'].sum()
                if net_inflow_sum > 0:
                    # 股东户数减少且大单净流入为正，可能筹码集中度提高
                    gini_increase = True
                else:
                    gini_increase = False
            else:
                # 无法估计
                gini_increase = False
        
        # ----- 筹码锁定率 -----
        locked_chips_ratio = 0.0
        
        if 'locked_chips_ratio' in recent_data.columns:
            # 直接获取最新的筹码锁定率
            locked_chips_ratio = recent_data['locked_chips_ratio'].iloc[-1]
        else:
            # 估计筹码锁定率
            # 可以通过换手率倒数估计平均持有天数，进而估计锁定率
            if 'turnover_rate' in recent_data.columns:
                avg_turnover = recent_data['turnover_rate'].mean()
                if avg_turnover > 0:
                    # 估计180天内未换手的筹码比例
                    locked_chips_ratio = max(0, 1 - min(1, 180 * avg_turnover / 100))
        
        # 判断筹码锁定率是否达标
        chips_locked = locked_chips_ratio >= self.config["locked_chips_ratio_min"]
        
        # 存储指标值
        self.indicators.update({
            "shareholders_decrease": shareholders_decrease,
            "significant_decrease": significant_decrease,
            "avg_holding_increase": avg_holding_increase,
            "significant_increase": significant_increase,
            "institution_holding_increase": institution_holding_increase,
            "institution_increase": institution_increase,
            "gini_coefficient_increase": gini_coefficient_increase,
            "gini_increase": gini_increase,
            "locked_chips_ratio": locked_chips_ratio,
            "chips_locked": chips_locked,
        })
        
        # 计算各项指标得分
        # 股东户数减少得分
        if shareholders_decrease >= self.config["shareholders_decrease_min"]:
            # 显著减少，按超出比例得分
            excess_ratio = (shareholders_decrease - self.config["shareholders_decrease_min"]) / self.config["shareholders_decrease_min"]
            shareholders_decrease_score = 70 + excess_ratio * 30
        else:
            # 未显著减少，按差距比例扣分
            gap_ratio = (self.config["shareholders_decrease_min"] - shareholders_decrease) / self.config["shareholders_decrease_min"]
            shareholders_decrease_score = 70 - gap_ratio * 40
        
        # 限制范围
        shareholders_decrease_score = max(0, min(shareholders_decrease_score, 100))
        
        # 户均持股增加得分
        if avg_holding_increase >= self.config["avg_holding_increase_min"]:
            # 显著增加，按超出比例得分
            excess_ratio = (avg_holding_increase - self.config["avg_holding_increase_min"]) / self.config["avg_holding_increase_min"]
            avg_holding_increase_score = 70 + excess_ratio * 30
        else:
            # 未显著增加，按差距比例扣分
            gap_ratio = (self.config["avg_holding_increase_min"] - avg_holding_increase) / self.config["avg_holding_increase_min"]
            avg_holding_increase_score = 70 - gap_ratio * 40
        
        # 限制范围
        avg_holding_increase_score = max(0, min(avg_holding_increase_score, 100))
        
        # 机构持股变化得分
        if institution_holding_increase >= self.config["institution_holding_increase_min"]:
            # 显著增加，按超出比例得分
            excess_ratio = (institution_holding_increase - self.config["institution_holding_increase_min"]) / self.config["institution_holding_increase_min"]
            institution_holding_score = 70 + excess_ratio * 30
        else:
            # 未显著增加，按差距比例扣分
            if institution_holding_increase < 0:
                # 机构减持，严重扣分
                institution_holding_score = 40 + institution_holding_increase * 10
            else:
                gap_ratio = (self.config["institution_holding_increase_min"] - institution_holding_increase) / self.config["institution_holding_increase_min"]
                institution_holding_score = 70 - gap_ratio * 30
        
        # 限制范围
        institution_holding_score = max(0, min(institution_holding_score, 100))
        
        # 基尼系数变化得分
        if gini_coefficient_increase >= self.config["gini_coefficient_increase_min"]:
            # 显著增加，按超出比例得分
            excess_ratio = (gini_coefficient_increase - self.config["gini_coefficient_increase_min"]) / self.config["gini_coefficient_increase_min"]
            gini_coefficient_score = 70 + excess_ratio * 30
        else:
            # 未显著增加，按差距比例扣分
            if gini_coefficient_increase < 0:
                # 基尼系数下降，严重扣分（筹码分散）
                gini_coefficient_score = 50 + gini_coefficient_increase * 200
            else:
                gap_ratio = (self.config["gini_coefficient_increase_min"] - gini_coefficient_increase) / self.config["gini_coefficient_increase_min"]
                gini_coefficient_score = 70 - gap_ratio * 30
        
        # 限制范围
        gini_coefficient_score = max(0, min(gini_coefficient_score, 100))
        
        # 筹码锁定率得分
        if locked_chips_ratio >= self.config["locked_chips_ratio_min"]:
            # 达标，按超出比例得分
            excess_ratio = (locked_chips_ratio - self.config["locked_chips_ratio_min"]) / (1 - self.config["locked_chips_ratio_min"])
            locked_chips_ratio_score = 70 + excess_ratio * 30
        else:
            # 未达标，按差距比例扣分
            gap_ratio = (self.config["locked_chips_ratio_min"] - locked_chips_ratio) / self.config["locked_chips_ratio_min"]
            locked_chips_ratio_score = 70 - gap_ratio * 40
        
        # 限制范围
        locked_chips_ratio_score = max(0, min(locked_chips_ratio_score, 100))
        
        # 存储指标得分
        self.indicator_scores.update({
            "shareholders_decrease_score": shareholders_decrease_score,
            "avg_holding_increase_score": avg_holding_increase_score,
            "institution_holding_score": institution_holding_score,
            "gini_coefficient_score": gini_coefficient_score,
            "locked_chips_ratio_score": locked_chips_ratio_score,
        })

    def _analyze_trading_structure(self, stock_data: pd.DataFrame) -> None:
        """
        分析成交结构
        
        Args:
            stock_data: 股票数据
        """
        # 获取最近交易日的数据
        recent_days = min(20, len(stock_data))
        recent_data = stock_data.tail(recent_days).copy()
        
        # ----- 大单买卖比 -----
        large_order_bid_ask_ratio = 0.0
        
        if 'large_order_buy' in recent_data.columns and 'large_order_sell' in recent_data.columns:
            # 计算大单买入与卖出的比值
            total_buy = recent_data['large_order_buy'].sum()
            total_sell = recent_data['large_order_sell'].sum()
            
            if total_sell > 0:
                large_order_bid_ask_ratio = total_buy / total_sell
        
        # 判断大单买卖比是否达标
        bid_ask_ratio_good = large_order_bid_ask_ratio >= self.config["large_order_bid_ask_ratio_min"]
        
        # ----- 大单占比变化 -----
        large_order_proportion = 0.0
        large_order_proportion_increase = 0.0
        
        if 'large_order_buy' in recent_data.columns and 'large_order_sell' in recent_data.columns and 'amount' in recent_data.columns:
            # 计算大单成交总额占总成交额的比例
            total_large_order = recent_data['large_order_buy'].sum() + recent_data['large_order_sell'].sum()
            total_amount = recent_data['amount'].sum() * 2  # 买卖双边计算
            
            if total_amount > 0:
                large_order_proportion = total_large_order / total_amount * 100
            
            # 计算大单占比的变化趋势
            if len(recent_data) >= 2:
                # 将数据分为前后两段
                half = len(recent_data) // 2
                first_half = recent_data.iloc[:half]
                second_half = recent_data.iloc[half:]
                
                # 计算前后两段的大单占比
                first_large_order = first_half['large_order_buy'].sum() + first_half['large_order_sell'].sum()
                first_amount = first_half['amount'].sum() * 2
                
                second_large_order = second_half['large_order_buy'].sum() + second_half['large_order_sell'].sum()
                second_amount = second_half['amount'].sum() * 2
                
                if first_amount > 0 and second_amount > 0:
                    first_proportion = first_large_order / first_amount * 100
                    second_proportion = second_large_order / second_amount * 100
                    
                    large_order_proportion_increase = second_proportion - first_proportion
        
        # 判断大单占比是否显著增加
        proportion_increase_good = large_order_proportion_increase >= self.config["large_order_proportion_increase_min"]
        
        # ----- 大宗交易特征 -----
        has_block_trade = False
        avg_block_trade_discount = 0.0
        block_trade_discount_good = False
        
        if 'block_trade_amount' in recent_data.columns:
            # 判断是否有大宗交易
            total_block_trade = recent_data['block_trade_amount'].sum()
            has_block_trade = total_block_trade > 0
            
            # 如果有大宗交易且有折价率数据
            if has_block_trade and 'block_trade_discount' in recent_data.columns:
                # 计算平均折价率
                valid_discounts = recent_data[recent_data['block_trade_amount'] > 0]['block_trade_discount']
                if len(valid_discounts) > 0:
                    avg_block_trade_discount = valid_discounts.mean()
                    
                    # 判断折价率是否合理（较低的折价率更好）
                    block_trade_discount_good = avg_block_trade_discount <= self.config["block_trade_discount_max"]
        
        # 存储指标值
        self.indicators.update({
            "large_order_bid_ask_ratio": large_order_bid_ask_ratio,
            "bid_ask_ratio_good": bid_ask_ratio_good,
            "large_order_proportion": large_order_proportion,
            "large_order_proportion_increase": large_order_proportion_increase,
            "proportion_increase_good": proportion_increase_good,
            "has_block_trade": has_block_trade,
            "avg_block_trade_discount": avg_block_trade_discount,
            "block_trade_discount_good": block_trade_discount_good,
        })
        
        # 计算各项指标得分
        # 大单买卖比得分
        if large_order_bid_ask_ratio >= self.config["large_order_bid_ask_ratio_min"]:
            # 大单买卖比达标，按超出比例得分
            excess_ratio = (large_order_bid_ask_ratio - self.config["large_order_bid_ask_ratio_min"]) / self.config["large_order_bid_ask_ratio_min"]
            large_order_bid_ask_ratio_score = 70 + min(30, excess_ratio * 30)
        else:
            # 大单买卖比不达标，按差距比例扣分
            if large_order_bid_ask_ratio > 0:
                gap_ratio = (self.config["large_order_bid_ask_ratio_min"] - large_order_bid_ask_ratio) / self.config["large_order_bid_ask_ratio_min"]
                large_order_bid_ask_ratio_score = 70 - gap_ratio * 50
            else:
                large_order_bid_ask_ratio_score = 20  # 无法计算或极低值给予基础分
        
        # 限制范围
        large_order_bid_ask_ratio_score = max(0, min(large_order_bid_ask_ratio_score, 100))
        
        # 大单占比得分
        # 结合大单占比和增长幅度评分
        large_order_proportion_score = 0.0
        
        if large_order_proportion > 30:
            # 大单占比较高，基础分60
            base_score = 60
            
            # 根据增长幅度加分
            if large_order_proportion_increase >= self.config["large_order_proportion_increase_min"]:
                growth_bonus = (large_order_proportion_increase / self.config["large_order_proportion_increase_min"]) * 20
                growth_bonus = min(40, growth_bonus)  # 最多加40分
            else:
                # 增长不足，根据差距扣分
                growth_bonus = (large_order_proportion_increase / self.config["large_order_proportion_increase_min"]) * 10
            
            large_order_proportion_score = base_score + growth_bonus
        else:
            # 大单占比较低，基础分40
            base_score = 40
            
            # 根据增长幅度加分
            if large_order_proportion_increase >= self.config["large_order_proportion_increase_min"]:
                growth_bonus = (large_order_proportion_increase / self.config["large_order_proportion_increase_min"]) * 30
                growth_bonus = min(50, growth_bonus)  # 最多加50分
            else:
                growth_bonus = 0
            
            large_order_proportion_score = base_score + growth_bonus
        
        # 限制范围
        large_order_proportion_score = max(0, min(large_order_proportion_score, 100))
        
        # 大宗交易特征得分
        block_trade_characteristics_score = 0.0
        
        if has_block_trade:
            # 有大宗交易，根据折价率打分
            if block_trade_discount_good:
                # 折价率较低，得高分
                discount_score = 80 - (avg_block_trade_discount / self.config["block_trade_discount_max"]) * 20
            else:
                # 折价率较高，得较低分
                excess_discount = avg_block_trade_discount - self.config["block_trade_discount_max"]
                discount_score = 60 - min(40, excess_discount * 4)
            
            block_trade_characteristics_score = discount_score
        else:
            # 无大宗交易，给予中等分数
            block_trade_characteristics_score = 50
        
        # 限制范围
        block_trade_characteristics_score = max(0, min(block_trade_characteristics_score, 100))
        
        # 存储指标得分
        self.indicator_scores.update({
            "large_order_bid_ask_ratio_score": large_order_bid_ask_ratio_score,
            "large_order_proportion_score": large_order_proportion_score,
            "block_trade_characteristics_score": block_trade_characteristics_score,
        })


