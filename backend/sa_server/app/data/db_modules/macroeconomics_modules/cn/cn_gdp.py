from typing import Optional
from pydantic import BaseModel, field_validator
import re


class CnGdpData(BaseModel):
    """
    Pydantic model for China quarterly GDP data.
    
    Fields:
    - quarter: Quarter (e.g., '2023Q1')
    - gdp: GDP accumulated value (billion yuan)
    - gdp_yoy: Year-on-year growth rate (%)
    - pi: Primary industry accumulated value (billion yuan)
    - pi_yoy: Primary industry year-on-year growth rate (%)
    - si: Secondary industry accumulated value (billion yuan)
    - si_yoy: Secondary industry year-on-year growth rate (%)
    - ti: Tertiary industry accumulated value (billion yuan)
    - ti_yoy: Tertiary industry year-on-year growth rate (%)
    """
    # 季度，作为主键
    quarter: str
    # GDP累计值（亿元）
    gdp: Optional[float] = None
    # 当季同比增速（%）
    gdp_yoy: Optional[float] = None
    # 第一产业累计值（亿元）
    pi: Optional[float] = None
    # 第一产业同比增速（%）
    pi_yoy: Optional[float] = None
    # 第二产业累计值（亿元）
    si: Optional[float] = None
    # 第二产业同比增速（%）
    si_yoy: Optional[float] = None
    # 第三产业累计值（亿元）
    ti: Optional[float] = None
    # 第三产业同比增速（%）
    ti_yoy: Optional[float] = None

    @field_validator('quarter')
    def validate_quarter(cls, value):
        """验证季度格式，应为'YYYYQN'格式，如'2023Q1'"""
        if value is None or value == '':
            raise ValueError("季度不能为空")
        
        # 验证季度格式
        pattern = r"^\d{4}Q[1-4]$"
        if not re.match(pattern, value):
            raise ValueError(f"无效的季度格式: {value}，正确格式应为'YYYYQN'，如'2023Q1'")
        
        return value
    
    class Config:
        from_attributes = True