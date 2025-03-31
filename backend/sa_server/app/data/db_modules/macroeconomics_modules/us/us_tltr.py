import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class UsTltrData(BaseModel):
    """
    Pydantic model for US Treasury Long-term Rates data.
    
    Fields:
    - date: Date of the long-term treasury rates
    - ltc: LT COMPOSITE (>10 Yrs) rate
    - cmt: TREASURY 20-Yr CMT rate
    - e_factor: EXTRAPOLATION FACTOR
    """
    # 日期
    date: datetime.date
    # 收益率 LT COMPOSITE (>10 Yrs)
    ltc: Optional[float] = None
    # 20年期CMT利率(TREASURY 20-Yr CMT)
    cmt: Optional[float] = None
    # 外推因子EXTRAPOLATION FACTOR
    e_factor: Optional[float] = None

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