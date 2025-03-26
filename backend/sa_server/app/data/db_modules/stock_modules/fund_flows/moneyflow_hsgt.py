import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator


class MoneyflowHsgtData(BaseModel):
    """
    Pydantic model for Hong Kong-Mainland stock connect moneyflow data.
    
    Fields:
    - trade_date: Trading date
    - ggt_ss: Shanghai-Hong Kong Stock Connect (HK -> Shanghai)
    - ggt_sz: Shenzhen-Hong Kong Stock Connect (HK -> Shenzhen)
    - hgt: Shanghai-Hong Kong Stock Connect (Shanghai -> HK, million yuan)
    - sgt: Shenzhen-Hong Kong Stock Connect (Shenzhen -> HK, million yuan)
    - north_money: Northbound money flow (million yuan)
    - south_money: Southbound money flow (million yuan)
    """
    # 交易日期
    trade_date: datetime.date
    # 港股通（上海）
    ggt_ss: Optional[float] = None
    # 港股通（深圳）
    ggt_sz: Optional[float] = None
    # 沪股通（百万元）
    hgt: Optional[float] = None
    # 深股通（百万元）
    sgt: Optional[float] = None
    # 北向资金（百万元）
    north_money: Optional[float] = None
    # 南向资金（百万元）
    south_money: Optional[float] = None

    @field_validator('trade_date', mode='before')
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