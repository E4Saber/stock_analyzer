import pytest
import pandas as pd
import numpy as np
from typing import Dict, Any
from datetime import datetime, timedelta

from app.core.ambush_predictive.data_models import StockMeta, MarketContext
from app.core.ambush_predictive.ambush_predictive_modules.fund_flow_module import FundFlowModule

class TestFundFlowModule:
    @pytest.fixture
    def mock_stock_meta(self) -> StockMeta:
        """
        创建模拟股票元信息
        """
        return StockMeta(
            code="000001",
            name="测试股票",
            industry="测试行业",
            market_cap=100.0,  # 流通市值（亿元）
            total_cap=150.0,   # 总市值（亿元）
            pe_ratio=15.0,     # 市盈率
            pb_ratio=1.8,      # 市净率
            float_shares=10.0,  # 流通股本（亿股）
            total_shares=15.0   # 总股本（亿股）
        )

    @pytest.fixture
    def mock_market_context(self) -> MarketContext:
        """
        创建模拟市场环境
        """
        return MarketContext(
            date=datetime.now(),
            market_status="bull",  # 'bull', 'bear', 'shock'
            index_price_change=0.5,  # 大盘涨跌幅
            industry_price_change=0.8,  # 所属行业涨跌幅
            market_turnover=2.1,  # 市场换手率
            market_money_flow=50.0,  # 市场资金流向（亿元）
            northbound_flow=10.5,  # 北向资金流入（亿元）
            industry_fund_flow=5.0,  # 行业资金流入（亿元），可选
            market_sentiment_index=65.0  # 市场情绪指数(0-100)，可选
        )

    @pytest.fixture
    def sample_stock_data(self) -> pd.DataFrame:
        """
        创建模拟股票交易数据
        """
        # 生成20个交易日的模拟数据
        dates = [datetime.now() - timedelta(days=x) for x in range(20, 0, -1)]
        np.random.seed(42)  # 设置随机种子以保证可重复性
        
        data = {
            'date': dates,
            'open': np.random.uniform(10, 20, 20),
            'high': np.random.uniform(15, 25, 20),
            'low': np.random.uniform(5, 15, 20),
            'close': np.random.uniform(10, 20, 20),
            'volume': np.random.uniform(1000000, 5000000, 20),
            'amount': np.random.uniform(10000000, 50000000, 20),
            'fund_flow': np.random.normal(500000, 200000, 20),  # 模拟资金流向
            'large_order_net_inflow': np.random.normal(200000, 100000, 20),
            'large_order_buy': np.random.normal(300000, 150000, 20),
            'large_order_sell': np.random.normal(100000, 50000, 20),
            'closing_fund_flow': np.random.normal(100000, 50000, 20),
            'active_buy_ratio': np.random.uniform(0.6, 0.8, 20)
        }
        
        return pd.DataFrame(data)

    def test_module_initialization(self):
        """
        测试模块初始化
        """
        fund_flow_module = FundFlowModule()
        
        assert fund_flow_module.name == "fund_flow_module"
        assert fund_flow_module.weight == 0.30
        assert fund_flow_module.description == "分析股票资金流入特征，包括持续性、资金质量和量价关系"

    def test_default_config(self):
        """
        测试默认配置
        """
        fund_flow_module = FundFlowModule()
        config = fund_flow_module._get_default_config()
        
        # 检查配置中的关键参数
        assert "continuous_days_min" in config
        assert "net_inflow_days_ratio_min" in config
        assert "indicator_weights" in config
        assert config["continuous_days_min"] == 10
        assert config["net_inflow_days_ratio_min"] == 0.75

    def test_analyze_method(self, sample_stock_data, mock_stock_meta, mock_market_context):
        """
        测试分析方法的基本功能
        """
        fund_flow_module = FundFlowModule()
        
        # 执行分析
        result = fund_flow_module.analyze(
            stock_data=sample_stock_data, 
            stock_meta=mock_stock_meta, 
            market_context=mock_market_context
        )
        
        # 验证分析结果
        assert result is not None
        assert 0 <= result.score <= 100
        assert len(result.indicators) > 0
        assert len(result.indicator_scores) > 0
        assert result.description is not None
        assert result.detail_info is not None
        # print(result.to_dict())

    def test_fund_flow_direction_analysis(self, sample_stock_data, mock_stock_meta):
        """
        测试资金流向分析子方法
        """
        fund_flow_module = FundFlowModule()
        
        # 使用反射调用私有方法
        fund_flow_module._analyze_fund_flow_direction(sample_stock_data, mock_stock_meta)
        
        # 验证关键指标
        indicators = fund_flow_module.indicators
        assert "continuous_inflow_days" in indicators
        assert "inflow_days_ratio" in indicators
        assert "total_inflow" in indicators
        assert "inflow_to_cap_ratio" in indicators
        
        # 验证指标得分
        indicator_scores = fund_flow_module.indicator_scores
        assert "continuous_inflow_score" in indicator_scores
        assert "inflow_to_cap_ratio_score" in indicator_scores

        print(indicators)
        print(indicator_scores)

    def test_fund_quality_analysis(self, sample_stock_data, mock_stock_meta):
        """
        测试资金质量分析子方法
        """
        fund_flow_module = FundFlowModule()

        # 使用反射调用私有方法
        fund_flow_module._analyze_fund_flow_direction(sample_stock_data, mock_stock_meta)
        
        # 使用反射调用私有方法
        fund_flow_module._analyze_fund_quality(sample_stock_data, mock_stock_meta)
        
        # 验证关键指标
        indicators = fund_flow_module.indicators
        assert "large_order_ratio" in indicators
        assert "fund_style" in indicators
        assert "inflow_acceleration" in indicators
        
        # 验证指标得分
        indicator_scores = fund_flow_module.indicator_scores
        assert "large_order_ratio_score" in indicator_scores
        assert "fund_style_score" in indicator_scores

        print(indicators)
        print(indicator_scores)

    def test_volume_price_interaction(self, sample_stock_data, mock_stock_meta):
        """
        测试量价互动分析子方法
        """
        fund_flow_module = FundFlowModule()

        # 使用反射调用私有方法
        fund_flow_module._analyze_fund_flow_direction(sample_stock_data, mock_stock_meta)
        
        # 使用反射调用私有方法
        fund_flow_module._analyze_fund_quality(sample_stock_data, mock_stock_meta)
        
        # 使用反射调用私有方法
        fund_flow_module._analyze_volume_price_interaction(sample_stock_data, mock_stock_meta)
        
        # 验证关键指标
        indicators = fund_flow_module.indicators
        assert "volume_price_divergence" in indicators
        assert "support_level_buying" in indicators
        assert "breakthrough_fund_accumulation" in indicators
        
        # 验证指标得分
        indicator_scores = fund_flow_module.indicator_scores
        assert "volume_price_divergence_score" in indicator_scores
        assert "support_level_buying_score" in indicator_scores

        print(indicators)
        print(indicator_scores)

    def test_charts_data_generation(self, sample_stock_data, mock_stock_meta):
        """
        测试图表数据生成
        """
        fund_flow_module = FundFlowModule()
        # 使用反射调用私有方法
        fund_flow_module._analyze_fund_flow_direction(sample_stock_data, mock_stock_meta)
        
        # 使用反射调用私有方法
        fund_flow_module._analyze_fund_quality(sample_stock_data, mock_stock_meta)
        
        # 使用反射调用私有方法
        fund_flow_module._analyze_volume_price_interaction(sample_stock_data, mock_stock_meta)
        fund_flow_module._generate_charts_data(sample_stock_data)
        
        charts_data = fund_flow_module.charts_data
        assert "dates" in charts_data
        assert "fund_flow" in charts_data
        assert "prices" in charts_data
        assert len(charts_data["dates"]) > 0

        print(charts_data)

    def test_edge_cases(self):
        """
        测试边界情况
        """
        fund_flow_module = FundFlowModule()

        stock_meta=StockMeta(
            code="000000", 
            name="测试股票", 
            industry="测试",
            market_cap=10.0,
            total_cap=15.0,
            pe_ratio=12.0,
            pb_ratio=1.5,
            float_shares=5.0,
            total_shares=8.0
        )
        
        # 测试空数据情况
        with pytest.raises(ValueError):
            empty_data = pd.DataFrame()
            fund_flow_module.analyze(
                stock_data=empty_data, 
                stock_meta=stock_meta,
                market_context=MarketContext(
                                    date=datetime.now(),
                                    market_status="bull",
                                    index_price_change=0.5,
                                    industry_price_change=0.8,
                                    market_turnover=2.1,
                                    market_money_flow=50.0,
                                    northbound_flow=10.5
                                )
            )
        
        # 测试缺少必要列的情况
        with pytest.raises(ValueError):
            incomplete_data = pd.DataFrame({
                'date': pd.date_range(start='2023-01-01', periods=10),
                'close': np.random.uniform(10, 20, 10)
            })
            fund_flow_module.analyze(
                stock_data=incomplete_data,
                stock_meta=stock_meta,
                market_context=MarketContext()
            )