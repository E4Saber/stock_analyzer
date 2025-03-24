import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional, Union, Any
import json

class YFinanceSearch:
    """
    基于 yfinance.Search 的增强搜索模块，提供雅虎财经搜索的全部功能
    """
    
    def __init__(
        self,
        query: str,
        max_results: int = 8,
        news_count: int = 8,
        lists_count: int = 8,
        include_cb: bool = True,
        include_nav_links: bool = False,
        include_research: bool = False,
        include_cultural_assets: bool = False,
        enable_fuzzy_query: bool = False,
        recommended: int = 8,
        session: Optional[Any] = None,
        proxy: Optional[str] = None,
        timeout: int = 30,
        raise_errors: bool = True
    ):
        """
        初始化 FinanceSearch 对象
        
        参数:
            query (str): 搜索查询（股票代码或公司名称）
            max_results (int): 返回的最大股票引用数量（默认为8）
            news_count (int): 包含的新闻文章数量（默认为8）
            lists_count (int): 包含的列表数量（默认为8）
            include_cb (bool): 是否包含公司分析（默认为True）
            include_nav_links (bool): 是否包含导航链接（默认为False）
            include_research (bool): 是否包含研究报告（默认为False）
            include_cultural_assets (bool): 是否包含文化资产（默认为False）
            enable_fuzzy_query (bool): 是否启用模糊搜索（默认为False）
            recommended (int): 建议返回的结果数量（默认为8）
            session (Optional): 自定义HTTP会话（默认为None）
            proxy (Optional[str]): 代理设置（默认为None）
            timeout (int): 请求超时秒数（默认为30）
            raise_errors (bool): 出错时是否抛出异常（默认为True）
        """
        self.query = query
        self.max_results = max_results
        self.news_count = news_count
        self.lists_count = lists_count
        self.include_cb = include_cb
        self.include_nav_links = include_nav_links
        self.include_research = include_research
        self.include_cultural_assets = include_cultural_assets
        self.enable_fuzzy_query = enable_fuzzy_query
        self.recommended = recommended
        self.session = session
        self.proxy = proxy
        self.timeout = timeout
        self.raise_errors = raise_errors
        
        # 初始化 yfinance.Search 对象
        self.search_obj = yf.Search(
            query=self.query,
            max_results=self.max_results,
            news_count=self.news_count,
            lists_count=self.lists_count,
            include_cb=self.include_cb,
            include_nav_links=self.include_nav_links,
            include_research=self.include_research,
            include_cultural_assets=self.include_cultural_assets,
            enable_fuzzy_query=self.enable_fuzzy_query,
            recommended=self.recommended,
            session=self.session,
            proxy=self.proxy,
            timeout=self.timeout,
            raise_errors=self.raise_errors
        )
        
        # 执行搜索
        self.search_obj.search()
    
    def search(self) -> 'YFinanceSearch':
        """
        使用构造函数中定义的查询参数执行搜索
        
        返回:
            FinanceSearch: 返回自身，用于链式调用
        """
        self.search_obj.search()
        return self
    
    @property
    def quotes(self) -> List[Dict]:
        """
        获取搜索结果中的股票报价
        
        返回:
            List[Dict]: 股票报价列表
        """
        return self.search_obj.quotes
    
    @property
    def quotes_df(self) -> pd.DataFrame:
        """
        获取搜索结果中的股票报价，转换为 DataFrame 格式
        
        返回:
            pd.DataFrame: 包含股票报价的 DataFrame
        """
        if not self.quotes:
            return pd.DataFrame()
        return pd.DataFrame(self.quotes)
    
    @property
    def news(self) -> List[Dict]:
        """
        获取搜索结果中的新闻
        
        返回:
            List[Dict]: 新闻文章列表
        """
        return self.search_obj.news
    
    @property
    def news_df(self) -> pd.DataFrame:
        """
        获取搜索结果中的新闻，转换为 DataFrame 格式
        
        返回:
            pd.DataFrame: 包含新闻的 DataFrame
        """
        if not self.news:
            return pd.DataFrame()
        return pd.DataFrame(self.news)
    
    @property
    def lists(self) -> List[Dict]:
        """
        获取搜索结果中的列表
        
        返回:
            List[Dict]: 列表结果
        """
        return self.search_obj.lists
    
    @property
    def lists_df(self) -> pd.DataFrame:
        """
        获取搜索结果中的列表，转换为 DataFrame 格式
        
        返回:
            pd.DataFrame: 包含列表的 DataFrame
        """
        if not self.lists:
            return pd.DataFrame()
        return pd.DataFrame(self.lists)
    
    @property
    def nav(self) -> List[Dict]:
        """
        获取搜索结果中的导航链接
        
        返回:
            List[Dict]: 导航链接列表
        """
        return self.search_obj.nav
    
    @property
    def research(self) -> List[Dict]:
        """
        获取搜索结果中的研究报告
        
        返回:
            List[Dict]: 研究报告列表
        """
        return self.search_obj.research
    
    @property
    def all(self) -> Dict[str, List]:
        """
        获取搜索结果的过滤版本
        
        返回:
            Dict[str, List]: 所有搜索结果
        """
        return self.search_obj.all
    
    @property
    def response(self) -> Dict:
        """
        获取搜索结果的原始响应
        
        返回:
            Dict: 原始搜索响应
        """
        return self.search_obj.response
    
    def to_json(self, path: Optional[str] = None) -> Optional[str]:
        """
        将所有搜索结果转换为 JSON 格式
        
        参数:
            path (Optional[str]): 如果提供，将 JSON 保存到此路径
            
        返回:
            Optional[str]: 如果未提供路径，则返回 JSON 字符串
        """
        result = {
            "query": self.query,
            "quotes": self.quotes,
            "news": self.news,
            "lists": self.lists,
            "nav": self.nav,
            "research": self.research
        }
        
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            return None
        else:
            return json.dumps(result, ensure_ascii=False, indent=4)
    
    def get_ticker_details(self, ticker_symbol: Optional[str] = None) -> Dict:
        """
        获取特定股票代码或搜索结果中第一个股票的详细信息
        
        参数:
            ticker_symbol (Optional[str]): 股票代码，如果为 None，则使用搜索结果中的第一个股票
            
        返回:
            Dict: 股票详细信息
        """
        if ticker_symbol is None:
            if not self.quotes:
                return {}
            ticker_symbol = self.quotes[0].get('symbol')
            
        if not ticker_symbol:
            return {}
            
        ticker = yf.Ticker(ticker_symbol)
        
        return {
            "info": ticker.info,
            "recommendations": ticker.get_recommendations(),
            "major_holders": ticker.major_holders,
            "institutional_holders": ticker.institutional_holders,
            "balance_sheet": ticker.balance_sheet,
            "cashflow": ticker.cashflow,
            "earnings": ticker.income_stmt,
            "sustainability": ticker.sustainability
        }
    
    def get_multiple_tickers(self, limit: int = 5) -> Dict[str, yf.Ticker]:
        """
        获取搜索结果中的多个股票对象
        
        参数:
            limit (int): 要获取的股票对象数量限制
            
        返回:
            Dict[str, yf.Ticker]: 股票代码到 Ticker 对象的映射
        """
        result = {}
        
        if not self.quotes:
            return result
            
        for i, quote in enumerate(self.quotes):
            if i >= limit:
                break
                
            symbol = quote.get('symbol')
            if symbol:
                result[symbol] = yf.Ticker(symbol)
                
        return result
    
    def summary(self) -> Dict:
        """
        生成搜索结果的摘要
        
        返回:
            Dict: 包含搜索结果关键信息的摘要
        """
        return {
            "query": self.query,
            "quotes_count": len(self.quotes),
            "news_count": len(self.news),
            "lists_count": len(self.lists),
            "top_quotes": [q.get('symbol') for q in self.quotes[:3]] if self.quotes else [],
            "top_news_titles": [n.get('title') for n in self.news[:3]] if self.news else []
        }


# 使用示例
if __name__ == "__main__":
    # 创建搜索对象
    search = YFinanceSearch(
        query="AAPL",
        max_results=5,
        news_count=3,
        include_research=True
    )
    
    # 查看股票报价
    print("股票报价:")
    print(search.quotes_df)
    
    # 查看新闻
    print("\n相关新闻:")
    print(search.news_df)
    
    # 获取特定股票的详细信息
    print("\n股票详情:")
    details = search.get_ticker_details()
    print(f"公司名称: {details['info'].get('longName')}")
    print(f"行业: {details['info'].get('industry')}")
    print(f"当前价格: {details['info'].get('currentPrice')}")
    
    # 生成摘要
    print("\n搜索摘要:")
    print(search.summary())
    
    # 导出为JSON
    search.to_json("apple_search_results.json")