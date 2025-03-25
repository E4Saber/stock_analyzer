import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator


class StkPremarketData(BaseModel):
    """
    Pydantic model for stock premarket data.
    
    Fields:
    - trade_date: Trading date
    - ts_code: TS stock code
    - total_share: Total share (10,000 shares)
    - float_share: Floating share (10,000 shares)
    - pre_close: Previous closing price
    - up_limit: Today's upper limit price
    - down_limit: Today's lower limit price
    """
    # 交易日期，复合主键之一
    trade_date: datetime.date
    # TS股票代码，复合主键之一
    ts_code: str
    # 总股本（万股），非必须字段
    total_share: Optional[float] = None
    # 流通股本（万股），非必须字段
    float_share: Optional[float] = None
    # 昨日收盘价，非必须字段
    pre_close: Optional[float] = None
    # 今日涨停价，非必须字段
    up_limit: Optional[float] = None
    # 今日跌停价，非必须字段
    down_limit: Optional[float] = None

    @field_validator('trade_date', mode='before')
    def parse_date(cls, value):
        if value is None or value == '':
            raise ValueError("交易日期不能为空")
        
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