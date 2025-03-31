import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class UsTycrData(BaseModel):
    """
    Pydantic model for US Treasury Yield Curve Rate data.
    
    Fields:
    - date: Date of the yield curve
    - m1: 1-month rate
    - m2: 2-month rate
    - m3: 3-month rate
    - m4: 4-month rate (data available since 2022-10-19)
    - m6: 6-month rate
    - y1: 1-year rate
    - y2: 2-year rate
    - y3: 3-year rate
    - y5: 5-year rate
    - y7: 7-year rate
    - y10: 10-year rate
    - y20: 20-year rate
    - y30: 30-year rate
    """
    # 日期
    date: datetime.date
    # 1月期
    m1: Optional[float] = None
    # 2月期
    m2: Optional[float] = None
    # 3月期
    m3: Optional[float] = None
    # 4月期（数据从20221019开始）
    m4: Optional[float] = None
    # 6月期
    m6: Optional[float] = None
    # 1年期
    y1: Optional[float] = None
    # 2年期
    y2: Optional[float] = None
    # 3年期
    y3: Optional[float] = None
    # 5年期
    y5: Optional[float] = None
    # 7年期
    y7: Optional[float] = None
    # 10年期
    y10: Optional[float] = None
    # 20年期
    y20: Optional[float] = None
    # 30年期
    y30: Optional[float] = None

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