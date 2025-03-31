from typing import Optional
from pydantic import BaseModel, field_validator
import re


class CnCpiData(BaseModel):
    """
    Pydantic model for China monthly CPI data.
    
    Fields:
    - month: Month (e.g., '202301')
    - nt_val: National monthly value
    - nt_yoy: National year-on-year growth rate (%)
    - nt_mom: National month-on-month growth rate (%)
    - nt_accu: National accumulated value
    - town_val: Urban monthly value
    - town_yoy: Urban year-on-year growth rate (%)
    - town_mom: Urban month-on-month growth rate (%)
    - town_accu: Urban accumulated value
    - cnt_val: Rural monthly value
    - cnt_yoy: Rural year-on-year growth rate (%)
    - cnt_mom: Rural month-on-month growth rate (%)
    - cnt_accu: Rural accumulated value
    """
    # 月份，作为主键
    month: str
    # 全国当月值
    nt_val: Optional[float] = None
    # 全国同比（%）
    nt_yoy: Optional[float] = None
    # 全国环比（%）
    nt_mom: Optional[float] = None
    # 全国累计值
    nt_accu: Optional[float] = None
    # 城市当月值
    town_val: Optional[float] = None
    # 城市同比（%）
    town_yoy: Optional[float] = None
    # 城市环比（%）
    town_mom: Optional[float] = None
    # 城市累计值
    town_accu: Optional[float] = None
    # 农村当月值
    cnt_val: Optional[float] = None
    # 农村同比（%）
    cnt_yoy: Optional[float] = None
    # 农村环比（%）
    cnt_mom: Optional[float] = None
    # 农村累计值
    cnt_accu: Optional[float] = None

    @field_validator('month')
    def validate_month(cls, value):
        """验证月份格式，应为'YYYYMM'格式，如'202301'"""
        if value is None or value == '':
            raise ValueError("月份不能为空")
        
        # 验证月份格式
        pattern = r"^\d{6}$"
        if not re.match(pattern, value):
            raise ValueError(f"无效的月份格式: {value}，正确格式应为'YYYYMM'，如'202301'")
        
        # 验证月份值
        year = int(value[:4])
        month = int(value[4:6])
        
        if year < 1900 or year > 2100:
            raise ValueError(f"无效的年份: {year}")
        
        if month < 1 or month > 12:
            raise ValueError(f"无效的月份: {month}")
        
        return value
    
    class Config:
        from_attributes = True