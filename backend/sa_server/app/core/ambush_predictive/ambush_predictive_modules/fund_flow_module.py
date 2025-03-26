"""
资金流入特征模块
分析股票的资金流入特征，判断是否存在资金埋伏迹象
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import logging

from app.core.ambush_predictive.base_module import AnalysisModule
from app.core.ambush_predictive.data_models import StockMeta, MarketContext, AnalysisResult

logger = logging.getLogger('fund_burying_system')


class FundFlowModule(AnalysisModule):
    """资金流入特征模块"""
    
    def __init__(self, weight: float = 0.30):
        """
        初始化模块
        
        Args:
            weight: 模块权重，默认为30%
        """
        super().__init__(name="fund_flow_module", weight=weight)
        self.description = "分析股票资金流入特征，包括持续性、资金质量和量价关系"
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            # 持续性指标配置
            "continuous_days_min": 10,  # 最小连续资金流入天数
            "net_inflow_days_ratio_min": 0.75,  # 最小净流入天数比例
            "net_inflow_market_cap_ratio": {
                "small_cap": 0.01,  # 小市值股票(流通市值<50亿)
                "mid_cap": 0.006,   # 中市值股票(流通市值50-200亿)
                "large_cap": 0.003   # 大市值股票(流通市值>200亿)
            },
            "price_inflow_correlation_max": 0.25,  # 价格与资金流入最大相关系数
            
            # 资金流入节奏配置
            "closing_inflow_ratio_min": 0.38,  # 最小尾盘资金占比
            "inflow_volatility_max": 0.4,  # 资金流入波动系数最大值
            "active_buy_ratio_min": 0.70,  # 最小主动性买盘比例
            
            # 资金规模适配性配置
            "large_order_ratio_min": 0.4,  # 最小大单成交占比
            "daily_fund_turnover_ratio_min": 0.08,  # 日均资金流入占日均成交额最小比例
            "inflow_acceleration_min": 0.4,  # 最小资金流入加速度
            
            # 指标权重配置
            "indicator_weights": {
                # 多维资金流向分析 (权重50%)
                "continuous_inflow_score": 10,  # 持续性指标
                "inflow_to_cap_ratio_score": 10,  # 累计净流入占流通市值比例
                "price_inflow_correlation_score": 10,  # 资金流入与股价相关性
                "closing_inflow_ratio_score": 10,  # 尾盘资金占比
                "inflow_volatility_score": 5,  # 资金流入稳定性
                "active_buy_ratio_score": 5,  # 主动性买盘比例
                
                # 资金质量分析 (权重30%)
                "fund_style_score": 10,  # 资金来源与建仓风格
                "inflow_acceleration_score": 10,  # 资金流入加速度
                "inflow_recent_ratio_score": 10,  # 近期资金流入占比
                
                # 量价互动特征 (权重20%)
                "volume_price_divergence_score": 10,  # 量价背离度
                "support_level_buying_score": 5,  # 支撑位大单买入
                "breakthrough_fund_accumulation_score": 5  # 突破前资金蓄势
            }
        }
    
    def analyze(self, 
                stock_data: pd.DataFrame, 
                stock_meta: StockMeta, 
                market_context: MarketContext,
                **kwargs) -> AnalysisResult:
        """
        分析股票资金流入特征
        
        Args:
            stock_data: 包含交易数据、资金流向数据的DataFrame
            stock_meta: 股票元信息
            market_context: 市场环境上下文
            
        Returns:
            分析结果
        """
        logger.info(f"开始分析 {stock_meta.code} 的资金流入特征")
        
        # 确保数据按日期排序
        stock_data = stock_data.sort_values('date').reset_index(drop=True)
        
        # 确保必要的列存在
        required_columns = ['date', 'close', 'volume', 'amount', 'fund_flow', 
                           'large_order_net_inflow', 'large_order_buy', 'large_order_sell',
                           'closing_fund_flow', 'active_buy_ratio']
        
        missing_cols = [col for col in required_columns if col not in stock_data.columns]
        if missing_cols:
            logger.error(f"缺少必要的列: {missing_cols}")
            raise ValueError(f"数据缺少必要的列: {missing_cols}")
        
        # 计算各项指标
        # 1. 多维资金流向分析 (50%)
        self._analyze_fund_flow_direction(stock_data, stock_meta)
        
        # 2. 资金质量分析 (30%)
        self._analyze_fund_quality(stock_data, stock_meta)
        
        # 3. 量价互动特征 (20%)
        self._analyze_volume_price_interaction(stock_data, stock_meta)
        
        # 计算总分
        self.score = self._calculate_weighted_score()
        
        # 生成分析描述
        self._generate_description()
        
        # 生成详细分析信息
        self._generate_detail_info(stock_data, stock_meta)
        
        # 生成图表数据
        self._generate_charts_data(stock_data)
        
        return self.get_result()
    
    def _analyze_fund_flow_direction(self, stock_data: pd.DataFrame, stock_meta: StockMeta) -> None:
        """
        分析资金流向特征
        
        Args:
            stock_data: 股票数据
            stock_meta: 股票元信息
        """
        # 获取最近交易日的数据(通常是20个交易日)
        recent_days = min(20, len(stock_data))
        recent_data = stock_data.tail(recent_days).copy()
        
        # ----- 持续性指标 -----
        # 计算连续净流入天数
        recent_data['is_inflow'] = recent_data['fund_flow'] > 0
        continuous_inflow_days = recent_data['is_inflow'].sum()
        
        # 计算净流入天数比例
        inflow_days_ratio = continuous_inflow_days / recent_days
        
        # 计算累计净流入
        total_inflow = recent_data['fund_flow'].sum()
        
        # 计算累计净流入占流通市值比例
        market_cap = stock_meta.market_cap * 100000000  # 转换为元
        inflow_to_cap_ratio = total_inflow / market_cap * 100  # 转换为百分比
        
        # 确定市值类别
        cap_type = "small_cap"
        if stock_meta.market_cap >= 50 and stock_meta.market_cap < 200:
            cap_type = "mid_cap"
        elif stock_meta.market_cap >= 200:
            cap_type = "large_cap"
        
        # 根据市值类别获取阈值
        inflow_cap_threshold = self.config["net_inflow_market_cap_ratio"][cap_type]
        
        # 计算价格与资金流入的相关性
        price_series = recent_data['close']
        inflow_series = recent_data['fund_flow']
        price_inflow_correlation = price_series.corr(inflow_series)
        
        # ----- 资金流入节奏 -----
        # 计算尾盘资金占比
        total_closing_inflow = recent_data['closing_fund_flow'].sum()
        closing_inflow_ratio = total_closing_inflow / total_inflow if total_inflow > 0 else 0
        
        # 计算资金流入波动系数
        inflow_mean = recent_data['fund_flow'].mean()
        inflow_std = recent_data['fund_flow'].std()
        inflow_volatility = inflow_std / inflow_mean if inflow_mean > 0 else float('inf')
        
        # 计算主动性买盘比例
        active_buy_ratio = recent_data['active_buy_ratio'].mean()
        
        # 存储指标值
        self.indicators.update({
            "continuous_inflow_days": continuous_inflow_days,
            "inflow_days_ratio": inflow_days_ratio,
            "total_inflow": total_inflow,
            "inflow_to_cap_ratio": inflow_to_cap_ratio,
            "price_inflow_correlation": price_inflow_correlation,
            "closing_inflow_ratio": closing_inflow_ratio,
            "inflow_volatility": inflow_volatility,
            "active_buy_ratio": active_buy_ratio,
        })
        
        # 计算指标得分
        # 持续性指标得分
        config = self.config
        continuous_inflow_score = self._normalize_score(
            continuous_inflow_days, 
            config["continuous_days_min"] * 0.5, 
            config["continuous_days_min"] * 1.5
        )
        
        # 净流入天数比例得分
        inflow_days_ratio_score = self._normalize_score(
            inflow_days_ratio,
            config["net_inflow_days_ratio_min"] * 0.7,
            config["net_inflow_days_ratio_min"] * 1.3
        )
        
        # 资金流入占市值比例得分
        inflow_to_cap_ratio_score = self._normalize_score(
            inflow_to_cap_ratio,
            inflow_cap_threshold * 0.5,
            inflow_cap_threshold * 2.0
        )
        
        # 价格与资金流入相关性得分 (越低越好)
        price_inflow_correlation_score = self._normalize_score(
            config["price_inflow_correlation_max"] - price_inflow_correlation,
            0,
            config["price_inflow_correlation_max"] * 2
        )
        
        # 尾盘资金占比得分
        closing_inflow_ratio_score = self._normalize_score(
            closing_inflow_ratio,
            config["closing_inflow_ratio_min"] * 0.7,
            config["closing_inflow_ratio_min"] * 1.5
        )
        
        # 资金流入稳定性得分 (波动系数越低越好)
        inflow_volatility_score = self._normalize_score(
            config["inflow_volatility_max"] - inflow_volatility,
            -config["inflow_volatility_max"],
            config["inflow_volatility_max"]
        )
        
        # 主动性买盘比例得分
        active_buy_ratio_score = self._normalize_score(
            active_buy_ratio,
            config["active_buy_ratio_min"] * 0.8,
            config["active_buy_ratio_min"] * 1.2
        )
        
        # 存储指标得分
        self.indicator_scores.update({
            "continuous_inflow_score": continuous_inflow_score,
            "inflow_days_ratio_score": (continuous_inflow_score + inflow_days_ratio_score) / 2,
            "inflow_to_cap_ratio_score": inflow_to_cap_ratio_score,
            "price_inflow_correlation_score": price_inflow_correlation_score,
            "closing_inflow_ratio_score": closing_inflow_ratio_score,
            "inflow_volatility_score": inflow_volatility_score,
            "active_buy_ratio_score": active_buy_ratio_score,
        })
    
    def _analyze_fund_quality(self, stock_data: pd.DataFrame, stock_meta: StockMeta) -> None:
        """
        分析资金质量
        
        Args:
            stock_data: 股票数据
            stock_meta: 股票元信息
        """
        # 获取最近交易日的数据
        recent_days = min(20, len(stock_data))
        recent_data = stock_data.tail(recent_days).copy()
        
        # ----- 资金来源与建仓风格 -----
        # 计算大单占比
        if 'large_order_volume' in recent_data.columns and 'volume' in recent_data.columns:
            large_order_ratio = recent_data['large_order_volume'].sum() / recent_data['volume'].sum()
        else:
            # 如果没有直接的大单量，通过大单金额/成交金额估算
            large_order_buy = recent_data['large_order_buy'].sum()
            large_order_sell = recent_data['large_order_sell'].sum()
            total_amount = recent_data['amount'].sum()
            large_order_ratio = (large_order_buy + large_order_sell) / (2 * total_amount) if total_amount > 0 else 0
        
        # 计算大单买卖比
        large_order_buy_sell_ratio = recent_data['large_order_buy'].sum() / recent_data['large_order_sell'].sum() if recent_data['large_order_sell'].sum() > 0 else float('inf')
        
        # 资金建仓风格判断
        fund_style = "unknown"
        fund_style_score = 50.0  # 默认中等分数
        
        # 游资特征: 资金波动大，大单买卖比高，集中在某几天
        if self.indicators["inflow_volatility"] > 0.6 and large_order_buy_sell_ratio > 2.0:
            fund_style = "retail"  # 游资风格
            fund_style_score = 70.0 if self.indicators["inflow_to_cap_ratio"] > self.config["net_inflow_market_cap_ratio"]["small_cap"] else 50.0
        
        # 机构特征: 资金稳定流入，波动小，尾盘资金比例高
        elif (self.indicators["inflow_volatility"] < 0.4 and 
              self.indicators["closing_inflow_ratio"] > 0.35 and 
              self.indicators["continuous_inflow_days"] >= 10):
            fund_style = "institutional"  # 机构风格
            fund_style_score = 85.0
        
        # 北向资金特征: 持续性强，大单比例高，主动性买盘比例适中
        elif (self.indicators["inflow_days_ratio"] > 0.8 and 
              large_order_ratio > 0.5 and 
              0.6 <= self.indicators["active_buy_ratio"] <= 0.8):
            fund_style = "northbound"  # 北向资金风格
            fund_style_score = 90.0
        
        # ----- 资金流入加速度 -----
        # 分析前后两个时间段的资金流入
        half_window = recent_days // 2
        if half_window > 1:
            first_half = recent_data.iloc[:half_window]
            second_half = recent_data.iloc[half_window:]
            
            first_half_inflow = first_half['fund_flow'].sum()
            second_half_inflow = second_half['fund_flow'].sum()
            
            # 计算资金流入加速度 (后半段占总流入的比例)
            inflow_acceleration = second_half_inflow / (first_half_inflow + second_half_inflow) if (first_half_inflow + second_half_inflow) > 0 else 0
        else:
            inflow_acceleration = 0.5  # 数据不足，默认为平稳
        
        # 计算近期资金流入占比 (最近5天占整个周期的比例)
        recent_5d = min(5, len(recent_data))
        recent_5d_inflow = recent_data.tail(recent_5d)['fund_flow'].sum()
        recent_5d_ratio = recent_5d_inflow / recent_data['fund_flow'].sum() if recent_data['fund_flow'].sum() > 0 else 0
        
        # 存储指标值
        self.indicators.update({
            "large_order_ratio": large_order_ratio,
            "large_order_buy_sell_ratio": large_order_buy_sell_ratio,
            "fund_style": fund_style,
            "inflow_acceleration": inflow_acceleration,
            "recent_5d_inflow_ratio": recent_5d_ratio,
        })
        
        # 计算指标得分
        # 大单占比得分
        large_order_ratio_score = self._normalize_score(
            large_order_ratio,
            self.config["large_order_ratio_min"] * 0.7,
            self.config["large_order_ratio_min"] * 1.5
        )
        
        # 资金建仓风格得分
        # 已在上面计算
        
        # 资金流入加速度得分
        inflow_acceleration_score = self._normalize_score(
            inflow_acceleration,
            self.config["inflow_acceleration_min"] * 0.7,
            self.config["inflow_acceleration_min"] * 1.5
        )
        
        # 近期资金流入占比得分
        inflow_recent_ratio_score = self._normalize_score(
            recent_5d_ratio,
            0.2,  # 最近5天至少占20%
            0.6   # 最好不超过60%（太集中也不好）
        )
        
        # 存储指标得分
        self.indicator_scores.update({
            "large_order_ratio_score": large_order_ratio_score,
            "fund_style_score": fund_style_score,
            "inflow_acceleration_score": inflow_acceleration_score,
            "inflow_recent_ratio_score": inflow_recent_ratio_score,
        })
    
    def _analyze_volume_price_interaction(self, stock_data: pd.DataFrame, stock_meta: StockMeta) -> None:
        """
        分析量价互动特征
        
        Args:
            stock_data: 股票数据
            stock_meta: 股票元信息
        """
        # 获取最近交易日的数据
        recent_days = min(20, len(stock_data))
        recent_data = stock_data.tail(recent_days).copy()
        
        # ----- 量价背离度 -----
        # 计算资金流入和价格变动的标准化比值
        recent_data['price_change_pct'] = recent_data['close'].pct_change() * 100
        
        # 计算累计价格变动和累计资金流入
        start_price = recent_data['close'].iloc[0]
        end_price = recent_data['close'].iloc[-1]
        price_change_pct = (end_price / start_price - 1) * 100
        
        cumulative_inflow = recent_data['fund_flow'].sum()
        market_cap = stock_meta.market_cap * 100000000  # 转换为元
        
        # 如果价格没变化但有资金流入，背离度设为最大
        if abs(price_change_pct) < 0.1 and cumulative_inflow > 0:
            volume_price_divergence = 10.0  # 最大背离
        elif price_change_pct == 0:
            volume_price_divergence = 0  # 无法计算
        else:
            # 计算资金流入与价格变动的比值，正值表示同向，负值表示背离
            volume_price_divergence = (cumulative_inflow / market_cap) * 100 / price_change_pct if price_change_pct != 0 else 0
            # 如果价格下跌但资金流入，这也是背离信号
            if price_change_pct < 0 and cumulative_inflow > 0:
                volume_price_divergence = abs(volume_price_divergence)
        
        # ----- 支撑位大单买入 -----
        # 识别回调日
        recent_data['is_pullback'] = (recent_data['price_change_pct'] < -0.5)
        pullback_days = recent_data[recent_data['is_pullback']].copy()
        
        # 计算回调日的大单买入强度
        if len(pullback_days) > 0:
            pullback_large_buy = pullback_days['large_order_buy'].sum()
            normal_days = recent_data[~recent_data['is_pullback']]
            normal_large_buy_avg = normal_days['large_order_buy'].mean() if len(normal_days) > 0 else 0
            
            # 回调日大单买入相对强度 (相对于正常日的倍数)
            support_level_buying = pullback_large_buy / (normal_large_buy_avg * len(pullback_days)) if normal_large_buy_avg > 0 and len(pullback_days) > 0 else 1.0
        else:
            support_level_buying = 1.0  # 没有回调日，设为中性值
        
        # ----- 突破前资金蓄势 -----
        # 识别关键压力位
        # 这里简化处理，以最近20天的高点或前期高点作为压力位
        pressure_level = recent_data['close'].max()
        
        # 计算接近压力位的天数
        close_to_pressure = recent_data[recent_data['close'] > pressure_level * 0.95].copy()
        
        # 计算接近压力位时的资金流入
        if len(close_to_pressure) > 0:
            pressure_test_inflow = close_to_pressure['fund_flow'].sum()
            breakthrough_fund_accumulation = pressure_test_inflow / cumulative_inflow if cumulative_inflow > 0 else 0
        else:
            breakthrough_fund_accumulation = 0  # 没有接近压力位的情况
        
        # 存储指标值
        self.indicators.update({
            "volume_price_divergence": volume_price_divergence,
            "support_level_buying": support_level_buying,
            "breakthrough_fund_accumulation": breakthrough_fund_accumulation,
        })
        
        # 计算指标得分
        # 量价背离度得分 (越大越好)
        volume_price_divergence_score = self._normalize_score(
            abs(volume_price_divergence), 
            1.0,  # 基础分
            5.0   # 满分线
        )
        
        # 支撑位大单买入得分
        support_level_buying_score = self._normalize_score(
            support_level_buying,
            1.0,  # 正常值
            2.0   # 回调日是正常日2倍以上视为强支撑
        )
        
        # 突破前资金蓄势得分
        breakthrough_fund_accumulation_score = self._normalize_score(
            breakthrough_fund_accumulation,
            0.2,  # 突破前资金至少占20%
            0.5   # 突破前资金占比理想值
        )
        
        # 存储指标得分
        self.indicator_scores.update({
            "volume_price_divergence_score": volume_price_divergence_score,
            "support_level_buying_score": support_level_buying_score,
            "breakthrough_fund_accumulation_score": breakthrough_fund_accumulation_score,
        })
    
    def _generate_description(self) -> None:
        """生成模块分析描述"""
        # 根据总分确定整体评价
        if self.score >= 85:
            overall = "非常强烈"
        elif self.score >= 75:
            overall = "明显"
        elif self.score >= 65:
            overall = "一定"
        elif self.score >= 55:
            overall = "轻微"
        else:
            overall = "不明显"
        
        # 主要资金特征描述
        fund_style = self.indicators.get("fund_style", "unknown")
        style_desc = ""
        if fund_style == "institutional":
            style_desc = "机构资金建仓"
        elif fund_style == "northbound":
            style_desc = "北向资金流入"
        elif fund_style == "retail":
            style_desc = "游资资金活跃"
        else:
            style_desc = "主力资金介入"
        
        # 量价关系描述
        price_inflow_corr = self.indicators.get("price_inflow_correlation", 0)
        if abs(price_inflow_corr) < 0.25:
            price_desc = "资金流入与股价关联度低，可能存在吸筹行为"
        else:
            price_desc = "资金流入与股价变动基本同步"
        
        # 资金节奏描述
        if self.indicators.get("closing_inflow_ratio", 0) > 0.4:
            rhythm_desc = "尾盘资金占比高，具有明显的机构建仓特征"
        elif self.indicators.get("inflow_volatility", 1) < 0.4:
            rhythm_desc = "资金流入稳定，波动性低"
        else:
            rhythm_desc = "资金流入节奏一般"
        
        # 生成最终描述
        self.description = f"该股表现出{overall}的资金埋伏特征，主要体现为{style_desc}。"
        
        # 如果得分高于75，添加更多细节
        if self.score >= 75:
            self.description += f" {price_desc}，且{rhythm_desc}。"
        
        # 如果发现量价背离，特别强调
        if self.indicators.get("volume_price_divergence", 0) > 3 and self.indicator_scores.get("volume_price_divergence_score", 0) > 75:
            self.description += f" 存在明显的量价背离现象，资金流入强度远高于股价变动幅度。"
        
        # 如果大单买入占比高，添加说明
        if self.indicator_scores.get("large_order_ratio_score", 0) > 80:
            self.description += f" 大单交易占比较高，主力介入迹象明显。"
        
        # 最后加上验证建议
        if self.score >= 80:
            self.description += f" 建议重点关注持续跟踪。"
        elif self.score >= 65:
            self.description += f" 可以继续观察资金流向变化。"
    
    def _generate_detail_info(self, stock_data: pd.DataFrame, stock_meta: StockMeta) -> None:
        """
        生成详细分析信息
        
        Args:
            stock_data: 股票数据
            stock_meta: 股票元信息
        """
        detail_info = {}
        
        # 资金流入概况
        detail_info["资金流入概况"] = {
            "连续净流入天数": f"{self.indicators.get('continuous_inflow_days', 0)}/{len(stock_data.tail(20))}天",
            "累计净流入金额": f"{self.indicators.get('total_inflow', 0) / 100000000:.2f}亿元",
            "占流通市值比例": f"{self.indicators.get('inflow_to_cap_ratio', 0):.2f}%",
            "尾盘资金占比": f"{self.indicators.get('closing_inflow_ratio', 0) * 100:.2f}%",
            "资金流入波动系数": f"{self.indicators.get('inflow_volatility', 0):.2f}",
            "主动性买盘比例": f"{self.indicators.get('active_buy_ratio', 0) * 100:.2f}%"
        }
        
        # 资金特征分析
        detail_info["资金特征分析"] = {
            "资金类型": self._fund_style_to_chinese(self.indicators.get("fund_style", "unknown")),
            "大单占比": f"{self.indicators.get('large_order_ratio', 0) * 100:.2f}%",
            "大单买卖比": f"{self.indicators.get('large_order_buy_sell_ratio', 0):.2f}",
            "资金流入加速度": f"{self.indicators.get('inflow_acceleration', 0) * 100:.2f}%",
            "近5日资金占比": f"{self.indicators.get('recent_5d_inflow_ratio', 0) * 100:.2f}%"
        }
        
        # 量价关系分析
        detail_info["量价关系分析"] = {
            "价格与资金相关性": f"{self.indicators.get('price_inflow_correlation', 0):.2f}",
            "量价背离度": f"{self.indicators.get('volume_price_divergence', 0):.2f}",
            "回调买入强度": f"{self.indicators.get('support_level_buying', 0):.2f}",
            "突破前资金蓄势": f"{self.indicators.get('breakthrough_fund_accumulation', 0) * 100:.2f}%"
        }
        
        # 各项指标得分
        detail_info["各项指标得分"] = {k: f"{v:.2f}" for k, v in self.indicator_scores.items()}
        
        # 建议关注点
        suggestions = []
        if self.indicator_scores.get("closing_inflow_ratio_score", 0) > 75:
            suggestions.append("继续关注尾盘资金流向，如连续3天以上尾盘资金转为净流出，可能预示主力行为变化")
            
        if self.indicator_scores.get("volume_price_divergence_score", 0) > 75:
            suggestions.append("关注量价背离现象是否持续，如股价出现放量拉升可能是建仓完成信号")
            
        if self.indicator_scores.get("support_level_buying_score", 0) > 75:
            suggestions.append("已观察到回调时有大单支撑，建议关注支撑力度是否持续")
        
        if self.score >= 75:
            suggestions.append("整体资金埋伏迹象明显，建议重点跟踪")
        
        detail_info["建议关注点"] = suggestions if suggestions else ["暂无特别建议"]
        
        self.detail_info = detail_info
    
    def _generate_charts_data(self, stock_data: pd.DataFrame) -> None:
        """
        生成图表数据
        
        Args:
            stock_data: 股票数据
        """
        # 获取最近交易日的数据
        recent_days = min(60, len(stock_data))  # 使用更长的周期绘图
        chart_data = stock_data.tail(recent_days).copy()
        
        # 准备时间轴
        dates = chart_data['date'].dt.strftime('%Y-%m-%d').tolist()
        
        # 准备资金流向数据
        fund_flow = chart_data['fund_flow'].tolist()
        closing_fund_flow = chart_data['closing_fund_flow'].tolist() if 'closing_fund_flow' in chart_data.columns else []
        large_order_net_inflow = chart_data['large_order_net_inflow'].tolist() if 'large_order_net_inflow' in chart_data.columns else []
        
        # 准备累计资金流向数据
        cumulative_fund_flow = chart_data['fund_flow'].cumsum().tolist()
        
        # 准备价格数据
        prices = chart_data['close'].tolist()
        
        # 打包图表数据
        self.charts_data = {
            "dates": dates,
            "fund_flow": {
                "title": "日资金流向",
                "type": "bar",
                "data": fund_flow
            },
            "closing_fund_flow": {
                "title": "尾盘资金流向",
                "type": "bar",
                "data": closing_fund_flow
            },
            "large_order_net_inflow": {
                "title": "大单净流入",
                "type": "bar",
                "data": large_order_net_inflow
            },
            "cumulative_fund_flow": {
                "title": "累计资金流向",
                "type": "line",
                "data": cumulative_fund_flow
            },
            "prices": {
                "title": "收盘价",
                "type": "line",
                "data": prices,
                "yAxisIndex": 1
            }
        }
    
    def _fund_style_to_chinese(self, fund_style: str) -> str:
        """
        将资金类型转换为中文描述
        
        Args:
            fund_style: 资金类型
            
        Returns:
            中文描述
        """
        style_map = {
            "institutional": "机构资金",
            "northbound": "北向资金",
            "retail": "游资主导",
            "unknown": "未能明确判断"
        }
        return style_map.get(fund_style, "未知类型")