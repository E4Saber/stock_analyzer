import yfinance as yf
from typing import Union, List, Dict, Any, Optional
from yfinance import EquityQuery, FundQuery  # 导入yfinance原生的查询类


class Screener:
    """股票和基金筛选模块"""
    
    def __init__(self):
        """初始化筛选模块，加载预定义查询"""
        self.predefined_queries = yf.PREDEFINED_SCREENER_QUERIES
    
    def get_predefined_queries(self) -> List[str]:
        """
        获取所有预定义查询的名称
        
        返回:
            所有可用预定义查询的名称列表
        """
        return list(self.predefined_queries.keys())
    
    def get_predefined_query_details(self, query_name: str) -> Dict:
        """
        获取指定预定义查询的详细信息
        
        参数:
            query_name: 预定义查询的名称
            
        返回:
            查询的详细配置信息
        """
        if query_name not in self.predefined_queries:
            raise ValueError(f"查询 '{query_name}' 不存在。可用查询: {', '.join(self.get_predefined_queries())}")
        
        return self.predefined_queries[query_name]
    
    def screen(self, 
               query: Union[str, EquityQuery, FundQuery], 
               offset: Optional[int] = None, 
               size: Optional[int] = None, 
               sort_field: Optional[str] = None, 
               sort_asc: Optional[bool] = None, 
               user_id: Optional[str] = None, 
               user_id_type: Optional[str] = None,
               session = None,
               proxy = None) -> Dict[str, Any]:
        """
        执行筛选查询
        
        参数:
            query: 要执行的查询，可以是预定义查询的名称或自定义查询对象
            offset: 结果的偏移量，默认为0
            size: 返回结果的数量，默认为100，最大为250
            sort_field: 排序字段，默认为"ticker"
            sort_asc: 是否升序排序，默认为False
            user_id: 用户ID，默认为空
            user_id_type: 用户ID类型，默认为"guid"
            session: 会话对象，用于HTTP请求
            proxy: 代理设置
            
        返回:
            筛选结果
        """
        return yf.screen(
            query=query,
            offset=offset,
            size=size,
            sortField=sort_field,
            sortAsc=sort_asc,
            userId=user_id,
            userIdType=user_id_type,
            session=session,
            proxy=proxy
        )
    
    def create_equity_query(self, operator: str, parameters: List) -> EquityQuery:
        """
        创建股票查询对象
        
        参数:
            operator: 操作符
            parameters: 参数列表
            
        返回:
            EquityQuery对象
        """
        return EquityQuery(operator, parameters)
    
    def create_fund_query(self, operator: str, parameters: List) -> FundQuery:
        """
        创建基金查询对象
        
        参数:
            operator: 操作符
            parameters: 参数列表
            
        返回:
            FundQuery对象
        """
        return FundQuery(operator, parameters)
    
    def create_compound_equity_query(self, logical_op: str, conditions: List[EquityQuery]) -> EquityQuery:
        """
        创建复合股票查询条件
        
        参数:
            logical_op: 逻辑操作符，'and' 或 'or'
            conditions: EquityQuery对象列表
            
        返回:
            复合EquityQuery对象
        """
        return EquityQuery(logical_op, conditions)
    
    def create_compound_fund_query(self, logical_op: str, conditions: List[FundQuery]) -> FundQuery:
        """
        创建复合基金查询条件
        
        参数:
            logical_op: 逻辑操作符，'and' 或 'or'
            conditions: FundQuery对象列表
            
        返回:
            复合FundQuery对象
        """
        return FundQuery(logical_op, conditions)


# 常用查询操作符
class Operators:
    AND = "AND"
    OR = "OR"
    GT = "GT"  # 大于
    LT = "LT"  # 小于
    GTE = "GTE"  # 大于等于
    LTE = "LTE"  # 小于等于
    EQ = "EQ"  # 等于
    BTWN = "BTWN"  # 介于...之间
    IS_IN = "IS-IN"  # 在列表中


# 使用示例
if __name__ == "__main__":
    # 创建筛选模块实例
    screener = Screener()
    
    # 示例1: 使用预定义查询
    print("预定义查询列表:", screener.get_predefined_queries())
    
    # 获取日涨幅最大的股票
    day_gainers = screener.screen("day_gainers")
    print(f"日涨幅最大的股票数量: {len(day_gainers['quotes'])}")
    
    # 示例2: 创建自定义查询 - 查找美国地区涨幅超过3%的股票
    q1 = screener.create_equity_query(Operators.GT, ["percentchange", 3])
    q2 = screener.create_equity_query(Operators.EQ, ["region", "us"])
    custom_query = screener.create_compound_equity_query(Operators.AND, [q1, q2])
    
    results = screener.screen(
        query=custom_query,
        sort_field="percentchange",
        sort_asc=True
    )
    
    print(f"自定义查询结果数量: {len(results['quotes'])}")
    
    # 示例3: 查找表现优秀的大型成长基金
    large_growth_funds = screener.screen("solid_large_growth_funds", size=10)
    print(f"大型成长基金数量: {len(large_growth_funds['quotes'])}")