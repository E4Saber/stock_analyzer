import math
from decimal import Decimal, DecimalException
from typing import Optional, Union, Any

class NumericValidators:
    """
    数值验证工具类，提供各种数值类型的验证和转换功能。
    """
    
    @staticmethod
    def to_decimal(value: Any) -> Optional[Decimal]:
        """
        将输入值安全转换为Decimal类型。
        
        处理None、空字符串、NaN、Infinity等特殊情况。
        无效的数值将返回None，而不是抛出异常。
        
        参数:
            value: 要转换的值，可以是任何类型
            
        返回:
            Optional[Decimal]: 转换后的Decimal值，如果无法转换则返回None
        """
        # 处理None和空字符串
        if value is None or value == '':
            return None
        
        # 处理浮点数中的NaN和Infinity
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return None
        
        # 处理Decimal中的NaN和Infinity
        if isinstance(value, Decimal) and (value.is_nan() or value.is_infinite()):
            return None
        
        # 处理字符串表示的特殊值
        if isinstance(value, str) and value.lower().strip() in ['nan', 'infinity', '-infinity', 'inf', '-inf', '']:
            return None
        
        # 正常数值转换
        try:
            decimal_value = Decimal(str(value))
            # 再次检查转换后的值是否为有限值
            if decimal_value.is_nan() or decimal_value.is_infinite():
                return None
            return decimal_value
        except (ValueError, TypeError, DecimalException):
            # 无法转换为数值，返回None
            return None
    
    @staticmethod
    def to_float(value: Any) -> Optional[float]:
        """
        将输入值安全转换为float类型。
        
        处理None、空字符串、NaN、Infinity等特殊情况。
        无效的数值将返回None，而不是抛出异常。
        
        参数:
            value: 要转换的值，可以是任何类型
            
        返回:
            Optional[float]: 转换后的float值，如果无法转换则返回None
        """
        decimal_value = NumericValidators.to_decimal(value)
        if decimal_value is None:
            return None
        
        try:
            return float(decimal_value)
        except (ValueError, TypeError, OverflowError):
            return None
    
    @staticmethod
    def to_int(value: Any) -> Optional[int]:
        """
        将输入值安全转换为int类型。
        
        处理None、空字符串、NaN、Infinity等特殊情况。
        无效的数值将返回None，而不是抛出异常。
        
        参数:
            value: 要转换的值，可以是任何类型
            
        返回:
            Optional[int]: 转换后的int值，如果无法转换则返回None
        """
        decimal_value = NumericValidators.to_decimal(value)
        if decimal_value is None:
            return None
        
        try:
            return int(decimal_value)
        except (ValueError, TypeError, OverflowError):
            return None
    
    @staticmethod
    def is_valid_number(value: Any) -> bool:
        """
        检查值是否是有效的数值。
        
        参数:
            value: 要检查的值，可以是任何类型
            
        返回:
            bool: 如果值是有效的有限数值则返回True，否则返回False
        """
        return NumericValidators.to_decimal(value) is not None