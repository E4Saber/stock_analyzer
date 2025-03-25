import datetime
import re
from typing import Optional, Any, Union, List


class DateValidators:
    """
    日期验证工具类，提供各种日期类型的验证和转换功能。
    """
    
    @staticmethod
    def to_date(value: Any, raise_error: bool = False) -> Optional[datetime.date]:
        """
        将输入值安全转换为date类型。
        
        支持多种日期格式：
        - 已有的date对象
        - YYYYMMDD字符串格式
        - ISO格式 (YYYY-MM-DD)
        - 中文日期格式 (YYYY年MM月DD日)
        
        参数:
            value: 要转换的值，可以是字符串、日期对象等
            raise_error: 是否在无效日期时抛出异常，默认为False
            
        返回:
            Optional[datetime.date]: 转换后的date对象，如果无法转换且raise_error为False则返回None
            
        异常:
            ValueError: 当raise_error为True且日期格式无效时抛出
        """
        # 处理None和空字符串
        if value is None or value == '':
            return None
        
        # 已经是datetime.date类型
        if isinstance(value, datetime.date):
            return value
        
        # 如果是datetime类型，转换为date
        if isinstance(value, datetime.datetime):
            return value.date()
        
        try:
            # 处理YYYYMMDD格式
            if isinstance(value, str) and value.isdigit() and len(value) == 8:
                year = int(value[:4])
                month = int(value[4:6])
                day = int(value[6:8])
                return datetime.date(year, month, day)
            
            # 处理ISO格式 (YYYY-MM-DD)
            if isinstance(value, str):
                # 尝试使用ISO格式解析
                try:
                    return datetime.date.fromisoformat(value)
                except ValueError:
                    pass
                
                # 处理中文日期格式 (YYYY年MM月DD日)
                chinese_pattern = r'(\d{4})年(\d{1,2})月(\d{1,2})日'
                match = re.match(chinese_pattern, value)
                if match:
                    year, month, day = map(int, match.groups())
                    return datetime.date(year, month, day)
                
                # 处理斜杠分隔的日期 (YYYY/MM/DD 或 MM/DD/YYYY)
                if '/' in value:
                    parts = value.split('/')
                    if len(parts) == 3:
                        # 尝试YYYY/MM/DD格式
                        if len(parts[0]) == 4:
                            year, month, day = map(int, parts)
                            return datetime.date(year, month, day)
                        # 尝试MM/DD/YYYY格式
                        elif len(parts[2]) == 4:
                            month, day, year = map(int, parts)
                            return datetime.date(year, month, day)
            
            # 其他可能的格式...
            
            if raise_error:
                raise ValueError(f"无效的日期格式: {value}")
            return None
            
        except (ValueError, TypeError) as e:
            if raise_error:
                raise ValueError(f"无效的日期格式: {value}，错误: {str(e)}")
            return None
    
    @staticmethod
    def to_datetime(value: Any, raise_error: bool = False) -> Optional[datetime.datetime]:
        """
        将输入值安全转换为datetime类型。
        
        支持多种日期时间格式。
        
        参数:
            value: 要转换的值，可以是字符串、日期时间对象等
            raise_error: 是否在无效日期时间时抛出异常，默认为False
            
        返回:
            Optional[datetime.datetime]: 转换后的datetime对象，如果无法转换且raise_error为False则返回None
            
        异常:
            ValueError: 当raise_error为True且日期时间格式无效时抛出
        """
        # 处理None和空字符串
        if value is None or value == '':
            return None
        
        # 已经是datetime类型
        if isinstance(value, datetime.datetime):
            return value
        
        # 如果是date类型，转换为datetime
        if isinstance(value, datetime.date):
            return datetime.datetime.combine(value, datetime.time())
        
        try:
            # 处理ISO格式
            if isinstance(value, str):
                try:
                    return datetime.datetime.fromisoformat(value)
                except ValueError:
                    # 尝试将日期转换为日期时间
                    date_value = DateValidators.to_date(value)
                    if date_value:
                        return datetime.datetime.combine(date_value, datetime.time())
            
            if raise_error:
                raise ValueError(f"无效的日期时间格式: {value}")
            return None
            
        except (ValueError, TypeError) as e:
            if raise_error:
                raise ValueError(f"无效的日期时间格式: {value}，错误: {str(e)}")
            return None
    
    @staticmethod
    def is_valid_date(value: Any) -> bool:
        """
        检查值是否是有效的日期。
        
        参数:
            value: 要检查的值，可以是任何类型
            
        返回:
            bool: 如果值可以被转换为有效日期则返回True，否则返回False
        """
        return DateValidators.to_date(value) is not None
    
    @staticmethod
    def format_date(
        date_value: Union[datetime.date, datetime.datetime, str],
        format_str: str = '%Y-%m-%d',
        default: str = ''
    ) -> str:
        """
        将日期值格式化为指定格式的字符串。
        
        参数:
            date_value: 要格式化的日期值
            format_str: 格式化字符串，默认为'%Y-%m-%d'
            default: 当日期值无效时返回的默认值
            
        返回:
            str: 格式化后的日期字符串，如果日期无效则返回default
        """
        date_obj = DateValidators.to_date(date_value)
        if date_obj is None:
            return default
        return date_obj.strftime(format_str)
    
    @staticmethod
    def get_date_parts(date_value: Any) -> Optional[dict]:
        """
        获取日期的年、月、日部分。
        
        参数:
            date_value: 要分解的日期值
            
        返回:
            Optional[dict]: 包含年、月、日的字典，如果日期无效则返回None
        """
        date_obj = DateValidators.to_date(date_value)
        if date_obj is None:
            return None
        return {
            'year': date_obj.year,
            'month': date_obj.month,
            'day': date_obj.day
        }