# app/utils/json_utils.py
import math
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel

def clean_nan_values(data: Any) -> Any:
    """
    递归清理数据中的NaN、Infinity和-Infinity值，替换为None
    
    Args:
        data: 任意类型的数据，可以是基本类型、字典、列表或Pydantic模型
        
    Returns:
        清理后的数据，所有NaN和Infinity值都被替换为None
    """
    # 处理None
    if data is None:
        return None
        
    # 处理浮点数
    if isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            return None
        return data
        
    # 处理整数和其他基本类型
    if isinstance(data, (int, str, bool)):
        return data
        
    # 处理列表
    if isinstance(data, list):
        return [clean_nan_values(item) for item in data]
        
    # 处理字典
    if isinstance(data, dict):
        return {key: clean_nan_values(value) for key, value in data.items()}
        
    # 处理Pydantic模型
    if isinstance(data, BaseModel):
        # 获取模型的字典表示
        model_dict = data.dict()
        # 清理字典中的NaN值
        cleaned_dict = clean_nan_values(model_dict)
        # 使用清理后的字典创建新的模型实例
        return data.__class__(**cleaned_dict)
        
    # 其他类型，尝试转换为字典后处理
    try:
        as_dict = dict(data)
        return clean_nan_values(as_dict)
    except (TypeError, ValueError):
        # 如果无法转换，则原样返回
        return data

def clean_model_list(models: List[BaseModel]) -> List[BaseModel]:
    """
    清理Pydantic模型列表中的所有NaN值
    
    Args:
        models: Pydantic模型列表
        
    Returns:
        清理后的模型列表
    """
    return [clean_nan_values(model) for model in models]

def clean_dict_list(dicts: List[Dict]) -> List[Dict]:
    """
    清理字典列表中的所有NaN值
    
    Args:
        dicts: 字典列表
        
    Returns:
        清理后的字典列表
    """
    return [clean_nan_values(d) for d in dicts]

# 用于替换CRUD响应的装饰器
def clean_nan_response(func):
    """
    装饰器：自动清理CRUD方法返回的数据中的NaN值
    
    用法：
    @clean_nan_response
    async def get_all_cpi(self) -> List[CnCpiData]:
        ...
    """
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        return clean_nan_values(result)
    return wrapper