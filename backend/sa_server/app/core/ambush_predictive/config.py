from typing import Dict

# 持续性→
fund_flow_config: Dict = {
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

main_force_config: Dict = {
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

market_environment_config: Dict = {
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

share_structure_config: Dict = {
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

technical_pattern_config: Dict = {
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