import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class ShiborQuoteData(BaseModel):
    """
    Pydantic model for SHIBOR quote data.
    
    Fields:
    - date: Date of the quote
    - bank: Bank name providing the quote
    - on_b: Overnight Bid rate
    - on_a: Overnight Ask rate
    - w1_b: 1-week Bid rate
    - w1_a: 1-week Ask rate
    - w2_b: 2-week Bid rate
    - w2_a: 2-week Ask rate
    - m1_b: 1-month Bid rate
    - m1_a: 1-month Ask rate
    - m3_b: 3-month Bid rate
    - m3_a: 3-month Ask rate
    - m6_b: 6-month Bid rate
    - m6_a: 6-month Ask rate
    - m9_b: 9-month Bid rate
    - m9_a: 9-month Ask rate
    - y1_b: 1-year Bid rate
    - y1_a: 1-year Ask rate
    """
    # 日期
    date: datetime.date
    # 报价银行
    bank: str
    # 隔夜_Bid
    on_b: Optional[float] = None
    # 隔夜_Ask
    on_a: Optional[float] = None
    # 1周_Bid
    w1_b: Optional[float] = None
    # 1周_Ask
    w1_a: Optional[float] = None
    # 2周_Bid
    w2_b: Optional[float] = None
    # 2周_Ask
    w2_a: Optional[float] = None
    # 1月_Bid
    m1_b: Optional[float] = None
    # 1月_Ask
    m1_a: Optional[float] = None
    # 3月_Bid
    m3_b: Optional[float] = None
    # 3月_Ask
    m3_a: Optional[float] = None
    # 6月_Bid
    m6_b: Optional[float] = None
    # 6月_Ask
    m6_a: Optional[float] = None
    # 9月_Bid
    m9_b: Optional[float] = None
    # 9月_Ask
    m9_a: Optional[float] = None
    # 1年_Bid
    y1_b: Optional[float] = None
    # 1年_Ask
    y1_a: Optional[float] = None

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