import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class UsTbrData(BaseModel):
    """
    Pydantic model for US Treasury Bill Rates data.
    
    Fields:
    - date: Date of the treasury bill rates
    - w4_bd: 4-week bank discount rate
    - w4_ce: 4-week coupon equivalent rate
    - w8_bd: 8-week bank discount rate
    - w8_ce: 8-week coupon equivalent rate
    - w13_bd: 13-week bank discount rate
    - w13_ce: 13-week coupon equivalent rate
    - w17_bd: 17-week bank discount rate (data available since 2022-10-19)
    - w17_ce: 17-week coupon equivalent rate (data available since 2022-10-19)
    - w26_bd: 26-week bank discount rate
    - w26_ce: 26-week coupon equivalent rate
    - w52_bd: 52-week bank discount rate
    - w52_ce: 52-week coupon equivalent rate
    """
    # 日期
    date: datetime.date
    # 4周银行折现收益率
    w4_bd: Optional[float] = None
    # 4周票面利率
    w4_ce: Optional[float] = None
    # 8周银行折现收益率
    w8_bd: Optional[float] = None
    # 8周票面利率
    w8_ce: Optional[float] = None
    # 13周银行折现收益率
    w13_bd: Optional[float] = None
    # 13周票面利率
    w13_ce: Optional[float] = None
    # 17周银行折现收益率（数据从20221019开始）
    w17_bd: Optional[float] = None
    # 17周票面利率（数据从20221019开始）
    w17_ce: Optional[float] = None
    # 26周银行折现收益率
    w26_bd: Optional[float] = None
    # 26周票面利率
    w26_ce: Optional[float] = None
    # 52周银行折现收益率
    w52_bd: Optional[float] = None
    # 52周票面利率
    w52_ce: Optional[float] = None

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