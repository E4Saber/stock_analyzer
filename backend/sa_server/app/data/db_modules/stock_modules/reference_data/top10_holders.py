import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class Top10HoldersData(BaseModel):
    """
    Pydantic model for top 10 shareholders data.
    
    Fields:
    - id: 主键ID
    - ts_code: TS股票代码
    - ann_date: 公告日期
    - end_date: 报告期
    - holder_name: 股东名称
    - hold_amount: 持有数量（股）
    - hold_ratio: 占总股本比例(%)
    - hold_float_ratio: 占流通股本比例(%)
    - hold_change: 持股变动
    - holder_type: 股东类型
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # TS代码，唯一标识
    ts_code: str
    # 公告日期
    ann_date: Optional[datetime.date] = None
    # 报告期
    end_date: Optional[datetime.date] = None
    # 股东名称
    holder_name: str
    # 持有数量（股）
    hold_amount: Optional[Decimal] = None
    # 占总股本比例(%)
    hold_ratio: Optional[Decimal] = None
    # 占流通股本比例(%)
    hold_float_ratio: Optional[Decimal] = None
    # 持股变动
    hold_change: Optional[Decimal] = None
    # 股东类型
    holder_type: Optional[str] = None

    @field_validator('ann_date', 'end_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('hold_amount', 'hold_ratio', 'hold_float_ratio', 'hold_change', mode='before')
    def parse_numeric(cls, value):
        # 使用通用工具类进行数值验证
        return NumericValidators.to_decimal(value)
    
    class Config:
        from_attributes = True