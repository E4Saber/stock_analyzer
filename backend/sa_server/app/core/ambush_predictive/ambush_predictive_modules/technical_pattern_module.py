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

from app.core.ambush_predictive.base_module import AnalysisModule
from app.core.ambush_predictive.data_models import StockMeta, MarketContext, AnalysisResult

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
    
    def _add_technical_indicators(self, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        为股票数据添加技术指标
        
        Args:
            stock_data: 原始股票数据
        
        Returns:
            添加了技术指标的DataFrame
        """
        # 计算布林带
        stock_data['bollinger_upper'], stock_data['bollinger_middle'], stock_data['bollinger_lower'] = ta.BBANDS(
            stock_data['close'], 
            timeperiod=20, 
            nbdevup=2, 
            nbdevdn=2, 
            matype=0
        )
        
        # 计算布林带宽度
        stock_data['bollinger_width'] = (stock_data['bollinger_upper'] - stock_data['bollinger_lower']) / stock_data['bollinger_middle']
        
        # 计算平均真实波动范围(ATR)
        stock_data['atr'] = ta.ATR(stock_data['high'], stock_data['low'], stock_data['close'], timeperiod=14)
        
        # 计算多个移动平均线
        stock_data['MA5'] = ta.SMA(stock_data['close'], timeperiod=5)
        stock_data['MA10'] = ta.SMA(stock_data['close'], timeperiod=10)
        stock_data['MA20'] = ta.SMA(stock_data['close'], timeperiod=20)
        stock_data['MA30'] = ta.SMA(stock_data['close'], timeperiod=30)
        stock_data['MA60'] = ta.SMA(stock_data['close'], timeperiod=60)
        
        # 计算MACD指标
        stock_data['macd'], stock_data['macdsignal'], stock_data['macdhist'] = ta.MACD(
            stock_data['close'], 
            fastperiod=12, 
            slowperiod=26, 
            signalperiod=9
        )
        
        # 计算RSI
        stock_data['rsi'] = ta.RSI(stock_data['close'], timeperiod=14)
        
        # 计算多空均线关系
        stock_data['short_long_ma_angle'] = np.abs(np.arctan(stock_data['MA5'] - stock_data['MA30']) * 180 / np.pi)
        
        # 计算K线形态特征
        # 计算上下影线长度
        stock_data['lower_shadow_ratio'] = (stock_data['close'] - stock_data['low']) / (stock_data['high'] - stock_data['low'])
        stock_data['upper_shadow_ratio'] = (stock_data['high'] - stock_data['close']) / (stock_data['high'] - stock_data['low'])
        
        return stock_data

    def _analyze_bottom_pattern(self, data: pd.DataFrame) -> None:
        """
        分析底部形态特征
        
        Args:
            data: 包含技术指标的股票数据
        """
        # 最近的交易日数据
        recent_days = min(30, len(data))
        recent_data = data.tail(recent_days).copy()
        
        # 价格波动性
        price_volatility = recent_data['close'].std() / recent_data['close'].mean() * 100
        price_volatility_score = self._normalize_score(
            self.config["price_volatility_decrease_min"] - price_volatility,
            0,
            self.config["price_volatility_decrease_min"]
        )
        
        # 布林带宽度收窄
        bollinger_width_series = recent_data['bollinger_width']
        bollinger_width_change = (bollinger_width_series.iloc[0] - bollinger_width_series.iloc[-1]) / bollinger_width_series.iloc[0] * 100
        bollinger_width_score = self._normalize_score(
            bollinger_width_change,
            self.config["bollinger_width_decrease_min"] * 0.7,
            self.config["bollinger_width_decrease_min"] * 1.5
        )
        
        # 支撑位抬高
        support_level_change = (recent_data['low'].iloc[-1] - recent_data['low'].iloc[0]) / recent_data['low'].iloc[0] * 100
        support_resistance_score = self._normalize_score(
            support_level_change,
            self.config["support_level_increase_min"] * 0.7,
            self.config["support_level_increase_min"] * 1.5
        )
        
        # 阻力位变化
        resistance_level_change = (recent_data['high'].iloc[-1] - recent_data['high'].iloc[0]) / recent_data['high'].iloc[0] * 100
        resistance_change_score = self._normalize_score(
            self.config["resistance_level_change_max"] - abs(resistance_level_change),
            -self.config["resistance_level_change_max"],
            self.config["resistance_level_change_max"]
        )
        
        # 底部整理形态
        consolidation_days = (recent_data['high'] - recent_data['low']).std() / recent_data['close'].mean() * 100
        consolidation_pattern_score = self._normalize_score(
            self.config["bottom_consolidation_days_min"] - consolidation_days,
            0,
            self.config["bottom_consolidation_days_min"]
        )
        
        # 存储指标和得分
        self.indicators.update({
            "price_volatility": price_volatility,
            "bollinger_width_change": bollinger_width_change,
            "support_level_change": support_level_change,
            "resistance_level_change": resistance_level_change,
            "consolidation_days": consolidation_days
        })
        
        self.indicator_scores.update({
            "price_volatility_score": price_volatility_score,
            "bollinger_width_score": bollinger_width_score,
            "support_resistance_score": support_resistance_score,
            "resistance_change_score": resistance_change_score,
            "consolidation_pattern_score": consolidation_pattern_score
        })

    def _analyze_shakeout_signals(self, data: pd.DataFrame) -> None:
        """
        分析洗盘信号特征
        
        Args:
            data: 包含技术指标的股票数据
        """
        # 最近的交易日数据
        recent_days = min(30, len(data))
        recent_data = data.tail(recent_days).copy()
        
        # 长下影线特征
        long_lower_shadow_days = recent_data[recent_data['lower_shadow_ratio'] >= 1.5].shape[0]
        long_lower_shadow_score = self._normalize_score(
            long_lower_shadow_days,
            self.config["long_lower_shadow_min_count"] * 0.7,
            self.config["long_lower_shadow_min_count"] * 1.5
        )
        
        # 假突破次数
        false_breakout_count = 0
        # 这里简化处理，实际需要更复杂的逻辑来识别假突破
        if len(recent_data) > 5:
            for i in range(1, len(recent_data)):
                if (recent_data['high'].iloc[i] > recent_data['high'].iloc[i-1] and 
                    recent_data['close'].iloc[i] < recent_data['high'].iloc[i-1]):
                    false_breakout_count += 1
        
        false_breakout_score = self._normalize_score(
            false_breakout_count,
            self.config["false_breakout_min_count"] * 0.7,
            self.config["false_breakout_min_count"] * 1.5
        )
        
        # 盘中震仓
        intraday_shakeout_count = 0
        # 这里简化处理，实际需要更复杂的逻辑来识别盘中震仓
        if len(recent_data) > 1:
            for i in range(1, len(recent_data)):
                intraday_high_low_range = (recent_data['high'].iloc[i] - recent_data['low'].iloc[i]) / recent_data['close'].iloc[i-1] * 100
                if intraday_high_low_range > 2:  # 大于2%视为有震仓
                    intraday_shakeout_count += 1
        
        intraday_shakeout_score = self._normalize_score(
            intraday_shakeout_count,
            self.config["intraday_shakeout_min_count"] * 0.7,
            self.config["intraday_shakeout_min_count"] * 1.5
        )
        
        # 尾盘拉升特征
        closing_rally_days = recent_data[
            (recent_data['close'] - recent_data['low']) / (recent_data['high'] - recent_data['low']) >= 0.8
        ].shape[0]
        
        closing_rally_score = self._normalize_score(
            closing_rally_days,
            self.config["closing_rally_min"] * 0.7,
            self.config["closing_rally_min"] * 1.5
        )
        
        # 存储指标和得分
        self.indicators.update({
            "long_lower_shadow_days": long_lower_shadow_days,
            "false_breakout_count": false_breakout_count,
            "intraday_shakeout_count": intraday_shakeout_count,
            "closing_rally_days": closing_rally_days
        })
        
        self.indicator_scores.update({
            "long_lower_shadow_score": long_lower_shadow_score,
            "false_breakout_score": false_breakout_score,
            "intraday_shakeout_score": intraday_shakeout_score,
            "closing_rally_score": closing_rally_score
        })
    
    def _analyze_breakthrough_signals(self, data: pd.DataFrame) -> None:
        """
        分析突破前信号特征
        
        Args:
            data: 包含技术指标的股票数据
        """
        # 最近的交易日数据
        recent_days = min(30, len(data))
        recent_data = data.tail(recent_days).copy()
        
        # 关键压力位测试
        key_resistance_test_count = 0
        pressure_level = recent_data['close'].max()
        
        for i in range(1, len(recent_data)):
            if abs(recent_data['high'].iloc[i] - pressure_level) / pressure_level < 0.02:  # 2%范围内
                key_resistance_test_count += 1
        
        resistance_test_score = self._normalize_score(
            key_resistance_test_count,
            self.config["key_resistance_test_min_count"] * 0.7,
            self.config["key_resistance_test_min_count"] * 1.5
        )
        
        # 压力位测试间隔缩短
        test_intervals = []
        last_test_index = -1
        for i in range(1, len(recent_data)):
            if abs(recent_data['high'].iloc[i] - pressure_level) / pressure_level < 0.02:
                if last_test_index != -1:
                    test_intervals.append(i - last_test_index)
                last_test_index = i
        
        test_interval_change = np.std(test_intervals) if test_intervals else 0
        interval_score = self._normalize_score(
            self.config["resistance_test_interval_decrease_min"] - test_interval_change,
            0,
            self.config["resistance_test_interval_decrease_min"]
        )
        
        # 压力位测试量能
        volume_at_resistance = []
        for i in range(1, len(recent_data)):
            if abs(recent_data['high'].iloc[i] - pressure_level) / pressure_level < 0.02:
                volume_at_resistance.append(recent_data['volume'].iloc[i])
        
        volume_increase_rate = len(volume_at_resistance) / len(recent_data) * 100 if volume_at_resistance else 0
        volume_score = self._normalize_score(
            volume_increase_rate,
            self.config["volume_increase_at_resistance_min"] * 0.7,
            self.config["volume_increase_at_resistance_min"] * 1.5
        )
        
        # 均线收敛
        ma_convergence_angle = recent_data['short_long_ma_angle'].mean()
        ma_score = self._normalize_score(
            self.config["moving_average_convergence_max"] - ma_convergence_angle,
            0,
            self.config["moving_average_convergence_max"]
        )
        
        # MACD底背离
        macd_divergence = abs(recent_data['macd'].min() - recent_data['macd'].max()) / abs(recent_data['macd'].max()) * 100
        macd_score = self._normalize_score(
            macd_divergence,
            self.config["macd_divergence_min"] * 0.7,
            self.config["macd_divergence_min"] * 1.5
        )
        
        # 存储指标和得分
        self.indicators.update({
            "key_resistance_test_count": key_resistance_test_count,
            "test_interval_change": test_interval_change,
            "volume_increase_at_resistance": volume_increase_rate,
            "ma_convergence_angle": ma_convergence_angle,
            "macd_divergence": macd_divergence
        })
        
        self.indicator_scores.update({
            "resistance_test_score": resistance_test_score,
            "resistance_test_interval_score": interval_score,
            "volume_increase_score": volume_score,
            "moving_average_score": ma_score,
            "macd_divergence_score": macd_score
        })

    def _generate_description(self) -> None:
        """生成模块分析描述"""
        # 根据总分确定整体评价
        if self.score >= 85:
            overall = "非常明确"
        elif self.score >= 75:
            overall = "较为明显"
        elif self.score >= 65:
            overall = "一定程度"
        elif self.score >= 55:
            overall = "轻微"
        else:
            overall = "不明显"
        
        # 底部形态描述
        if self.indicator_scores.get("consolidation_pattern_score", 0) > 75:
            bottom_desc = "底部区域呈现明显整理形态，股价波动收窄"
        elif self.indicator_scores.get("consolidation_pattern_score", 0) > 60:
            bottom_desc = "底部区域显示出一定的整理趋势"
        else:
            bottom_desc = "底部形态尚未明确形成"
        
        # 洗盘信号描述
        shakeout_signals = []
        if self.indicator_scores.get("long_lower_shadow_score", 0) > 75:
            shakeout_signals.append("存在频繁的长下影线特征")
        if self.indicator_scores.get("false_breakout_score", 0) > 75:
            shakeout_signals.append("出现多次假突破回落")
        if self.indicator_scores.get("closing_rally_score", 0) > 75:
            shakeout_signals.append("尾盘拉升强度较高")
        
        shakeout_desc = "洗盘信号" + ("明显" if len(shakeout_signals) > 1 else "轻微")
        if shakeout_signals:
            shakeout_desc += f"，主要表现为：{' '.join(shakeout_signals)}"
        
        # 突破前兆描述
        breakthrough_signals = []
        if self.indicator_scores.get("resistance_test_score", 0) > 75:
            breakthrough_signals.append("关键压力位反复测试")
        if self.indicator_scores.get("moving_average_score", 0) > 75:
            breakthrough_signals.append("均线系统逐步收敛")
        if self.indicator_scores.get("macd_divergence_score", 0) > 75:
            breakthrough_signals.append("MACD底背离迹象明显")
        
        breakthrough_desc = "突破前兆" + ("强烈" if len(breakthrough_signals) > 1 else "轻微")
        if breakthrough_signals:
            breakthrough_desc += f"，主要表现为：{' '.join(breakthrough_signals)}"
        
        # 生成最终描述
        self.description = f"该股技术形态分析显示{overall}的底部特征。{bottom_desc}。"
        
        if shakeout_signals:
            self.description += f" {shakeout_desc}。"
        
        if breakthrough_signals:
            self.description += f" {breakthrough_desc}。"
        
        # 根据得分添加额外建议
        if self.score >= 75:
            self.description += " 技术形态显示较强的底部蓄势迹象，建议密切关注。"
        elif self.score >= 65:
            self.description += " 技术形态显示一定的底部整理可能，可保持观察。"

    def _generate_detail_info(self, data: pd.DataFrame) -> None:
        """
        生成详细分析信息
        
        Args:
            data: 包含技术指标的股票数据
        """
        detail_info = {}
        
        # 底部形态详细信息
        detail_info["底部形态分析"] = {
            "价格波动性": f"{self.indicators.get('price_volatility', 0):.2f}%",
            "布林带宽度变化": f"{self.indicators.get('bollinger_width_change', 0):.2f}%",
            "支撑位变化": f"{self.indicators.get('support_level_change', 0):.2f}%",
            "阻力位变化": f"{self.indicators.get('resistance_level_change', 0):.2f}%",
            "底部整理天数特征": f"{self.indicators.get('consolidation_days', 0):.2f}%"
        }
        
        # 洗盘信号详细信息
        detail_info["洗盘信号分析"] = {
            "长下影线天数": f"{self.indicators.get('long_lower_shadow_days', 0)}天",
            "假突破次数": f"{self.indicators.get('false_breakout_count', 0)}次",
            "盘中震仓次数": f"{self.indicators.get('intraday_shakeout_count', 0)}次",
            "尾盘拉升天数": f"{self.indicators.get('closing_rally_days', 0)}天"
        }
        
        # 突破前兆详细信息
        detail_info["突破前兆分析"] = {
            "压力位测试次数": f"{self.indicators.get('key_resistance_test_count', 0)}次",
            "压力位测试间隔变化": f"{self.indicators.get('test_interval_change', 0):.2f}",
            "压力位测试量能": f"{self.indicators.get('volume_increase_at_resistance', 0):.2f}%",
            "均线收敛角度": f"{self.indicators.get('ma_convergence_angle', 0):.2f}度",
            "MACD底背离程度": f"{self.indicators.get('macd_divergence', 0):.2f}%"
        }
        
        # 各项指标得分
        detail_info["指标得分"] = {
            # 底部形态得分
            "价格波动性得分": f"{self.indicator_scores.get('price_volatility_score', 0):.2f}",
            "布林带宽度得分": f"{self.indicator_scores.get('bollinger_width_score', 0):.2f}",
            "支撑位得分": f"{self.indicator_scores.get('support_resistance_score', 0):.2f}",
            "阻力位得分": f"{self.indicator_scores.get('resistance_change_score', 0):.2f}",
            "底部整理形态得分": f"{self.indicator_scores.get('consolidation_pattern_score', 0):.2f}",
            
            # 洗盘信号得分
            "长下影线得分": f"{self.indicator_scores.get('long_lower_shadow_score', 0):.2f}",
            "假突破得分": f"{self.indicator_scores.get('false_breakout_score', 0):.2f}",
            "盘中震仓得分": f"{self.indicator_scores.get('intraday_shakeout_score', 0):.2f}",
            "尾盘拉升得分": f"{self.indicator_scores.get('closing_rally_score', 0):.2f}",
            
            # 突破前兆得分
            "压力位测试得分": f"{self.indicator_scores.get('resistance_test_score', 0):.2f}",
            "压力位测试间隔得分": f"{self.indicator_scores.get('resistance_test_interval_score', 0):.2f}",
            "量能增加得分": f"{self.indicator_scores.get('volume_increase_score', 0):.2f}",
            "均线系统得分": f"{self.indicator_scores.get('moving_average_score', 0):.2f}",
            "MACD底背离得分": f"{self.indicator_scores.get('macd_divergence_score', 0):.2f}"
        }
        
        # 建议关注点
        suggestions = []
        
        # 底部形态建议
        if self.indicator_scores.get("consolidation_pattern_score", 0) > 75:
            suggestions.append("底部整理形态明显，可能即将迎来上涨")
        
        # 洗盘信号建议
        if self.indicator_scores.get("long_lower_shadow_score", 0) > 75:
            suggestions.append("长下影线频繁，显示主力可能在底部区域吸货")
        
        # 突破前兆建议
        if self.indicator_scores.get("resistance_test_score", 0) > 75:
            suggestions.append("关键压力位反复测试，突破可能性增加")
        
        if self.indicator_scores.get("moving_average_score", 0) > 75:
            suggestions.append("均线系统正在收敛，股价可能即将转折")
        
        # 总体建议
        if self.score >= 75:
            suggestions.append("技术形态显示明显的底部蓄势特征，值得重点关注")
        elif self.score >= 65:
            suggestions.append("技术形态显示一定的底部整理迹象，可保持观察")
        
        detail_info["建议关注点"] = suggestions if suggestions else ["暂无特别建议"]
        
        self.detail_info = detail_info

    def _generate_charts_data(self, data: pd.DataFrame) -> None:
        """
        生成图表数据
        
        Args:
            data: 包含技术指标的股票数据
        """
        # 获取最近交易日的数据
        recent_days = min(60, len(data))  # 使用更长的周期绘图
        chart_data = data.tail(recent_days).copy()
        
        # 准备时间轴
        dates = chart_data['date'].dt.strftime('%Y-%m-%d').tolist()
        
        # 准备K线和技术指标数据
        prices = {
            'open': chart_data['open'].tolist(),
            'high': chart_data['high'].tolist(),
            'low': chart_data['low'].tolist(),
            'close': chart_data['close'].tolist()
        }
        
        # 移动平均线
        moving_averages = {
            'MA5': chart_data['MA5'].tolist(),
            'MA10': chart_data['MA10'].tolist(),
            'MA20': chart_data['MA20'].tolist(),
            'MA30': chart_data['MA30'].tolist(),
            'MA60': chart_data['MA60'].tolist()
        }
        
        # 布林带
        bollinger_bands = {
            'upper': chart_data['bollinger_upper'].tolist(),
            'middle': chart_data['bollinger_middle'].tolist(),
            'lower': chart_data['bollinger_lower'].tolist()
        }
        
        # MACD指标
        macd_data = {
            'macd': chart_data['macd'].tolist(),
            'signal': chart_data['macdsignal'].tolist(),
            'hist': chart_data['macdhist'].tolist()
        }
        
        # RSI指标
        rsi_data = chart_data['rsi'].tolist()
        
        # 长下影线和上影线特征
        shadow_data = {
            'lower_shadow_ratio': chart_data['lower_shadow_ratio'].tolist(),
            'upper_shadow_ratio': chart_data['upper_shadow_ratio'].tolist()
        }
        
        # 均线角度变化
        ma_angle_data = chart_data['short_long_ma_angle'].tolist()
        
        # 打包图表数据
        self.charts_data = {
            "dates": dates,
            "prices": {
                "title": "价格K线图",
                "type": "candlestick",
                "data": prices
            },
            "moving_averages": {
                "title": "移动平均线",
                "type": "line_multi",
                "data": moving_averages
            },
            "bollinger_bands": {
                "title": "布林带",
                "type": "line_multi",
                "data": bollinger_bands
            },
            "macd": {
                "title": "MACD指标",
                "type": "macd",
                "data": macd_data
            },
            "rsi": {
                "title": "RSI指标",
                "type": "line",
                "data": rsi_data
            },
            "shadow_ratios": {
            "title": "K线影线比例",
            "type": "line_multi",
            "data": shadow_data
        },
        "ma_angle": {
            "title": "多空均线角度",
            "type": "line",
            "data": ma_angle_data
        }
    }