import datetime
import math
from typing import Optional
from decimal import Decimal, DecimalException
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.numeric_validators import NumericValidators
from app.utils.date_validators import DateValidators


class StockRewardData(BaseModel):
    """
    Pydantic model for company managers rewards and shareholdings data.
    
    Fields:
    - id: Auto-incremented primary key
    - ts_code: TS stock code
    - ann_date: Announcement date
    - end_date: End date
    - name: Manager name
    - title: Position title
    - reward: Compensation (in 10,000 CNY)
    - hold_vol: Number of shares held
    """
    # 自增主键，非必须字段，新建时无需提供
    id: Optional[int] = None
    # TS股票代码
    ts_code: str
    # 公告日期，非必须字段
    ann_date: Optional[datetime.date] = None
    # 截止日期，非必须字段
    end_date: Optional[datetime.date] = None
    # 姓名
    name: str
    # 职务，非必须字段
    title: Optional[str] = None
    # 报酬(万元)，非必须字段
    reward: Optional[Decimal] = None
    # 持股数(股)，非必须字段
    hold_vol: Optional[Decimal] = None

    @field_validator('ann_date', 'end_date', mode='before')
    def parse_date(cls, value):
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj
    
    @field_validator('reward', 'hold_vol', mode='before')
    def parse_numeric(cls, value):
        return NumericValidators.to_decimal(value)
    
    class Config:
        from_attributes = True