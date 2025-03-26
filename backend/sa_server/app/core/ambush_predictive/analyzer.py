"""
资金埋伏分析器主类
整合所有模块，提供完整的分析功能
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
import pandas as pd
import numpy as np
from datetime import datetime

from .base_module import AnalysisModule
from .data_models import StockMeta, MarketContext, AnalysisResult, FinalAnalysisResult

# 配置日志
logger = logging.getLogger('fund_burying_system')


class FundBuryingAnalyzer:
    """资金埋伏分析器主类"""
    
    def __init__(self):
        """初始化分析器"""
        self.modules: Dict[str, AnalysisModule] = {}
        self.module_results: Dict[str, AnalysisResult] = {}
        self.final_score: float = 0.0
        self.analysis_date: Optional[datetime] = None
        self.stock_meta: Optional[StockMeta] = None
        self.market_context: Optional[MarketContext] = None
        self.prediction_threshold: float = 75.0  # 预测阈值，根据二次验证提高
        self.is_predicted_buried: bool = False
        self.analysis_summary: str = ""
        self.recommendation: str = ""
        
        # 验证周期和止损水平
        self.verification_periods: Dict[str, int] = {
            "short_term": 10,  # 短线验证期(天)
            "medium_term": 30,  # 中线验证期(天)
            "long_term": 90     # 长线验证期(天)
        }
        
        self.stop_loss_levels: Dict[str, float] = {
            "short_term": 5.0,   # 短线止损比例(%)
            "medium_term": 10.0,  # 中线止损比例(%)
            "long_term": 15.0    # 长线止损比例(%)
        }
        
        # 动态权重配置
        self.weight_rules: Dict[str, Dict[str, float]] = {}
    
    def register_module(self, module: AnalysisModule) -> None:
        """
        注册分析模块
        
        Args:
            module: 分析模块
        """
        self.modules[module.name] = module
        logger.info(f"注册模块: {module.name}, 权重: {module.weight}")
    
    def load_config(self, config_path: str) -> None:
        """
        从文件加载配置
        
        Args:
            config_path: 配置文件路径
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 加载全局配置
            if 'global' in config:
                global_config = config['global']
                if 'prediction_threshold' in global_config:
                    self.prediction_threshold = global_config['prediction_threshold']
                
                if 'verification_periods' in global_config:
                    self.verification_periods.update(global_config['verification_periods'])
                
                if 'stop_loss_levels' in global_config:
                    self.stop_loss_levels.update(global_config['stop_loss_levels'])
            
            # 加载权重规则
            if 'weight_rules' in config:
                self.weight_rules = config['weight_rules']
            
            # 加载模块配置
            if 'modules' in config:
                modules_config = config['modules']
                for module_name, module_config in modules_config.items():
                    if module_name in self.modules:
                        self.modules[module_name].load_config(module_config)
            
            logger.info(f"成功加载配置文件: {config_path}")
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
    
    def save_config(self, config_path: str) -> None:
        """
        保存当前配置到文件
        
        Args:
            config_path: 配置文件路径
        """
        config = {
            'global': {
                'prediction_threshold': self.prediction_threshold,
                'verification_periods': self.verification_periods,
                'stop_loss_levels': self.stop_loss_levels
            },
            'weight_rules': self.weight_rules,
            'modules': {}
        }
        
        # 保存每个模块的配置
        for name, module in self.modules.items():
            config['modules'][name] = {
                'weight': module.weight,
                'enabled': module.is_enabled(),
                'params': module.config
            }
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"成功保存配置文件: {config_path}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
    
    def adjust_weights_by_context(self) -> None:
        """根据市场环境和股票特性调整各模块权重"""
        if not self.market_context or not self.stock_meta:
            logger.warning("无法调整权重: 缺少市场环境或股票基础信息")
            return
        
        # 检查是否有市场状态对应的权重规则
        market_status = self.market_context.market_status
        if market_status in self.weight_rules:
            logger.info(f"根据市场状态 '{market_status}' 调整模块权重")
            status_rules = self.weight_rules[market_status]
            
            # 应用权重规则
            for module_name, weight in status_rules.items():
                if module_name in self.modules:
                    self.modules[module_name].set_weight(weight)
                    logger.info(f"模块 '{module_name}' 权重调整为: {weight}")
        
        # 根据股票市值调整权重
        market_cap = self.stock_meta.market_cap
        cap_type = ""
        if market_cap < 50:
            cap_type = "small_cap"
        elif market_cap < 200:
            cap_type = "mid_cap"
        else:
            cap_type = "large_cap"
        
        if cap_type in self.weight_rules:
            logger.info(f"根据市值类型 '{cap_type}' 调整模块权重")
            cap_rules = self.weight_rules[cap_type]
            
            # 应用权重规则
            for module_name, weight in cap_rules.items():
                if module_name in self.modules:
                    self.modules[module_name].set_weight(weight)
                    logger.info(f"模块 '{module_name}' 权重调整为: {weight}")
        
        # 根据行业调整权重
        industry = self.stock_meta.industry
        industry_key = f"industry_{industry}"
        if industry_key in self.weight_rules:
            logger.info(f"根据行业 '{industry}' 调整模块权重")
            industry_rules = self.weight_rules[industry_key]
            
            # 应用权重规则
            for module_name, weight in industry_rules.items():
                if module_name in self.modules:
                    self.modules[module_name].set_weight(weight)
                    logger.info(f"模块 '{module_name}' 权重调整为: {weight}")
    
    def analyze(self, 
                stock_data: pd.DataFrame, 
                stock_meta: StockMeta, 
                market_context: MarketContext) -> FinalAnalysisResult:
        """
        分析股票数据
        
        Args:
            stock_data: 股票数据
            stock_meta: 股票元信息
            market_context: 市场环境上下文
            
        Returns:
            分析结果
        """
        self.stock_meta = stock_meta
        self.market_context = market_context
        self.analysis_date = market_context.date
        
        # 调整权重
        self.adjust_weights_by_context()
        
        # 存储各模块分数
        module_scores = {}
        total_weight = 0.0
        
        # 运行每个启用的模块
        for module_name, module in self.modules.items():
            if module.is_enabled():
                try:
                    logger.info(f"运行模块: {module_name}")
                    module_result = module.analyze(stock_data, stock_meta, market_context)
                    self.module_results[module_name] = module_result
                    module_scores[module_name] = module.score
                    total_weight += module.weight
                    logger.info(f"模块 '{module_name}' 得分: {module.score:.2f}, 权重: {module.weight:.2f}")
                except Exception as e:
                    logger.error(f"模块 '{module_name}' 分析失败: {e}")
                    module_scores[module_name] = 0.0
        
        # 计算总分
        if total_weight > 0:
            # 归一化权重，确保总和为1
            normalized_weights = {name: module.weight / total_weight 
                                for name, module in self.modules.items() 
                                if module.is_enabled()}
            
            # 计算加权总分
            self.final_score = sum(score * normalized_weights[name] 
                                  for name, score in module_scores.items())
        else:
            self.final_score = 0.0
        
        # 判断是否被预测为资金埋伏股
        self.is_predicted_buried = self.final_score >= self.prediction_threshold
        
        # 生成分析总结
        self._generate_analysis_summary()
        
        # 生成具体建议
        self._generate_recommendation()
        
        # 返回最终结果
        return FinalAnalysisResult(
            stock_code=stock_meta.code,
            stock_name=stock_meta.name,
            analysis_date=self.analysis_date,
            final_score=self.final_score,
            is_predicted_buried=self.is_predicted_buried,
            module_results=self.module_results,
            analysis_summary=self.analysis_summary,
            recommendation=self.recommendation,
            verification_periods=self.verification_periods,
            stop_loss_levels=self.stop_loss_levels,
            entry_strategy=self._get_entry_strategy(),
            threshold=self.prediction_threshold
        )
    
    def _generate_analysis_summary(self) -> None:
        """生成分析总结"""
        # 基本信息
        summary = f"{self.stock_meta.name}({self.stock_meta.code}) 资金埋伏分析结果:\n\n"
        
        # 总分和判断
        summary += f"综合得分: {self.final_score:.2f}\n"
        summary += f"预测结果: {'被资金埋伏的可能性较高' if self.is_predicted_buried else '暂未发现明显的资金埋伏迹象'}\n\n"
        
        # 模块得分概述
        summary += "各维度得分:\n"
        for name, result in self.module_results.items():
            summary += f"- {name}: {result.score:.2f} (权重: {result.weight:.2f})\n"
        
        # 强项和弱项分析
        if self.module_results:
            # 按得分排序
            sorted_modules = sorted(self.module_results.items(), key=lambda x: x[1].score, reverse=True)
            
            # 强项
            summary += "\n强项分析:\n"
            for name, result in sorted_modules[:3]:
                if result.score >= 70:
                    summary += f"- {name}: {result.score:.2f} - {result.description}\n"
            
            # 弱项
            summary += "\n弱项分析:\n"
            for name, result in sorted_modules[-3:]:
                if result.score < 60:
                    summary += f"- {name}: {result.score:.2f} - {result.description}\n"
        
        # 市场环境分析
        summary += f"\n市场环境: {self.market_context.market_status} (大盘涨跌幅: {self.market_context.index_price_change:.2f}%, 行业涨跌幅: {self.market_context.industry_price_change:.2f}%)\n"
        
        self.analysis_summary = summary
    
    def _generate_recommendation(self) -> None:
        """生成具体建议"""
        if not self.is_predicted_buried:
            self.recommendation = "当前暂未发现明显的资金埋伏迹象，建议继续观察或寻找其他机会。"
            return
        
        # 判断主力类型
        main_force_type = "unknown"
        if "main_force_module" in self.module_results:
            force_indicators = self.module_results["main_force_module"].indicators
            if "main_force_type" in force_indicators:
                main_force_type = force_indicators["main_force_type"]
            elif "institutional_buyer_proportion" in force_indicators:
                # 根据机构买入占比判断
                if force_indicators.get("institutional_buyer_proportion", 0) > 50:
                    main_force_type = "institutional"
                elif force_indicators.get("northbound_capital_holding_change", 0) > 0.5:
                    main_force_type = "northbound"
                else:
                    main_force_type = "retail"
        
        # 根据主力类型确定验证周期和建议
        verification_period = ""
        stop_loss_level = 0.0
        
        if main_force_type == "institutional" or main_force_type == "northbound":
            verification_period = "medium_term"
            stop_loss_level = self.stop_loss_levels["medium_term"]
            main_force_desc = "机构资金"
        elif main_force_type == "retail":
            verification_period = "short_term"
            stop_loss_level = self.stop_loss_levels["short_term"]
            main_force_desc = "游资主导"
        else:
            verification_period = "medium_term"
            stop_loss_level = self.stop_loss_levels["medium_term"]
            main_force_desc = "主力资金"
        
        days = self.verification_periods[verification_period]
        
        # 建仓策略
        entry_strategy = "分批建仓"
        if self.final_score >= 85:
            entry_strategy = "可一次性建仓60%，剩余资金分批补仓"
        elif self.final_score >= 75:
            entry_strategy = "首次建仓40%，突破确认后再加30%，剩余分批补仓"
        else:
            entry_strategy = "首次试探性建仓30%，等待进一步确认信号"
        
        # 生成建议
        recommendation = f"分析结果显示 {self.stock_meta.name}({self.stock_meta.code}) 可能存在{main_force_desc}埋伏迹象。\n\n"
        recommendation += f"建议操作:\n"
        recommendation += f"1. 建仓策略: {entry_strategy}\n"
        recommendation += f"2. 验证周期: 约{days}个交易日\n"
        recommendation += f"3. 止损设置: {stop_loss_level}%\n\n"
        
        # 关键监控指标
        recommendation += f"重点监控指标:\n"
        
        # 资金流入监控
        if "fund_flow_module" in self.module_results:
            flow_score = self.module_results["fund_flow_module"].score
            if flow_score >= 70:
                recommendation += f"- 持续关注尾盘资金流向变化，连续3天以上资金净流出为减仓信号\n"
        
        # 筹码结构监控
        if "share_structure_module" in self.module_results:
            structure_score = self.module_results["share_structure_module"].score
            if structure_score >= 70:
                recommendation += f"- 监控筹码集中度变化，一旦开始分散可能是主力出货信号\n"
        
        # 技术形态监控
        if "technical_pattern_module" in self.module_results:
            tech_score = self.module_results["technical_pattern_module"].score
            if tech_score >= 70:
                recommendation += f"- 关注颈线突破信号，有效突破可加仓，突破失败考虑止损\n"
        
        # 风险提示
        recommendation += f"\n风险提示: 本分析仅供参考，投资决策请结合个人风险承受能力及市场实际情况。"
        
        self.recommendation = recommendation
    
    def _get_entry_strategy(self) -> str:
        """获取建仓策略建议"""
        if not self.is_predicted_buried:
            return "暂不建仓"
        
        if self.final_score >= 85:
            return "可一次性建仓60%，剩余资金分批补仓"
        elif self.final_score >= 75:
            return "首次建仓40%，突破确认后再加30%，剩余分批补仓"
        else:
            return "首次试探性建仓30%，等待进一步确认信号"
    
    def get_enabled_modules(self) -> List[str]:
        """
        获取当前启用的模块列表
        
        Returns:
            启用的模块名称列表
        """
        return [name for name, module in self.modules.items() if module.is_enabled()]
    
    def set_module_enabled(self, module_name: str, enabled: bool) -> bool:
        """
        设置模块是否启用
        
        Args:
            module_name: 模块名称
            enabled: 是否启用
            
        Returns:
            操作是否成功
        """
        if module_name in self.modules:
            self.modules[module_name].set_enabled(enabled)
            return True
        return False
    
    def set_module_weight(self, module_name: str, weight: float) -> bool:
        """
        设置模块权重
        
        Args:
            module_name: 模块名称
            weight: 权重
            
        Returns:
            操作是否成功
        """
        if module_name in self.modules:
            self.modules[module_name].set_weight(weight)
            return True
        return False
    
    def set_prediction_threshold(self, threshold: float) -> None:
        """
        设置预测阈值
        
        Args:
            threshold: 阈值
        """
        self.prediction_threshold = threshold