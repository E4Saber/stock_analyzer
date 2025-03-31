import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class ShiborLprData(BaseModel):
    """
    Pydantic model for SHIBOR LPR (Loan Prime Rate) data.
    
    Fields:
    - date: Date of the LPR
    - y1: 1-year loan rate
    - y5: 5-year loan rate
    """
    # 日期
    date: datetime.date
    # 1年贷款利率
    y1: Optional[float] = None
    # 5年贷款利率
    y5: Optional[float] = None

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