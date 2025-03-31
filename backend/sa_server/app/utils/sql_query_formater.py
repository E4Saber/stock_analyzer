import datetime
from typing import List, Any


def format_sql_query(query: str, params: List[Any]) -> str:
    """
    格式化SQL查询语句，将占位符替换为实际参数值
    
    Args:
        query: SQL查询语句
        params: 参数列表
    
    Returns:
        格式化后的SQL语句字符串
    """
    try:
        # 使用正则替换占位符
        import re
        
        def replace_param(match):
            param_idx = int(match.group(1)) - 1
            if param_idx < len(params):
                # 特殊处理不同类型的参数
                param = params[param_idx]
                if param is None:
                    return 'NULL'
                elif isinstance(param, str):
                    return f"'{param}'"
                elif isinstance(param, (datetime.date, datetime.datetime)):
                    return f"'{param.isoformat()}'"
                else:
                    return str(param)
            return match.group(0)
        
        formatted_query = re.sub(r'\$(\d+)', replace_param, query)
        return formatted_query
    except Exception as e:
        # 如果格式化失败，返回原始查询
        return query
