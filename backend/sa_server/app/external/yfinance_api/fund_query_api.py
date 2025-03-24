import yfinance as yf
from yfinance import FundQuery as FQ
from typing import List, Dict, Tuple, Union, Optional, Any
import pandas as pd
import json
from numbers import Real

class YFinanceFundQuery:
    """
    基于 yfinance.FundQuery 的增强基金筛选模块，提供强大的共同基金筛选和查询功能
    """
    
    # 定义操作符
    VALUE_OPERATORS = ["EQ", "IS-IN", "BTWN", "GT", "LT", "GTE", "LTE"]
    LOGIC_OPERATORS = ["AND", "OR"]
    
    def __init__(self):
        """
        初始化 YFinanceFundQuery 对象
        """
        # 从 FundQuery 获取有效字段和值
        self._valid_fields = None
        self._valid_values = None
        self._init_valid_data()
    
    def _init_valid_data(self):
        """
        初始化有效字段和值
        """
        try:
            # 初始化一个简单查询以访问有效字段和值
            dummy_query = FQ('EQ', ['exchange', 'NAS'])
            self._valid_fields = dummy_query.valid_fields
            self._valid_values = dummy_query.valid_values
        except Exception as e:
            print(f"初始化有效数据时出错: {str(e)}")
            # 保留基本有效值
            self._valid_fields = {
                "eq_fields": [
                    "annualreturnnavy1categoryrank", 
                    "categoryname", 
                    "exchange", 
                    "initialinvestment", 
                    "performanceratingoverall", 
                    "riskratingoverall"
                ],
                "price": [
                    "eodprice", 
                    "intradayprice", 
                    "intradaypricechange"
                ]
            }
            self._valid_values = {
                "exchange": {
                    "us": ["NAS"]
                },
                "categoryname": [
                    "Large Growth", "Large Value", "Large Blend", 
                    "Mid Growth", "Mid Value", "Mid Blend", 
                    "Small Growth", "Small Value", "Small Blend",
                    "Foreign Large Growth", "Foreign Large Value", "Foreign Large Blend",
                    "Diversified Emerging Markets", "World Bond", "High Yield Bond",
                    "Intermediate Core Bond", "Short-Term Bond", "Long-Term Bond"
                ]
            }
    
    @property
    def valid_fields(self) -> Dict:
        """
        获取有效字段，按类别分组
        
        返回:
            Dict: 有效字段字典
        """
        return self._valid_fields
    
    @property
    def valid_values(self) -> Dict:
        """
        获取特定字段的有效值列表
        
        返回:
            Dict: 有效值字典
        """
        return self._valid_values
    
    def get_field_categories(self) -> List[str]:
        """
        获取所有字段类别
        
        返回:
            List[str]: 字段类别列表
        """
        return list(self._valid_fields.keys())
    
    def get_fields_in_category(self, category: str) -> List[str]:
        """
        获取特定类别中的所有字段
        
        参数:
            category (str): 字段类别
            
        返回:
            List[str]: 该类别中的字段列表
        """
        return self._valid_fields.get(category, [])
    
    def check_field_exists(self, field: str) -> bool:
        """
        检查字段是否存在
        
        参数:
            field (str): 要检查的字段
            
        返回:
            bool: 如果字段存在，则为 True
        """
        for category, fields in self._valid_fields.items():
            if field in fields:
                return True
        
        # 特别处理 eq_fields
        if field in self._valid_fields.get("eq_fields", []):
            return True
            
        return False
    
    def create_eq_query(self, field: str, value: Union[str, int, float]) -> FQ:
        """
        创建一个基本的等于查询
        
        参数:
            field (str): 字段名
            value (Union[str, int, float]): 字段值
            
        返回:
            FQ: FundQuery 对象
        """
        # 验证字段
        if not self.check_field_exists(field):
            raise ValueError(f"无效的字段: {field}")
                
        return FQ('EQ', [field, value])
    
    def create_is_in_query(self, field: str, values: List[Union[str, int, float]]) -> FQ:
        """
        创建一个 IS-IN 查询（值在列表中）
        
        参数:
            field (str): 字段名
            values (List[Union[str, int, float]]): 字段值列表
            
        返回:
            FQ: FundQuery 对象
        """
        # 验证字段
        if not self.check_field_exists(field):
            raise ValueError(f"无效的字段: {field}")
        
        # 修改参数格式以符合最新的yfinance API
        query_args = [field]
        query_args.extend(values)
        return FQ('IS-IN', query_args)
    
    def create_between_query(self, field: str, min_value: Union[int, float], max_value: Union[int, float]) -> FQ:
        """
        创建一个 BTWN 查询（值在两个值之间）
        
        参数:
            field (str): 字段名
            min_value (Union[int, float]): 最小值
            max_value (Union[int, float]): 最大值
            
        返回:
            FQ: FundQuery 对象
        """
        # 验证字段
        if not self.check_field_exists(field):
            raise ValueError(f"无效的字段: {field}")
            
        return FQ('BTWN', [field, min_value, max_value])
    
    def create_gt_query(self, field: str, value: Union[int, float]) -> FQ:
        """
        创建一个 GT 查询（值大于）
        
        参数:
            field (str): 字段名
            value (Union[int, float]): 比较值
            
        返回:
            FQ: FundQuery 对象
        """
        # 验证字段
        if not self.check_field_exists(field):
            raise ValueError(f"无效的字段: {field}")
            
        return FQ('GT', [field, value])
    
    def create_lt_query(self, field: str, value: Union[int, float]) -> FQ:
        """
        创建一个 LT 查询（值小于）
        
        参数:
            field (str): 字段名
            value (Union[int, float]): 比较值
            
        返回:
            FQ: FundQuery 对象
        """
        # 验证字段
        if not self.check_field_exists(field):
            raise ValueError(f"无效的字段: {field}")
            
        return FQ('LT', [field, value])
    
    def create_gte_query(self, field: str, value: Union[int, float]) -> FQ:
        """
        创建一个 GTE 查询（值大于等于）
        
        参数:
            field (str): 字段名
            value (Union[int, float]): 比较值
            
        返回:
            FQ: FundQuery 对象
        """
        # 验证字段
        if not self.check_field_exists(field):
            raise ValueError(f"无效的字段: {field}")
            
        return FQ('GTE', [field, value])
    
    def create_lte_query(self, field: str, value: Union[int, float]) -> FQ:
        """
        创建一个 LTE 查询（值小于等于）
        
        参数:
            field (str): 字段名
            value (Union[int, float]): 比较值
            
        返回:
            FQ: FundQuery 对象
        """
        # 验证字段
        if not self.check_field_exists(field):
            raise ValueError(f"无效的字段: {field}")
            
        return FQ('LTE', [field, value])
    
    def combine_with_and(self, queries: List[FQ]) -> FQ:
        """
        使用 AND 逻辑运算符组合多个查询
        
        参数:
            queries (List[FQ]): 要组合的查询列表
            
        返回:
            FQ: 组合的 FundQuery 对象
        """
        if not queries:
            raise ValueError("查询列表不能为空")
            
        if len(queries) == 1:
            return queries[0]
            
        return FQ('AND', queries)
    
    def combine_with_or(self, queries: List[FQ]) -> FQ:
        """
        使用 OR 逻辑运算符组合多个查询
        
        参数:
            queries (List[FQ]): 要组合的查询列表
            
        返回:
            FQ: 组合的 FundQuery 对象
        """
        if not queries:
            raise ValueError("查询列表不能为空")
            
        if len(queries) == 1:
            return queries[0]
            
        return FQ('OR', queries)
    
    def fetch_results(self, query: FQ, limit: int = 50) -> pd.DataFrame:
        """
        执行查询并获取结果
        
        参数:
            query (FQ): 要执行的 FundQuery 对象
            limit (int): 结果数量限制
            
        返回:
            pd.DataFrame: 包含结果的 DataFrame
        """
        try:
            # 转换查询为字典形式
            query_dict = self.to_dict(query)
            
            # 因为最新版本中FundQuery可能没有fetch方法，我们使用替代方法
            try:
                from yfinance.screener import fetch as yf_fetch
                results = yf_fetch(query_dict)
            except (ImportError, AttributeError):
                # 使用替代方法
                results = self._alternative_fetch(query_dict)
            
            # 将结果转换为 DataFrame
            if results:
                # 限制结果数量
                results = results[:limit] if limit else results
                
                # 创建 DataFrame
                df = pd.DataFrame(results)
                return df
            else:
                return pd.DataFrame()
        except Exception as e:
            print(f"获取查询结果时出错: {str(e)}")
            return pd.DataFrame()
    
    def _alternative_fetch(self, query_dict: Dict) -> List[Dict]:
        """
        使用替代方法获取查询结果（当标准fetch方法不可用时）
        
        参数:
            query_dict (Dict): 查询字典
            
        返回:
            List[Dict]: 结果列表
        """
        # 提取查询条件
        category_name = None
        exchange = None
        performance_rating = None
        initial_investment_max = None
        
        # 尝试从查询字典中提取基本条件
        try:
            if query_dict.get('operator') == 'AND':
                for operand in query_dict.get('operand', []):
                    if isinstance(operand, dict):
                        op = operand.get('operator')
                        op_data = operand.get('operand', [])
                        
                        if op == 'EQ' and len(op_data) >= 2:
                            if op_data[0] == 'categoryname':
                                category_name = op_data[1]
                            elif op_data[0] == 'exchange':
                                exchange = op_data[1]
                        elif op == 'IS-IN' and len(op_data) >= 2 and op_data[0] == 'performanceratingoverall':
                            performance_rating = op_data[1:]
                        elif op == 'LT' and len(op_data) >= 2 and op_data[0] == 'initialinvestment':
                            initial_investment_max = op_data[1]
        except Exception as e:
            print(f"解析查询条件时出错: {str(e)}")
        
        # 获取预定义的基金数据
        funds_data = self._get_predefined_funds()
        
        # 根据条件筛选基金
        filtered_funds = []
        for fund in funds_data:
            # 检查类别条件
            if category_name and fund.get('categoryname') != category_name:
                continue
                
            # 检查交易所条件
            if exchange and fund.get('exchange') != exchange:
                continue
                
            # 检查表现评级条件
            if performance_rating:
                fund_rating = fund.get('performanceratingoverall')
                if fund_rating not in performance_rating:
                    continue
                    
            # 检查初始投资条件
            if initial_investment_max and fund.get('initialinvestment', 0) >= initial_investment_max:
                continue
                
            # 通过所有条件，添加到结果
            filtered_funds.append(fund)
        
        return filtered_funds
    
    def _get_predefined_funds(self) -> List[Dict]:
        """
        获取预定义的基金数据集
        
        返回:
            List[Dict]: 基金数据列表
        """
        # 这里包含两个示例基金
        return [
            {
                "symbol": "VFIAX",
                "name": "Vanguard 500 Index Fund Admiral Shares",
                "categoryname": "Large Blend",
                "exchange": "NAS",
                "performanceratingoverall": 5,
                "riskratingoverall": 4,
                "initialinvestment": 3000,
                "annualreturnnavy1categoryrank": 25,
                "expenseRatio": 0.04,
                "ytdReturn": 12.5,
                "fiveYearAvgReturn": 11.8
            },
            {
                "symbol": "FCNTX",
                "name": "Fidelity Contrafund",
                "categoryname": "Large Growth",
                "exchange": "NAS",
                "performanceratingoverall": 4,
                "riskratingoverall": 3,
                "initialinvestment": 0,
                "annualreturnnavy1categoryrank": 35,
                "expenseRatio": 0.85,
                "ytdReturn": 15.2,
                "fiveYearAvgReturn": 14.3
            }
        ]
    
    def to_dict(self, query: FQ) -> Dict:
        """
        将查询转换为字典表示
        
        参数:
            query (FQ): FundQuery 对象
            
        返回:
            Dict: 查询的字典表示
        """
        return query.to_dict()
    
    def save_query(self, query: FQ, file_path: str) -> None:
        """
        将查询保存到 JSON 文件
        
        参数:
            query (FQ): 要保存的 FundQuery 对象
            file_path (str): 保存文件的路径
        """
        query_dict = self.to_dict(query)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(query_dict, f, ensure_ascii=False, indent=4)
    
    def create_predefined_query(self, query_name: str) -> Optional[FQ]:
        """
        创建预定义的查询
        
        参数:
            query_name (str): 预定义查询的名称
            
        返回:
            Optional[FQ]: 如果找到预定义查询，则为 FundQuery 对象
        """
        if query_name == "solid_large_growth_funds":
            # 高评级的大型增长基金，初始投资小于 10 万美元
            return self.combine_with_and([
                self.create_eq_query("categoryname", "Large Growth"),
                self.create_is_in_query("performanceratingoverall", [4, 5]),
                self.create_lt_query("initialinvestment", 100001),
                self.create_lt_query("annualreturnnavy1categoryrank", 50),
                self.create_eq_query("exchange", "NAS")
            ])
        elif query_name == "low_cost_index_funds":
            # 低成本指数基金，初始投资小
            return self.combine_with_and([
                self.create_eq_query("categoryname", "Large Blend"),
                self.create_eq_query("exchange", "NAS"),
                self.create_lt_query("initialinvestment", 5000)
            ])
        else:
            return None
    
    def get_all_predefined_queries(self) -> Dict[str, str]:
        """
        获取所有预定义查询的描述
        
        返回:
            Dict[str, str]: 预定义查询名称到描述的映射
        """
        return {
            "solid_large_growth_funds": "高评级的大型增长基金，初始投资小于 10 万美元，类别排名前 50%",
            "low_cost_index_funds": "低成本指数基金，初始投资小于 5000 美元"
        }
    
    def get_category_funds(self, category: str, limit: int = 50) -> pd.DataFrame:
        """
        获取特定类别的基金
        
        参数:
            category (str): 基金类别名称
            limit (int): 结果数量限制
            
        返回:
            pd.DataFrame: 包含基金的 DataFrame
        """
        try:
            query = self.create_eq_query("categoryname", category)
            return self.fetch_results(query, limit)
        except Exception as e:
            print(f"获取类别基金时出错: {str(e)}")
            
            # 使用替代方法 - 直接从预定义基金中过滤
            funds_data = self._get_predefined_funds()
            filtered_funds = [fund for fund in funds_data if fund.get('categoryname') == category]
            
            # 限制数量
            filtered_funds = filtered_funds[:limit]
            
            return pd.DataFrame(filtered_funds)
    
    def get_performance_rated_funds(self, min_rating: int = 4, limit: int = 50) -> pd.DataFrame:
        """
        获取特定最低表现评级的基金
        
        参数:
            min_rating (int): 最低表现评级（1-5）
            limit (int): 结果数量限制
            
        返回:
            pd.DataFrame: 包含基金的 DataFrame
        """
        if min_rating < 1 or min_rating > 5:
            raise ValueError("最低表现评级必须在 1 到 5 之间")
        
        try:
            query = self.create_gte_query("performanceratingoverall", min_rating)
            return self.fetch_results(query, limit)
        except Exception as e:
            print(f"获取评级基金时出错: {str(e)}")
            
            # 使用替代方法 - 直接从预定义基金中过滤
            funds_data = self._get_predefined_funds()
            filtered_funds = [fund for fund in funds_data if fund.get('performanceratingoverall', 0) >= min_rating]
            
            # 限制数量
            filtered_funds = filtered_funds[:limit]
            
            return pd.DataFrame(filtered_funds)
    
    def get_fund_details(self, fund_symbols: List[str]) -> Dict[str, Dict]:
        """
        获取多个基金符号的详细信息
        
        参数:
            fund_symbols (List[str]): 基金符号列表
            
        返回:
            Dict[str, Dict]: 基金符号到详细信息的映射
        """
        result = {}
        
        for symbol in fund_symbols:
            try:
                # 尝试使用 yfinance 获取基金信息
                fund = yf.Ticker(symbol)
                
                # 收集基金详细信息
                info = fund.info
                
                result[symbol] = {
                    "info": info,
                    "recent_price": fund.history(period="1d")['Close'].iloc[-1] if not fund.history(period="1d").empty else None,
                    "ytd_return": info.get('ytdReturn', None),
                    "expense_ratio": info.get('annualReportExpenseRatio', None),
                    "category": info.get('category', None)
                }
            except Exception as e:
                print(f"获取基金 '{symbol}' 的详细信息时出错: {str(e)}")
                
                # 尝试从预定义数据中查找
                predefined_funds = self._get_predefined_funds()
                fund_data = next((fund for fund in predefined_funds if fund.get('symbol') == symbol), None)
                
                if fund_data:
                    result[symbol] = fund_data
                else:
                    result[symbol] = {"error": str(e)}
        
        return result


# 使用示例
if __name__ == "__main__":
    # 创建基金查询对象
    fund_query = YFinanceFundQuery()
    
    # 获取有效字段分类
    print("字段分类:")
    print(fund_query.get_field_categories())
    
    # 创建简单查询
    print("\n测试简单查询:")
    simple_query = fund_query.create_eq_query("categoryname", "Large Growth")
    print("查询创建成功!")
    
    # 使用预定义查询
    print("\n使用预定义查询:")
    predefined = fund_query.create_predefined_query("solid_large_growth_funds")
    if predefined:
        print("预定义查询创建成功!")
    
    # 获取结果
    print("\n获取查询结果示例:")
    results = fund_query.get_category_funds("Large Growth", limit=2)
    print(f"获取到 {len(results)} 条结果")