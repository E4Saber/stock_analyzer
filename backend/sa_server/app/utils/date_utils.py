from datetime import datetime, timedelta


class DateUtils:
    """
    日期工具类，提供常用的日期操作方法
    """
    
    @staticmethod
    def get_date_str(days_offset=0, date_format='%Y%m%d'):
        """
        获取指定偏移天数的日期字符串
        
        Args:
            days_offset (int): 相对于今天的天数偏移，负数表示过去，正数表示未来
            date_format (str): 日期格式，默认为'%Y%m%d'
            
        Returns:
            str: 格式化的日期字符串
        """
        target_date = datetime.now() + timedelta(days=days_offset)
        return target_date.strftime(date_format)
    
    @staticmethod
    def get_today_str(date_format='%Y%m%d'):
        """
        获取今天的日期字符串
        
        Args:
            date_format (str): 日期格式，默认为'%Y%m%d'
            
        Returns:
            str: 今天的日期字符串
        """
        return DateUtils.get_date_str(0, date_format)
    
    @staticmethod
    def get_yesterday_str(date_format='%Y%m%d'):
        """
        获取昨天的日期字符串
        
        Args:
            date_format (str): 日期格式，默认为'%Y%m%d'
            
        Returns:
            str: 昨天的日期字符串
        """
        return DateUtils.get_date_str(-1, date_format)
    
    @staticmethod
    def get_tomorrow_str(date_format='%Y%m%d'):
        """
        获取明天的日期字符串
        
        Args:
            date_format (str): 日期格式，默认为'%Y%m%d'
            
        Returns:
            str: 明天的日期字符串
        """
        return DateUtils.get_date_str(1, date_format)
    
    @staticmethod
    def get_date_range(start_offset, end_offset, date_format='%Y%m%d'):
        """
        获取指定日期范围的字符串列表
        
        Args:
            start_offset (int): 开始日期相对于今天的偏移天数
            end_offset (int): 结束日期相对于今天的偏移天数
            date_format (str): 日期格式，默认为'%Y%m%d'
            
        Returns:
            list: 日期字符串列表
        """
        result = []
        for offset in range(start_offset, end_offset + 1):
            result.append(DateUtils.get_date_str(offset, date_format))
        return result
    
    @staticmethod
    def str_to_date(date_str, date_format='%Y%m%d'):
        """
        将日期字符串转换为datetime对象
        
        Args:
            date_str (str): 日期字符串
            date_format (str): 日期格式，默认为'%Y%m%d'
            
        Returns:
            datetime: 转换后的datetime对象
        """
        return datetime.strptime(date_str, date_format)
    
    @staticmethod
    def get_days_between(start_date_str, end_date_str, date_format='%Y%m%d'):
        """
        计算两个日期字符串之间的天数差
        
        Args:
            start_date_str (str): 开始日期字符串
            end_date_str (str): 结束日期字符串
            date_format (str): 日期格式，默认为'%Y%m%d'
            
        Returns:
            int: 天数差
        """
        start_date = DateUtils.str_to_date(start_date_str, date_format)
        end_date = DateUtils.str_to_date(end_date_str, date_format)
        delta = end_date - start_date
        return delta.days
    
    @staticmethod
    def add_days(date_str, days, date_format='%Y%m%d'):
        """
        给日期字符串增加指定的天数
        
        Args:
            date_str (str): 日期字符串
            days (int): 要增加的天数，可以为负数
            date_format (str): 日期格式，默认为'%Y%m%d'
            
        Returns:
            str: 增加天数后的日期字符串
        """
        date_obj = DateUtils.str_to_date(date_str, date_format)
        new_date = date_obj + timedelta(days=days)
        return new_date.strftime(date_format)
    
    @staticmethod
    def is_weekend(date_str, date_format='%Y%m%d'):
        """
        判断日期是否为周末（周六或周日）
        
        Args:
            date_str (str): 日期字符串
            date_format (str): 日期格式，默认为'%Y%m%d'
            
        Returns:
            bool: 如果是周末则返回True，否则返回False
        """
        date_obj = DateUtils.str_to_date(date_str, date_format)
        # 周六是5，周日是6
        return date_obj.weekday() >= 5
    
    @staticmethod
    def get_month_first_day(date_str=None, date_format='%Y%m%d'):
        """
        获取指定日期所在月份的第一天
        
        Args:
            date_str (str, optional): 日期字符串，默认为今天
            date_format (str): 日期格式，默认为'%Y%m%d'
            
        Returns:
            str: 月份第一天的日期字符串
        """
        if date_str is None:
            date_obj = datetime.now()
        else:
            date_obj = DateUtils.str_to_date(date_str, date_format)
        
        first_day = date_obj.replace(day=1)
        return first_day.strftime(date_format)
    
    @staticmethod
    def get_month_last_day(date_str=None, date_format='%Y%m%d'):
        """
        获取指定日期所在月份的最后一天
        
        Args:
            date_str (str, optional): 日期字符串，默认为今天
            date_format (str): 日期格式，默认为'%Y%m%d'
            
        Returns:
            str: 月份最后一天的日期字符串
        """
        if date_str is None:
            date_obj = datetime.now()
        else:
            date_obj = DateUtils.str_to_date(date_str, date_format)
        
        # 获取下个月的第一天，然后减去一天
        if date_obj.month == 12:
            next_month = date_obj.replace(year=date_obj.year + 1, month=1, day=1)
        else:
            next_month = date_obj.replace(month=date_obj.month + 1, day=1)
        
        last_day = next_month - timedelta(days=1)
        return last_day.strftime(date_format)