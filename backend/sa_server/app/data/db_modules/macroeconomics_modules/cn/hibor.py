import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class HiborData(BaseModel):
    """
    Pydantic model for HIBOR (Hong Kong Interbank Offered Rate) data.
    
    Fields:
    - date: Date of the HIBOR rate
    - on_rate: Overnight rate
    - w1_rate: 1-week rate
    - w2_rate: 2-week rate
    - m1_rate: 1-month rate
    - m2_rate: 2-month rate
    - m3_rate: 3-month rate
    - m6_rate: 6-month rate
    - m12_rate: 12-month rate
    """
    # 日期
    date: datetime.date
    # 隔夜利率
    on_rate: Optional[float] = None
    # 1周利率
    w1_rate: Optional[float] = None
    # 2周利率
    w2_rate: Optional[float] = None
    # 1个月利率
    m1_rate: Optional[float] = None
    # 2个月利率
    m2_rate: Optional[float] = None
    # 3个月利率
    m3_rate: Optional[float] = None
    # 6个月利率
    m6_rate: Optional[float] = None
    # 12个月利率
    m12_rate: Optional[float] = None

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