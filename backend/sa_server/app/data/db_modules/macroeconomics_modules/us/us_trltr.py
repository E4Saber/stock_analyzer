import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class UsTrltrData(BaseModel):
    """
    Pydantic model for US Treasury Real Long-term Rates data.
    
    Fields:
    - date: Date of the real long-term treasury rate
    - ltr_avg: LT Real Average (10> Yrs) rate
    """
    # 日期
    date: datetime.date
    # 实际平均利率LT Real Average (10> Yrs)
    ltr_avg: Optional[float] = None

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