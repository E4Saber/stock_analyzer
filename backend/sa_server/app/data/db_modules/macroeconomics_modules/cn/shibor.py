import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator


class ShiborData(BaseModel):
    """
    Pydantic model for Shanghai Interbank Offered Rate (Shibor) data.
    
    Fields:
    - date: Date of the interest rate
    - on_rate: Overnight interest rate
    - w1_rate: 1-week interest rate
    - w2_rate: 2-week interest rate
    - m1_rate: 1-month interest rate
    - m3_rate: 3-month interest rate
    - m6_rate: 6-month interest rate
    - m9_rate: 9-month interest rate
    - y1_rate: 1-year interest rate
    """
    # 日期，作为主键
    date: datetime.date
    # 隔夜利率
    on_rate: Optional[float] = None
    # 1周利率
    w1_rate: Optional[float] = None
    # 2周利率
    w2_rate: Optional[float] = None
    # 1个月利率
    m1_rate: Optional[float] = None
    # 3个月利率
    m3_rate: Optional[float] = None
    # 6个月利率
    m6_rate: Optional[float] = None
    # 9个月利率
    m9_rate: Optional[float] = None
    # 1年利率
    y1_rate: Optional[float] = None

    @field_validator('date', mode='before')
    def parse_date(cls, value):
        if value is None or value == '':
            raise ValueError("日期不能为空")
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