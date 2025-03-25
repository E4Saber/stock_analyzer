import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator


class TradeCalData(BaseModel):
    """
    Pydantic model for trading calendar data.
    
    Fields:
    - exchange: Exchange code (SSE for Shanghai Stock Exchange, SZSE for Shenzhen Stock Exchange)
    - cal_date: Calendar date
    - is_open: Whether it's a trading day (0 for closed, 1 for trading)
    - pretrade_date: Previous trading day
    """
    # 交易所代码，复合主键之一
    exchange: str
    # 日历日期，复合主键之一
    cal_date: datetime.date
    # 是否交易 0休市 1交易
    is_open: int
    # 上一个交易日，非必须字段
    pretrade_date: Optional[datetime.date] = None

    @field_validator('cal_date', 'pretrade_date', mode='before')
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
    
    @field_validator('is_open')
    def validate_is_open(cls, value):
        if value not in [0, 1]:
            raise ValueError("is_open必须为0或1")
        return value
    
    class Config:
        from_attributes = True