from pydantic import BaseModel, Field, validator, root_validator
from typing import Dict, List, Optional, Union, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from dataclasses import dataclass


class FundFlowIndicators(BaseModel):
    """资金流入特征指标"""
    
    # 大单资金流入指标
    large_order_net_inflow_days: int = Field(
        default=10, 
        description="统计大单净流入的天数范围"
    )
    large_order_net_inflow_threshold: float = Field(
        default=0.5, 
        description="大单净流入占流通市值的最小比例(百分比)"
    )
    large_order_net_inflow_continuity: float = Field(
        default=0.7, 
        description="大单净流入天数占比的最小值(0-1)"
    )
    
    # 尾盘资金流特征
    closing_inflow_weight: float = Field(
        default=1.5, 
        description="尾盘资金流入的权重倍数"
    )
    closing_inflow_duration: int = Field(
        default=30, 
        description="尾盘最后N分钟的资金流入统计"
    )
    
    # 资金规模匹配指标
    fund_to_market_cap_ratio: float = Field(
        default=0.5, 
        description="累计资金流入占流通市值的最小比例(百分比)"
    )
    daily_fund_to_turnover_ratio: float = Field(
        default=10.0, 
        description="日均资金流入占日均成交额的最小比例(百分比)"
    )
    
    # 权重设置
    weight: float = Field(default=0.3, description="资金流入特征在总评分中的权重")
    
    class Config:
        validate_assignment = True


class ShareStructureIndicators(BaseModel):
    """筹码结构特征指标"""
    
    # 换手率特征
    turnover_rate_range_min: float = Field(
        default=1.0, 
        description="换手率下限(百分比)"
    )
    turnover_rate_range_max: float = Field(
        default=3.0, 
        description="换手率上限(百分比)"
    )
    turnover_rate_stability: float = Field(
        default=0.3, 
        description="换手率波动系数上限(标准差/均值)"
    )
    
    # 筹码集中度
    shareholders_decrease_rate: float = Field(
        default=5.0, 
        description="股东户数减少率最小值(百分比)"
    )
    major_shareholders_holding_change: float = Field(
        default=0.5, 
        description="大股东持股增加的最小变动(百分比)"
    )
    share_concentration_increase: float = Field(
        default=2.0, 
        description="筹码集中度提升的最小值(百分比)"
    )
    
    # 成交结构
    large_order_bid_ask_ratio: float = Field(
        default=1.2, 
        description="大单买入/卖出比例的最小值"
    )
    large_order_proportion_trend: float = Field(
        default=5.0, 
        description="大单占比增长的最小值(百分比)"
    )
    
    # 权重设置
    weight: float = Field(default=0.25, description="筹码结构特征在总评分中的权重")


class TechnicalPatternIndicators(BaseModel):
    """技术形态特征指标"""
    
    # 价格形态
    price_volatility_decrease: float = Field(
        default=20.0, 
        description="价格波动性降低的最小百分比"
    )
    support_level_increase: float = Field(
        default=2.0, 
        description="支撑位抬高的最小百分比"
    )
    resistance_level_stability: float = Field(
        default=1.0, 
        description="阻力位变化的最大百分比"
    )
    
    # 洗盘信号
    long_lower_shadow_frequency: int = Field(
        default=3, 
        description="观察期内长下影线出现的最小次数"
    )
    false_breakout_recovery: int = Field(
        default=2, 
        description="假突破后回落但无恐慌性抛售的最小次数"
    )
    closing_price_strength: float = Field(
        default=0.5, 
        description="尾盘拉升的最小幅度(百分比)"
    )
    
    # 突破前兆
    volume_increase_before_breakout: float = Field(
        default=50.0, 
        description="突破前量能增加的最小百分比"
    )
    key_resistance_test_frequency: int = Field(
        default=3, 
        description="关键压力位测试的最小次数"
    )
    moving_average_alignment: bool = Field(
        default=True, 
        description="均线系统是否开始多头排列"
    )
    
    # 权重设置
    weight: float = Field(default=0.2, description="技术形态特征在总评分中的权重")


class MainForceIndicators(BaseModel):
    """主力特征判断指标"""
    
    # 主力类型识别
    institutional_buyer_proportion: float = Field(
        default=50.0, 
        description="机构买入占比的最小值(百分比)"
    )
    northbound_capital_holding_change: float = Field(
        default=0.2, 
        description="北向资金持股变化的最小值(百分比)"
    )
    major_shareholder_increase: bool = Field(
        default=False, 
        description="是否有大股东增持"
    )
    
    # 操作风格匹配
    building_position_duration: int = Field(
        default=10, 
        description="建仓持续的最小天数"
    )
    building_position_pattern: str = Field(
        default="steady", 
        description="建仓模式: steady(稳定), aggressive(激进), cautious(谨慎)"
    )
    similar_stock_pattern_match: bool = Field(
        default=False, 
        description="是否与类似个股操作模式匹配"
    )
    
    # 权重设置
    weight: float = Field(default=0.15, description="主力特征在总评分中的权重")


class MarketEnvironmentIndicators(BaseModel):
    """市场环境匹配指标"""
    
    # 市场风格
    market_style_match: bool = Field(
        default=True, 
        description="是否匹配当前市场风格"
    )
    market_attention_to_sector: float = Field(
        default=0.5, 
        description="市场对该板块的关注度(0-1)"
    )
    
    # 联动效应
    sector_stocks_performance: float = Field(
        default=5.0, 
        description="同板块个股平均涨幅的最小值(百分比)"
    )
    related_concept_heat: float = Field(
        default=0.6, 
        description="相关概念热度(0-1)"
    )
    policy_environment_match: bool = Field(
        default=True, 
        description="是否匹配当前政策环境"
    )
    
    # 权重设置
    weight: float = Field(default=0.1, description="市场环境在总评分中的权重")


class FundBuryingModel(BaseModel):
    """资金埋伏股票预测模型"""
    
    # 模型名称和描述
    model_name: str = Field(default="资金埋伏预测模型", description="模型名称")
    description: str = Field(default="识别被主力资金埋伏且具备拉升潜力的股票", description="模型描述")
    
    # 各维度指标
    fund_flow: FundFlowIndicators = Field(default_factory=FundFlowIndicators)
    share_structure: ShareStructureIndicators = Field(default_factory=ShareStructureIndicators)
    technical_pattern: TechnicalPatternIndicators = Field(default_factory=TechnicalPatternIndicators)
    main_force: MainForceIndicators = Field(default_factory=MainForceIndicators)
    market_environment: MarketEnvironmentIndicators = Field(default_factory=MarketEnvironmentIndicators)
    
    # 回测参数
    verification_periods: Dict[str, int] = Field(
        default={
            "short_term": 10,   # 短线验证期(天)
            "medium_term": 30,  # 中线验证期(天)
            "long_term": 90     # 长线验证期(天)
        },
        description="不同周期的验证天数"
    )
    
    # 止损设置
    stop_loss_levels: Dict[str, float] = Field(
        default={
            "short_term": 5.0,   # 短线止损比例(%)
            "medium_term": 10.0, # 中线止损比例(%)
            "long_term": 15.0    # 长线止损比例(%)
        },
        description="不同周期的止损百分比"
    )
    
    # 预测阈值
    prediction_threshold: float = Field(
        default=70.0, 
        description="预测分数的阈值，高于该值视为被埋伏"
    )
    
    @root_validator
    def check_weights_sum(cls, values):
        """验证各维度权重之和是否为1"""
        dimensions = ['fund_flow', 'share_structure', 'technical_pattern', 'main_force', 'market_environment']
        weight_sum = sum(values[dim].weight for dim in dimensions if dim in values)
        
        if not np.isclose(weight_sum, 1.0, atol=1e-2):
            raise ValueError(f"所有维度的权重之和必须为1.0，当前为{weight_sum}")
        
        return values

    def calculate_score(self, stock_data: Dict) -> Dict[str, Union[float, Dict]]:
        """
        计算股票的资金埋伏得分
        
        Args:
            stock_data: 包含股票各项指标数据的字典
            
        Returns:
            包含总分和各维度得分的字典
        """
        # 初始化各维度得分
        dimension_scores = {
            "fund_flow": 0,
            "share_structure": 0,
            "technical_pattern": 0,
            "main_force": 0,
            "market_environment": 0
        }
        
        # 这里应实现具体的评分逻辑，根据stock_data中的数据与模型指标进行比较
        # 为简化示例，此处仅返回随机分数
        for dimension in dimension_scores:
            # 实际应用中，应根据stock_data中的值与模型中的阈值进行比较计算得分
            dimension_scores[dimension] = np.random.uniform(60, 95)
        
        # 计算加权总分
        dimensions = ['fund_flow', 'share_structure', 'technical_pattern', 'main_force', 'market_environment']
        total_score = sum(
            dimension_scores[dim] * getattr(self, dim).weight for dim in dimensions
        )
        
        return {
            "total_score": total_score,
            "dimension_scores": dimension_scores,
            "is_predicted_buried": total_score >= self.prediction_threshold
        }


class BacktestResult(BaseModel):
    """回测结果模型"""
    
    # 基本信息
    stock_code: str
    stock_name: str
    prediction_date: datetime
    prediction_score: float
    is_predicted_buried: bool
    
    # 表现指标
    performance: Dict[str, Dict[str, float]] = Field(
        default_factory=lambda: {
            "short_term": {"max_gain": 0, "max_loss": 0, "final_gain": 0},
            "medium_term": {"max_gain": 0, "max_loss": 0, "final_gain": 0},
            "long_term": {"max_gain": 0, "max_loss": 0, "final_gain": 0}
        }
    )
    
    # 信号是否有效
    signal_effectiveness: Dict[str, bool] = Field(
        default_factory=lambda: {
            "short_term": False,
            "medium_term": False, 
            "long_term": False
        }
    )
    
    # 回测时各维度的得分
    dimension_scores: Dict[str, float] = Field(default_factory=dict)


class BacktestFramework:
    """回测框架"""
    
    def __init__(self, model: FundBuryingModel):
        self.model = model
        self.results: List[BacktestResult] = []
    
    def run_backtest(self, 
                    stock_data_list: List[Dict], 
                    price_history: Dict[str, pd.DataFrame]) -> List[BacktestResult]:
        """
        运行回测
        
        Args:
            stock_data_list: 包含多只股票数据的列表，每个元素是一个字典
            price_history: 股票历史价格数据，键为股票代码，值为DataFrame
            
        Returns:
            回测结果列表
        """
        results = []
        
        for stock_data in stock_data_list:
            # 预测股票是否被埋伏
            prediction = self.model.calculate_score(stock_data)
            
            # 创建初始回测结果
            result = BacktestResult(
                stock_code=stock_data["stock_code"],
                stock_name=stock_data["stock_name"],
                prediction_date=stock_data["date"],
                prediction_score=prediction["total_score"],
                is_predicted_buried=prediction["is_predicted_buried"],
                dimension_scores=prediction["dimension_scores"]
            )
            
            # 如果股票被预测为埋伏股，分析后续表现
            if result.is_predicted_buried and stock_data["stock_code"] in price_history:
                # 获取该股票的价格历史数据
                df = price_history[stock_data["stock_code"]]
                prediction_idx = df[df['date'] == stock_data["date"]].index[0]
                
                # 计算不同周期的表现
                for period_name, days in self.model.verification_periods.items():
                    if prediction_idx + days < len(df):
                        # 获取验证期内的价格数据
                        period_df = df.iloc[prediction_idx:prediction_idx + days + 1]
                        
                        # 计算最大收益、最大回撤和最终收益
                        base_price = period_df.iloc[0]['close']
                        period_df['return'] = period_df['close'] / base_price - 1
                        
                        max_gain = period_df['return'].max() * 100
                        max_loss = period_df['return'].min() * 100
                        final_gain = period_df['return'].iloc[-1] * 100
                        
                        # 更新回测结果
                        result.performance[period_name] = {
                            "max_gain": max_gain,
                            "max_loss": max_loss,
                            "final_gain": final_gain
                        }
                        
                        # 判断信号是否有效
                        # 这里的判断标准可以自定义，例如最终收益大于5%
                        result.signal_effectiveness[period_name] = final_gain >= 5.0
            
            results.append(result)
            
        self.results = results
        return results
    
    def calculate_metrics(self) -> Dict:
        """计算回测的综合指标"""
        if not self.results:
            return {"error": "No backtest results found"}
        
        # 初始化指标字典
        metrics = {
            "total_predictions": 0,
            "buried_predictions": 0,
            "effectiveness": {
                "short_term": {"count": 0, "rate": 0},
                "medium_term": {"count": 0, "rate": 0},
                "long_term": {"count": 0, "rate": 0}
            },
            "avg_performance": {
                "short_term": {"max_gain": 0, "max_loss": 0, "final_gain": 0},
                "medium_term": {"max_gain": 0, "max_loss": 0, "final_gain": 0},
                "long_term": {"max_gain": 0, "max_loss": 0, "final_gain": 0}
            }
        }
        
        # 统计总预测和被预测为埋伏的股票数
        metrics["total_predictions"] = len(self.results)
        metrics["buried_predictions"] = sum(1 for r in self.results if r.is_predicted_buried)
        
        if metrics["buried_predictions"] == 0:
            return {**metrics, "warning": "No stocks predicted as buried"}
        
        # 计算各周期的有效性和平均表现
        buried_results = [r for r in self.results if r.is_predicted_buried]
        
        for period in ["short_term", "medium_term", "long_term"]:
            # 统计有效信号数量
            valid_signals = sum(1 for r in buried_results if r.signal_effectiveness.get(period, False))
            metrics["effectiveness"][period]["count"] = valid_signals
            metrics["effectiveness"][period]["rate"] = valid_signals / metrics["buried_predictions"] * 100
            
            # 计算平均表现
            period_performances = [r.performance.get(period, {}) for r in buried_results 
                                  if period in r.performance]
            
            if period_performances:
                metrics["avg_performance"][period]["max_gain"] = sum(p.get("max_gain", 0) for p in period_performances) / len(period_performances)
                metrics["avg_performance"][period]["max_loss"] = sum(p.get("max_loss", 0) for p in period_performances) / len(period_performances)
                metrics["avg_performance"][period]["final_gain"] = sum(p.get("final_gain", 0) for p in period_performances) / len(period_performances)
        
        return metrics
    
    def plot_performance_distribution(self):
        """绘制不同周期的收益分布图"""
        if not self.results:
            print("No backtest results to plot")
            return
        
        buried_results = [r for r in self.results if r.is_predicted_buried]
        if not buried_results:
            print("No stocks predicted as buried")
            return
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        periods = ["short_term", "medium_term", "long_term"]
        titles = ["短期({}天)".format(self.model.verification_periods["short_term"]),
                 "中期({}天)".format(self.model.verification_periods["medium_term"]),
                 "长期({}天)".format(self.model.verification_periods["long_term"])]
        
        for i, (period, title) in enumerate(zip(periods, titles)):
            gains = [r.performance.get(period, {}).get("final_gain", 0) for r in buried_results 
                    if period in r.performance]
            
            if gains:
                axes[i].hist(gains, bins=20, alpha=0.7)
                axes[i].axvline(x=0, color='r', linestyle='--')
                axes[i].set_title(title)
                axes[i].set_xlabel("收益率(%)")
                axes[i].set_ylabel("股票数量")
        
        plt.tight_layout()
        plt.show()
    
    def plot_dimension_importance(self):
        """绘制各维度得分与最终收益的相关性分析"""
        if not self.results:
            print("No backtest results to plot")
            return
        
        buried_results = [r for r in self.results if r.is_predicted_buried]
        if not buried_results:
            print("No stocks predicted as buried")
            return
        
        dimensions = ["fund_flow", "share_structure", "technical_pattern", "main_force", "market_environment"]
        
        # 准备数据
        data = {dim: [] for dim in dimensions}
        gains = []
        
        for result in buried_results:
            # 使用中期收益作为目标变量
            if "medium_term" in result.performance:
                for dim in dimensions:
                    if dim in result.dimension_scores:
                        data[dim].append(result.dimension_scores[dim])
                
                gains.append(result.performance["medium_term"]["final_gain"])
        
        # 计算相关性
        correlations = {}
        for dim in dimensions:
            if data[dim] and len(data[dim]) == len(gains):
                correlations[dim] = np.corrcoef(data[dim], gains)[0, 1]
        
        # 绘制相关性图表
        plt.figure(figsize=(10, 6))
        bars = plt.bar(correlations.keys(), correlations.values())
        
        # 为正负相关设置不同颜色
        for i, corr in enumerate(correlations.values()):
            if corr < 0:
                bars[i].set_color('r')
        
        plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        plt.title("各维度得分与中期收益的相关性")
        plt.ylabel("相关系数")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


class FundBuryingAnalyzer:
    """资金埋伏分析器"""
    
    def __init__(self, config_path=None):
        """
        初始化分析器
        
        Args:
            config_path: 模型配置文件路径，如果为None则使用默认配置
        """
        if config_path:
            # 从文件加载配置
            self.model = self._load_config(config_path)
        else:
            # 使用默认配置
            self.model = FundBuryingModel()
        
        self.backtest_framework = BacktestFramework(self.model)
    
    def _load_config(self, config_path: str) -> FundBuryingModel:
        """从文件加载模型配置"""
        import json
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return FundBuryingModel(**config)
    
    def save_config(self, config_path: str):
        """保存当前模型配置到文件"""
        import json
        
        config = self.model.dict()
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def analyze_stock(self, stock_data: Dict) -> Dict:
        """分析单只股票是否被资金埋伏"""
        return self.model.calculate_score(stock_data)
    
    def batch_analyze(self, stock_data_list: List[Dict]) -> List[Dict]:
        """批量分析多只股票是否被资金埋伏"""
        results = []
        
        for stock_data in stock_data_list:
            result = self.analyze_stock(stock_data)
            results.append({
                "stock_code": stock_data["stock_code"],
                "stock_name": stock_data["stock_name"],
                "prediction_score": result["total_score"],
                "is_predicted_buried": result["is_predicted_buried"],
                "dimension_scores": result["dimension_scores"]
            })
        
        return results
    
    def run_backtest(self, stock_data_list: List[Dict], price_history: Dict[str, pd.DataFrame]):
        """运行回测"""
        return self.backtest_framework.run_backtest(stock_data_list, price_history)
    
    def get_backtest_metrics(self) -> Dict:
        """获取回测指标"""
        return self.backtest_framework.calculate_metrics()
    
    def visualize_backtest_results(self):
        """可视化回测结果"""
        self.backtest_framework.plot_performance_distribution()
        self.backtest_framework.plot_dimension_importance()


# 使用示例
def example_usage():
    # 初始化分析器
    analyzer = FundBuryingAnalyzer()
    
    # 自定义模型参数（可选）
    analyzer.model.fund_flow.large_order_net_inflow_days = 15
    analyzer.model.fund_flow.weight = 0.35
    analyzer.model.technical_pattern.weight = 0.25
    analyzer.model.share_structure.weight = 0.20
    analyzer.model.main_force.weight = 0.12
    analyzer.model.market_environment.weight = 0.08
    
    # 准备回测数据
    # 注意：这里只是示例数据结构，实际应用需要填充真实数据
    stock_data_list = [
        {
            "stock_code": "600001",
            "stock_name": "示例股票1",
            "date": datetime(2025, 1, 15),
            # 以下是模型需要的各种指标数据，实际应用中需要填充
            "large_order_net_inflow": [], 
            "turnover_rates": [],
            # ... 其他指标数据
        },
        # ... 更多股票数据
    ]
    
    # 准备历史价格数据
    price_history = {
        "600001": pd.DataFrame({
            "date": pd.date_range(start="2025-01-01", periods=100),
            "open": np.random.normal(10, 0.5, 100),
            "high": np.random.normal(10.5, 0.5, 100),
            "low": np.random.normal(9.5, 0.5, 100),
            "close": np.random.normal(10, 0.5, 100),
            "volume": np.random.normal(1000000, 200000, 100)
        })
    }
    
    # 运行回测
    analyzer.run_backtest(stock_data_list, price_history)
    
    # 获取回测指标
    metrics = analyzer.get_backtest_metrics()
    print("回测指标:", metrics)
    
    # 可视化回测结果
    analyzer.visualize_backtest_results()


if __name__ == "__main__":
    example_usage()