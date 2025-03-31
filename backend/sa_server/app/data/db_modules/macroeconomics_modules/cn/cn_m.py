from typing import Optional
from pydantic import BaseModel, field_validator
import re


class CnMData(BaseModel):
    """
    Pydantic model for China monthly monetary supply data.
    
    Fields:
    - month: Month (e.g., '202301')
    - m0: M0 money supply in 100 million yuan
    - m0_yoy: M0 year-on-year growth rate (%)
    - m0_mom: M0 month-on-month growth rate (%)
    - m1: M1 money supply in 100 million yuan
    - m1_yoy: M1 year-on-year growth rate (%)
    - m1_mom: M1 month-on-month growth rate (%)
    - m2: M2 money supply in 100 million yuan
    - m2_yoy: M2 year-on-year growth rate (%)
    - m2_mom: M2 month-on-month growth rate (%)
    """
    # 月份，作为主键
    month: str
    # M0货币供应量（亿元）
    m0: Optional[float] = None
    # M0同比增长率（%）
    m0_yoy: Optional[float] = None
    # M0环比增长率（%）
    m0_mom: Optional[float] = None
    # M1货币供应量（亿元）
    m1: Optional[float] = None
    # M1同比增长率（%）
    m1_yoy: Optional[float] = None
    # M1环比增长率（%）
    m1_mom: Optional[float] = None
    # M2货币供应量（亿元）
    m2: Optional[float] = None
    # M2同比增长率（%）
    m2_yoy: Optional[float] = None
    # M2环比增长率（%）
    m2_mom: Optional[float] = None

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