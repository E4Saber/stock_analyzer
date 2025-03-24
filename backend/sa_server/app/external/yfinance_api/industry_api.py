import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional, Any, Union
import json

class YFinanceIndustry:
    """
    基于 yfinance.Industry 的增强行业模块，提供对金融市场行业数据的全面访问
    """
    
    def __init__(
        self,
        key: str,
        session: Optional[Any] = None,
        proxy: Optional[Dict] = None
    ):
        """
        初始化 YFinanceIndustry 对象
        
        参数:
            key (str): 行业的唯一标识符
            session (optional): 用于请求的会话
            proxy (optional): 用于请求的代理
        """
        self.key = key
        self.session = session
        self.proxy = proxy
        
        # 初始化 yfinance.Industry 对象
        self._industry = yf.Industry(
            key=self.key,
            session=self.session,
            proxy=self.proxy
        )
        
        # 缓存特性，用于减少 API 调用
        self._cached_top_companies = None
        self._cached_top_growth_companies = None
        self._cached_top_performing_companies = None
        self._cached_overview = None
        self._cached_research_reports = None
    
    @property
    def name(self) -> str:
        """
        获取行业的名称
        
        返回:
            str: 行业的名称
        """
        return self._industry.name
    
    @property
    def symbol(self) -> str:
        """
        获取表示行业的符号
        
        返回:
            str: 表示行业的符号
        """
        return self._industry.symbol
    
    @property
    def sector_key(self) -> str:
        """
        获取行业所属部门的键
        
        返回:
            str: 部门键
        """
        return self._industry.sector_key
    
    @property
    def sector_name(self) -> str:
        """
        获取行业所属部门的名称
        
        返回:
            str: 部门名称
        """
        return self._industry.sector_name
    
    @property
    def overview(self) -> Dict:
        """
        获取行业的概述信息
        
        返回:
            Dict: 包含行业概述的字典
        """
        if self._cached_overview is None:
            self._cached_overview = self._industry.overview
        return self._cached_overview
    
    @property
    def research_reports(self) -> List[Dict[str, str]]:
        """
        获取与行业相关的研究报告
        
        返回:
            List[Dict[str, str]]: 研究报告列表，每个报告是一个包含元数据的字典
        """
        if self._cached_research_reports is None:
            self._cached_research_reports = self._industry.research_reports
        return self._cached_research_reports
    
    @property
    def top_companies(self) -> pd.DataFrame:
        """
        获取行业内的顶级公司
        
        返回:
            pandas.DataFrame: 包含域中顶级公司的 DataFrame
        """
        if self._cached_top_companies is None:
            self._cached_top_companies = self._industry.top_companies
        return self._cached_top_companies
    
    @property
    def top_growth_companies(self) -> Optional[pd.DataFrame]:
        """
        获取行业内的顶级增长公司
        
        返回:
            Optional[pd.DataFrame]: 包含顶级增长公司的 DataFrame
        """
        if self._cached_top_growth_companies is None:
            self._cached_top_growth_companies = self._industry.top_growth_companies
        return self._cached_top_growth_companies
    
    @property
    def top_performing_companies(self) -> Optional[pd.DataFrame]:
        """
        获取行业内的顶级表现公司
        
        返回:
            Optional[pd.DataFrame]: 包含顶级表现公司的 DataFrame
        """
        if self._cached_top_performing_companies is None:
            self._cached_top_performing_companies = self._industry.top_performing_companies
        return self._cached_top_performing_companies
    
    def get_ticker(self) -> yf.Ticker:
        """
        获取基于行业符号的 Ticker 对象
        
        返回:
            yf.Ticker: 与行业关联的 Ticker 对象
        """
        return self._industry.ticker
    
    def get_sector(self) -> yf.Sector:
        """
        获取该行业所属的部门
        
        返回:
            yf.Sector: 行业所属的部门对象
        """
        return yf.Sector(self.sector_key)
    
    def get_company_details(self, limit: int = 5) -> Dict[str, Dict]:
        """
        获取行业顶级公司的详细信息
        
        参数:
            limit (int): 要获取的公司的数量限制
            
        返回:
            Dict[str, Dict]: 公司符号到详细信息的映射
        """
        result = {}
        
        if self.top_companies is None or len(self.top_companies) == 0:
            return result
        
        # 假设 top_companies 是一个 DataFrame，包含 'symbol' 列
        if 'symbol' in self.top_companies.columns:
            for i, row in self.top_companies.head(limit).iterrows():
                symbol = row['symbol']
                
                try:
                    ticker = yf.Ticker(symbol)
                    
                    # 收集公司详细信息
                    result[symbol] = {
                        "name": row.get('name', 'Unknown'),
                        "info": ticker.info,
                        "financials": ticker.financials.to_dict() if hasattr(ticker, 'financials') and ticker.financials is not None else None,
                        "major_holders": ticker.major_holders.to_dict() if hasattr(ticker, 'major_holders') and ticker.major_holders is not None else None,
                        "recommendations": ticker.get_recommendations().to_dict() if hasattr(ticker, 'get_recommendations') else None
                    }
                except Exception as e:
                    print(f"获取公司 '{symbol}' 的详细信息时出错: {str(e)}")
        
        return result
    
    def get_growth_company_details(self, limit: int = 5) -> Dict[str, Dict]:
        """
        获取行业顶级增长公司的详细信息
        
        参数:
            limit (int): 要获取的公司的数量限制
            
        返回:
            Dict[str, Dict]: 公司符号到详细信息的映射
        """
        result = {}
        
        if self.top_growth_companies is None or len(self.top_growth_companies) == 0:
            return result
        
        # 假设 top_growth_companies 是一个 DataFrame，包含 'symbol' 列
        if 'symbol' in self.top_growth_companies.columns:
            for i, row in self.top_growth_companies.head(limit).iterrows():
                symbol = row['symbol']
                
                try:
                    ticker = yf.Ticker(symbol)
                    
                    # 收集公司详细信息
                    result[symbol] = {
                        "name": row.get('name', 'Unknown'),
                        "info": ticker.info,
                        "growth_metrics": {
                            "revenue_growth": ticker.income_stmt.loc["Total Revenue"].pct_change().to_dict() if hasattr(ticker, 'income_stmt') and 'Total Revenue' in ticker.income_stmt.index else None,
                            "earnings_growth": ticker.income_stmt.loc["Net Income"].pct_change().to_dict() if hasattr(ticker, 'income_stmt') and 'Net Income' in ticker.income_stmt.index else None
                        }
                    }
                except Exception as e:
                    print(f"获取增长公司 '{symbol}' 的详细信息时出错: {str(e)}")
        
        return result
    
    def get_performance_company_details(self, limit: int = 5) -> Dict[str, Dict]:
        """
        获取行业顶级表现公司的详细信息
        
        参数:
            limit (int): 要获取的公司的数量限制
            
        返回:
            Dict[str, Dict]: 公司符号到详细信息的映射
        """
        result = {}
        
        if self.top_performing_companies is None or len(self.top_performing_companies) == 0:
            return result
        
        # 假设 top_performing_companies 是一个 DataFrame，包含 'symbol' 列
        if 'symbol' in self.top_performing_companies.columns:
            for i, row in self.top_performing_companies.head(limit).iterrows():
                symbol = row['symbol']
                
                try:
                    ticker = yf.Ticker(symbol)
                    
                    # 收集公司详细信息
                    result[symbol] = {
                        "name": row.get('name', 'Unknown'),
                        "info": ticker.info,
                        "performance_metrics": {
                            "price_history": ticker.history(period="1y")['Close'].to_dict() if hasattr(ticker, 'history') else None,
                            "returns": {
                                "1m": ticker.history(period="1mo")['Close'].pct_change().iloc[-1] if hasattr(ticker, 'history') else None,
                                "3m": ticker.history(period="3mo")['Close'].pct_change(fill_method=None).iloc[-1] if hasattr(ticker, 'history') else None,
                                "1y": ticker.history(period="1y")['Close'].pct_change(fill_method=None).iloc[-1] if hasattr(ticker, 'history') else None
                            }
                        }
                    }
                except Exception as e:
                    print(f"获取表现公司 '{symbol}' 的详细信息时出错: {str(e)}")
        
        return result
    
    def to_json(self, path: Optional[str] = None, include_details: bool = False) -> Optional[str]:
        """
        将行业信息转换为 JSON 格式
        
        参数:
            path (Optional[str]): 如果提供，将 JSON 保存到此路径
            include_details (bool): 是否包含详细信息
            
        返回:
            Optional[str]: 如果未提供路径，则返回 JSON 字符串
        """
        # 基本行业信息
        result = {
            "key": self.key,
            "name": self.name,
            "symbol": self.symbol,
            "sector_key": self.sector_key,
            "sector_name": self.sector_name,
            "overview": self.overview,
            "research_reports": self.research_reports,
            "top_companies": self.top_companies.to_dict() if self.top_companies is not None else None,
            "top_growth_companies": self.top_growth_companies.to_dict() if self.top_growth_companies is not None else None,
            "top_performing_companies": self.top_performing_companies.to_dict() if self.top_performing_companies is not None else None
        }
        
        # 如果需要，添加详细信息
        if include_details:
            result["company_details"] = self.get_company_details(limit=3)
            result["growth_company_details"] = self.get_growth_company_details(limit=3)
            result["performance_company_details"] = self.get_performance_company_details(limit=3)
        
        # 保存或返回 JSON
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            return None
        else:
            return json.dumps(result, ensure_ascii=False, indent=4)
    
    def summary(self) -> Dict:
        """
        生成行业信息的摘要
        
        返回:
            Dict: 包含行业关键信息的摘要
        """
        return {
            "key": self.key,
            "name": self.name,
            "symbol": self.symbol,
            "sector": self.sector_name,
            "top_companies_count": len(self.top_companies) if self.top_companies is not None else 0,
            "top_growth_companies_count": len(self.top_growth_companies) if self.top_growth_companies is not None else 0,
            "top_performing_companies_count": len(self.top_performing_companies) if self.top_performing_companies is not None else 0,
            "top_company_names": self.top_companies['name'].head(3).tolist() if self.top_companies is not None and 'name' in self.top_companies.columns else []
        }
    
    def compare_with_industry(self, other_industry_key: str) -> Dict:
        """
        将此行业与另一个行业进行比较
        
        参数:
            other_industry_key (str): 要比较的其他行业键
            
        返回:
            Dict: 比较结果的字典
        """
        try:
            other_industry = YFinanceIndustry(other_industry_key)
            
            # 提取数据进行比较
            comparison = {
                "this_industry": {
                    "key": self.key,
                    "name": self.name,
                    "sector": self.sector_name,
                    "top_companies_count": len(self.top_companies) if self.top_companies is not None else 0,
                    "top_growth_companies_count": len(self.top_growth_companies) if self.top_growth_companies is not None else 0,
                    "top_performing_companies_count": len(self.top_performing_companies) if self.top_performing_companies is not None else 0
                },
                "other_industry": {
                    "key": other_industry.key,
                    "name": other_industry.name,
                    "sector": other_industry.sector_name,
                    "top_companies_count": len(other_industry.top_companies) if other_industry.top_companies is not None else 0,
                    "top_growth_companies_count": len(other_industry.top_growth_companies) if other_industry.top_growth_companies is not None else 0,
                    "top_performing_companies_count": len(other_industry.top_performing_companies) if other_industry.top_performing_companies is not None else 0
                }
            }
            
            # 尝试比较两个行业的表现
            if self.symbol and other_industry.symbol:
                this_ticker = yf.Ticker(self.symbol)
                other_ticker = yf.Ticker(other_industry.symbol)
                
                this_history = this_ticker.history(period="1y")
                other_history = other_ticker.history(period="1y")
                
                if not this_history.empty and not other_history.empty:
                    this_return = (this_history['Close'].iloc[-1] / this_history['Close'].iloc[0] - 1) * 100
                    other_return = (other_history['Close'].iloc[-1] / other_history['Close'].iloc[0] - 1) * 100
                    
                    comparison["performance_comparison"] = {
                        f"{self.name}_1y_return": this_return,
                        f"{other_industry.name}_1y_return": other_return,
                        "difference": this_return - other_return
                    }
            
            return comparison
        except Exception as e:
            print(f"比较行业时出错: {str(e)}")
            return {"error": str(e)}
    
    def get_industry_performance(self, period: str = "1y") -> Dict:
        """
        获取行业表现指标
        
        参数:
            period (str): 时间段 ('1mo', '3mo', '6mo', '1y', '2y', '5y', 'ytd', 'max')
            
        返回:
            Dict: 行业表现指标的字典
        """
        if not self.symbol:
            return {"error": "行业没有有效的符号"}
        
        try:
            ticker = yf.Ticker(self.symbol)
            history = ticker.history(period=period)
            
            if history.empty:
                return {"error": "无法获取历史数据"}
            
            # 计算表现指标
            start_price = history['Close'].iloc[0]
            end_price = history['Close'].iloc[-1]
            percent_change = ((end_price - start_price) / start_price) * 100
            
            # 计算波动性
            daily_returns = history['Close'].pct_change().dropna()
            volatility = daily_returns.std() * (252 ** 0.5) * 100  # 年化波动率
            
            # 计算最大回撤
            cumulative_returns = (1 + daily_returns).cumprod()
            running_max = cumulative_returns.cummax()
            drawdown = (cumulative_returns / running_max - 1) * 100
            max_drawdown = drawdown.min()
            
            return {
                "industry": self.name,
                "period": period,
                "start_date": history.index[0].strftime('%Y-%m-%d'),
                "end_date": history.index[-1].strftime('%Y-%m-%d'),
                "start_price": start_price,
                "end_price": end_price,
                "percent_change": percent_change,
                "annualized_volatility": volatility,
                "max_drawdown": max_drawdown,
                "trading_days": len(history)
            }
        except Exception as e:
            print(f"获取行业表现时出错: {str(e)}")
            return {"error": str(e)}
    
    def get_company_comparison(self, metrics: List[str] = None) -> pd.DataFrame:
        """
        比较行业内顶级公司的关键指标
        
        参数:
            metrics (List[str]): 要比较的指标列表（如果为 None，则使用默认指标）
            
        返回:
            pd.DataFrame: 公司比较的 DataFrame
        """
        if self.top_companies is None or len(self.top_companies) == 0:
            return pd.DataFrame()
        
        if metrics is None:
            metrics = ['marketCap', 'trailingPE', 'forwardPE', 'dividendYield', 'returnOnEquity', 'debtToEquity']
        
        comparison_data = []
        
        # 假设 top_companies 是一个 DataFrame，包含 'symbol' 列
        if 'symbol' in self.top_companies.columns:
            for _, row in self.top_companies.head(10).iterrows():  # 限制为前 10 家公司
                symbol = row['symbol']
                name = row.get('name', symbol)
                
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    company_data = {"symbol": symbol, "name": name}
                    
                    # 收集所请求的指标
                    for metric in metrics:
                        company_data[metric] = info.get(metric, None)
                    
                    comparison_data.append(company_data)
                except Exception as e:
                    print(f"获取公司 '{symbol}' 的比较数据时出错: {str(e)}")
        
        # 创建 DataFrame
        comparison_df = pd.DataFrame(comparison_data)
        
        return comparison_df


# 使用示例
if __name__ == "__main__":
    # 创建软件应用行业对象
    software_industry = YFinanceIndustry("software-application")
    
    # 获取行业的基本信息
    print("软件应用行业信息:")
    print(f"名称: {software_industry.name}")
    print(f"符号: {software_industry.symbol}")
    print(f"所属部门: {software_industry.sector_name}")
    
    # 获取行业的顶级公司
    print("\n软件应用行业的顶级公司:")
    print(software_industry.top_companies)
    
    # 获取行业的顶级增长公司
    print("\n软件应用行业的顶级增长公司:")
    print(software_industry.top_growth_companies)
    
    # 获取行业的表现
    print("\n软件应用行业表现:")
    performance = software_industry.get_industry_performance(period="1y")
    print(performance)
    
    # 比较行业内公司
    print("\n软件应用行业内公司比较:")
    comparison = software_industry.get_company_comparison()
    print(comparison)
    
    # 生成行业摘要
    print("\n软件应用行业摘要:")
    print(software_industry.summary())
    
    # 将行业信息导出为 JSON
    software_industry.to_json("software_industry.json")
    
    # 与另一个行业比较
    print("\n与互联网内容信息行业比较:")
    comparison = software_industry.compare_with_industry("internet-content-information")
    print(comparison)