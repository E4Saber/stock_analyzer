import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional, Any, Union
import json

class YFinanceSector:
    """
    基于 yfinance.Sector 的增强部门模块，提供对金融市场部门数据的全面访问
    """
    
    # 所有有效的部门键列表
    VALID_SECTORS = [
        "basic-materials",
        "communication-services",
        "consumer-cyclical",
        "consumer-defensive",
        "energy",
        "financial-services",
        "healthcare",
        "industrials",
        "real-estate",
        "technology",
        "utilities"
    ]
    
    def __init__(
        self,
        key: str,
        session: Optional[Any] = None,
        proxy: Optional[Dict] = None
    ):
        """
        初始化 YFinanceSector 对象
        
        参数:
            key (str): 表示部门的键
            session (requests.Session, optional): 用于发送请求的会话，默认为 None
            proxy (dict, optional): 包含请求代理设置的字典，默认为 None
        """
        # 验证部门键是否有效
        if key not in self.VALID_SECTORS:
            print(f"警告: '{key}' 可能不是有效的部门键。有效键包括: {', '.join(self.VALID_SECTORS)}")
        
        self.key = key
        self.session = session
        self.proxy = proxy
        
        # 初始化 yfinance.Sector 对象
        self._sector = yf.Sector(
            key=self.key,
            session=self.session,
            proxy=self.proxy
        )
        
        # 缓存特性，用于减少 API 调用
        self._cached_industries = None
        self._cached_top_etfs = None
        self._cached_top_mutual_funds = None
        self._cached_top_companies = None
        self._cached_overview = None
        self._cached_research_reports = None
    
    @property
    def name(self) -> str:
        """
        获取部门的名称
        
        返回:
            str: 部门的名称
        """
        return self._sector.name
    
    @property
    def symbol(self) -> str:
        """
        获取表示部门的符号
        
        返回:
            str: 表示部门的符号
        """
        return self._sector.symbol
    
    @property
    def industries(self) -> pd.DataFrame:
        """
        获取部门内的行业
        
        返回:
            pandas.DataFrame: 包含行业的键、名称、符号和市场权重的 DataFrame
        """
        if self._cached_industries is None:
            self._cached_industries = self._sector.industries
        return self._cached_industries
    
    @property
    def top_etfs(self) -> Dict[str, str]:
        """
        获取部门的顶级 ETF
        
        返回:
            Dict[str, str]: ETF 符号和名称的字典
        """
        if self._cached_top_etfs is None:
            self._cached_top_etfs = self._sector.top_etfs
        return self._cached_top_etfs
    
    @property
    def top_mutual_funds(self) -> Dict[str, str]:
        """
        获取部门的顶级共同基金
        
        返回:
            Dict[str, str]: 共同基金符号和名称的字典
        """
        if self._cached_top_mutual_funds is None:
            self._cached_top_mutual_funds = self._sector.top_mutual_funds
        return self._cached_top_mutual_funds
    
    @property
    def top_companies(self) -> pd.DataFrame:
        """
        获取部门内的顶级公司
        
        返回:
            pandas.DataFrame: 包含域中顶级公司的 DataFrame
        """
        if self._cached_top_companies is None:
            self._cached_top_companies = self._sector.top_companies
        return self._cached_top_companies
    
    @property
    def overview(self) -> Dict:
        """
        获取部门的概述信息
        
        返回:
            Dict: 包含部门概述的字典
        """
        if self._cached_overview is None:
            self._cached_overview = self._sector.overview
        return self._cached_overview
    
    @property
    def research_reports(self) -> List[Dict[str, str]]:
        """
        获取与部门相关的研究报告
        
        返回:
            List[Dict[str, str]]: 研究报告列表，每个报告是一个包含元数据的字典
        """
        if self._cached_research_reports is None:
            self._cached_research_reports = self._sector.research_reports
        return self._cached_research_reports
    
    def get_ticker(self) -> yf.Ticker:
        """
        获取基于部门符号的 Ticker 对象
        
        返回:
            yf.Ticker: 与部门关联的 Ticker 对象
        """
        return self._sector.ticker
    
    def get_industry_details(self, industry_key: str) -> Dict:
        """
        获取特定行业的详细信息
        
        参数:
            industry_key (str): 行业的键
            
        返回:
            Dict: 包含行业详细信息的字典
        """
        # 检查行业键是否存在于此部门中
        if self.industries is not None and 'key' in self.industries.columns:
            if industry_key not in self.industries['key'].values:
                print(f"警告: '{industry_key}' 不在 '{self.key}' 部门的行业列表中")
        
        try:
            # 创建行业对象
            industry = yf.Industry(industry_key)
            
            # 收集行业详细信息
            details = {
                "key": industry.key,
                "name": industry.name,
                "symbol": industry.symbol,
                "overview": industry.overview,
                "research_reports": industry.research_reports,
                "top_companies": industry.top_companies,
            }
            
            return details
        except Exception as e:
            print(f"获取行业 '{industry_key}' 的详细信息时出错: {str(e)}")
            return {}
    
    def get_etf_details(self, limit: int = 5) -> Dict[str, Dict]:
        """
        获取部门顶级 ETF 的详细信息
        
        参数:
            limit (int): 要获取的 ETF 的数量限制
            
        返回:
            Dict[str, Dict]: ETF 符号到详细信息的映射
        """
        result = {}
        
        if not self.top_etfs:
            return result
        
        for i, (symbol, name) in enumerate(self.top_etfs.items()):
            if i >= limit:
                break
            
            try:
                ticker = yf.Ticker(symbol)
                
                # 收集 ETF 详细信息
                result[symbol] = {
                    "name": name,
                    "info": ticker.info,
                    "holdings": ticker.get_holdings() if hasattr(ticker, 'get_holdings') else None,
                    "history": ticker.history(period="1mo").tail(5).to_dict() if hasattr(ticker, 'history') else None
                }
            except Exception as e:
                print(f"获取 ETF '{symbol}' 的详细信息时出错: {str(e)}")
        
        return result
    
    def get_mutual_fund_details(self, limit: int = 5) -> Dict[str, Dict]:
        """
        获取部门顶级共同基金的详细信息
        
        参数:
            limit (int): 要获取的共同基金的数量限制
            
        返回:
            Dict[str, Dict]: 共同基金符号到详细信息的映射
        """
        result = {}
        
        if not self.top_mutual_funds:
            return result
        
        for i, (symbol, name) in enumerate(self.top_mutual_funds.items()):
            if i >= limit:
                break
            
            try:
                ticker = yf.Ticker(symbol)
                
                # 收集共同基金详细信息
                result[symbol] = {
                    "name": name,
                    "info": ticker.info,
                    "holdings": ticker.get_holdings() if hasattr(ticker, 'get_holdings') else None,
                    "history": ticker.history(period="1mo").tail(5).to_dict() if hasattr(ticker, 'history') else None
                }
            except Exception as e:
                print(f"获取共同基金 '{symbol}' 的详细信息时出错: {str(e)}")
        
        return result
    
    def get_company_details(self, limit: int = 5) -> Dict[str, Dict]:
        """
        获取部门顶级公司的详细信息
        
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
                        "info": ticker.info,
                        "financials": ticker.financials.to_dict() if hasattr(ticker, 'financials') and ticker.financials is not None else None,
                        "major_holders": ticker.major_holders.to_dict() if hasattr(ticker, 'major_holders') and ticker.major_holders is not None else None,
                        "recommendations": ticker.get_recommendations().to_dict() if hasattr(ticker, 'get_recommendations') else None
                    }
                except Exception as e:
                    print(f"获取公司 '{symbol}' 的详细信息时出错: {str(e)}")
        
        return result
    
    def to_json(self, path: Optional[str] = None, include_details: bool = False) -> Optional[str]:
        """
        将部门信息转换为 JSON 格式
        
        参数:
            path (Optional[str]): 如果提供，将 JSON 保存到此路径
            include_details (bool): 是否包含详细信息（ETF、共同基金、公司）
            
        返回:
            Optional[str]: 如果未提供路径，则返回 JSON 字符串
        """
        # 基本部门信息
        result = {
            "key": self.key,
            "name": self.name,
            "symbol": self.symbol,
            "overview": self.overview,
            "research_reports": self.research_reports,
            "industries": self.industries.to_dict() if self.industries is not None else None,
            "top_etfs": self.top_etfs,
            "top_mutual_funds": self.top_mutual_funds,
            "top_companies": self.top_companies.to_dict() if self.top_companies is not None else None
        }
        
        # 如果需要，添加详细信息
        if include_details:
            result["etf_details"] = self.get_etf_details(limit=3)
            result["mutual_fund_details"] = self.get_mutual_fund_details(limit=3)
            result["company_details"] = self.get_company_details(limit=3)
        
        # 保存或返回 JSON
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            return None
        else:
            return json.dumps(result, ensure_ascii=False, indent=4)
    
    def summary(self) -> Dict:
        """
        生成部门信息的摘要
        
        返回:
            Dict: 包含部门关键信息的摘要
        """
        return {
            "key": self.key,
            "name": self.name,
            "industries_count": len(self.industries) if self.industries is not None else 0,
            "top_etfs_count": len(self.top_etfs) if self.top_etfs is not None else 0,
            "top_mutual_funds_count": len(self.top_mutual_funds) if self.top_mutual_funds is not None else 0,
            "top_companies_count": len(self.top_companies) if self.top_companies is not None else 0,
            "top_industries": self.industries['name'].head(3).tolist() if self.industries is not None and 'name' in self.industries.columns else [],
            "top_etf_names": list(self.top_etfs.values())[:3] if self.top_etfs is not None else []
        }
    
    @classmethod
    def get_all_sectors(cls) -> List[str]:
        """
        获取所有有效部门的列表
        
        返回:
            List[str]: 所有有效部门键的列表
        """
        return cls.VALID_SECTORS
    
    @classmethod
    def get_sector_industry_map(cls) -> Dict[str, List[str]]:
        """
        获取部门到行业的映射
        
        返回:
            Dict[str, List[str]]: 每个部门键到其行业列表的映射
        """
        result = {}
        
        for sector_key in cls.VALID_SECTORS:
            try:
                sector = cls(sector_key)
                if sector.industries is not None and 'key' in sector.industries.columns:
                    result[sector_key] = sector.industries['key'].tolist()
                else:
                    result[sector_key] = []
            except Exception as e:
                print(f"获取部门 '{sector_key}' 的行业列表时出错: {str(e)}")
                result[sector_key] = []
        
        return result

    def get_industries_performance(self) -> pd.DataFrame:
        """
        获取部门内所有行业的性能指标（如果可用）
        
        返回:
            pd.DataFrame: 行业性能指标的 DataFrame
        """
        if self.industries is None or len(self.industries) == 0:
            return pd.DataFrame()
        
        performance_data = []
        
        # 假设 industries 是一个 DataFrame，包含 'key' 和 'symbol' 列
        if 'key' in self.industries.columns:
            for _, row in self.industries.iterrows():
                industry_key = row['key']
                industry_name = row['name'] if 'name' in row else industry_key
                
                try:
                    # 尝试创建行业对象
                    industry = yf.Industry(industry_key)
                    
                    # 尝试获取行业符号的历史数据
                    if hasattr(industry, 'symbol') and industry.symbol:
                        ticker = yf.Ticker(industry.symbol)
                        history = ticker.history(period="1mo")
                        
                        if not history.empty:
                            # 计算性能指标
                            first_price = history['Close'].iloc[0] if not history['Close'].empty else None
                            last_price = history['Close'].iloc[-1] if not history['Close'].empty else None
                            percent_change = ((last_price - first_price) / first_price * 100) if first_price and last_price else None
                            
                            performance_data.append({
                                'Industry Key': industry_key,
                                'Industry Name': industry_name,
                                'Symbol': industry.symbol,
                                'Start Price': first_price,
                                'End Price': last_price,
                                'Percent Change': percent_change
                            })
                except Exception as e:
                    print(f"获取行业 '{industry_key}' 的性能指标时出错: {str(e)}")
        
        # 创建 DataFrame 并按性能排序
        performance_df = pd.DataFrame(performance_data)
        if not performance_df.empty and 'Percent Change' in performance_df.columns:
            performance_df = performance_df.sort_values(by='Percent Change', ascending=False)
        
        return performance_df

    def compare_to_other_sectors(self, other_sectors: List[str] = None, metric: str = 'top_companies') -> pd.DataFrame:
        """
        将此部门与其他部门进行比较
        
        参数:
            other_sectors (List[str]): 要比较的其他部门键的列表，如果为 None，则使用所有部门
            metric (str): 要比较的指标 ('top_companies', 'industries', 'top_etfs', 'top_mutual_funds')
            
        返回:
            pd.DataFrame: 比较结果的 DataFrame
        """
        if other_sectors is None:
            other_sectors = [s for s in self.VALID_SECTORS if s != self.key]
        
        comparison_data = []
        
        # 将当前部门添加到比较数据中
        if metric == 'top_companies':
            current_count = len(self.top_companies) if self.top_companies is not None else 0
        elif metric == 'industries':
            current_count = len(self.industries) if self.industries is not None else 0
        elif metric == 'top_etfs':
            current_count = len(self.top_etfs) if self.top_etfs is not None else 0
        elif metric == 'top_mutual_funds':
            current_count = len(self.top_mutual_funds) if self.top_mutual_funds is not None else 0
        else:
            raise ValueError(f"不支持的指标 '{metric}'")
        
        comparison_data.append({
            'Sector Key': self.key,
            'Sector Name': self.name,
            f'{metric.capitalize()} Count': current_count
        })
        
        # 获取其他部门的比较数据
        for sector_key in other_sectors:
            try:
                sector = YFinanceSector(sector_key)
                
                if metric == 'top_companies':
                    count = len(sector.top_companies) if sector.top_companies is not None else 0
                elif metric == 'industries':
                    count = len(sector.industries) if sector.industries is not None else 0
                elif metric == 'top_etfs':
                    count = len(sector.top_etfs) if sector.top_etfs is not None else 0
                elif metric == 'top_mutual_funds':
                    count = len(sector.top_mutual_funds) if sector.top_mutual_funds is not None else 0
                
                comparison_data.append({
                    'Sector Key': sector_key,
                    'Sector Name': sector.name,
                    f'{metric.capitalize()} Count': count
                })
            except Exception as e:
                print(f"比较部门 '{sector_key}' 时出错: {str(e)}")
        
        # 创建 DataFrame 并按指标计数排序
        comparison_df = pd.DataFrame(comparison_data)
        if not comparison_df.empty and f'{metric.capitalize()} Count' in comparison_df.columns:
            comparison_df = comparison_df.sort_values(by=f'{metric.capitalize()} Count', ascending=False)
        
        return comparison_df


# 使用示例
if __name__ == "__main__":
    # 创建技术部门对象
    tech_sector = YFinanceSector("technology")
    
    # 获取部门的行业
    print("技术部门的行业:")
    print(tech_sector.industries)
    
    # 获取部门的顶级 ETF
    print("\n技术部门的顶级 ETF:")
    print(tech_sector.top_etfs)
    
    # 获取部门的顶级共同基金
    print("\n技术部门的顶级共同基金:")
    print(tech_sector.top_mutual_funds)
    
    # 获取部门的顶级公司
    print("\n技术部门的顶级公司:")
    print(tech_sector.top_companies)
    
    # 获取特定行业的详细信息
    print("\n软件行业的详细信息:")
    software_details = tech_sector.get_industry_details("software-application")
    print(software_details)
    
    # 生成部门摘要
    print("\n技术部门摘要:")
    print(tech_sector.summary())
    
    # 将部门信息导出为 JSON
    tech_sector.to_json("technology_sector.json")
    
    # 获取所有部门
    print("\n所有有效部门:")
    print(YFinanceSector.get_all_sectors())
    
    # 比较与其他部门
    print("\n部门比较 (基于行业计数):")
    comparison = tech_sector.compare_to_other_sectors(metric="industries")
    print(comparison)