import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class GzIndexData(BaseModel):
    """
    Pydantic model for Guizhou Small Loan Market Interest Rate Index data.
    
    Fields:
    - date: Date of the index
    - d10_rate: 10-day average small loan market interest rate (%)
    - m1_rate: 1-month average small loan market interest rate
    - m3_rate: 3-month average small loan market interest rate
    - m6_rate: 6-month average small loan market interest rate
    - m12_rate: 12-month average small loan market interest rate
    - long_rate: Long-term average small loan market interest rate
    """
    # 日期
    date: datetime.date
    # 小额贷市场平均利率（十天）（单位：%）
    d10_rate: Optional[float] = None
    # 小额贷市场平均利率（一月期）
    m1_rate: Optional[float] = None
    # 小额贷市场平均利率（三月期）
    m3_rate: Optional[float] = None
    # 小额贷市场平均利率（六月期）
    m6_rate: Optional[float] = None
    # 小额贷市场平均利率（一年期）
    m12_rate: Optional[float] = None
    # 小额贷市场平均利率（长期）
    long_rate: Optional[float] = None

    @field_validator('date', mode='before')
    def parse_date(cls, value):
        if value is None or value == '':
            return None
        if isinstance(value, datetime.date):
            return value
        try:
            # 假设日期格式为 'YYYYMMDD'
            if isinstance(value, str) and value.isdigit() and len(value) == 8:
                year = int(value[:4])
                month = int(value[4:6])
                day = int(value[6:8])
                return datetime.date(year, month, day)
            # 其他常见格式
            return datetime.date.fromisoformat(value)
        except (ValueError, TypeError):
            raise ValueError(f"无效的日期格式: {value}")

    class Config:
        from_attributes = True