import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class RepurchaseData(BaseModel):
    """
    Pydantic model for stock repurchase data.
    
    Fields:
    - id: 主键ID
    - ts_code: TS股票代码
    - ann_date: 公告日期
    - end_date: 截止日期
    - proc: 进度
    - exp_date: 过期日期
    - vol: 回购数量
    - amount: 回购金额
    - high_limit: 回购最高价
    - low_limit: 回购最低价
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # TS代码，唯一标识
    ts_code: str
    # 公告日期
    ann_date: Optional[datetime.date] = None
    # 截止日期
    end_date: Optional[datetime.date] = None
    # 进度
    proc: Optional[str] = None
    # 过期日期
    exp_date: Optional[datetime.date] = None
    # 回购数量
    vol: Optional[Decimal] = None
    # 回购金额
    amount: Optional[Decimal] = None
    # 回购最高价
    high_limit: Optional[Decimal] = None
    # 回购最低价
    low_limit: Optional[Decimal] = None

    @field_validator('ann_date', 'end_date', 'exp_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('vol', 'amount', 'high_limit', 'low_limit', mode='before')
    def parse_numeric(cls, value):
        # 使用通用工具类进行数值验证
        return NumericValidators.to_decimal(value)
    
    class Config:
        from_attributes = True