import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class BlockTradeData(BaseModel):
    """
    Pydantic model for block trade data.
    
    Fields:
    - id: 主键ID
    - ts_code: TS股票代码
    - trade_date: 交易日历
    - price: 成交价
    - vol: 成交量（万股）
    - amount: 成交金额
    - buyer: 买方营业部
    - seller: 卖方营业部
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # TS代码，唯一标识
    ts_code: str
    # 交易日历
    trade_date: datetime.date
    # 成交价
    price: Optional[Decimal] = None
    # 成交量（万股）
    vol: Optional[Decimal] = None
    # 成交金额
    amount: Optional[Decimal] = None
    # 买方营业部
    buyer: Optional[str] = None
    # 卖方营业部
    seller: Optional[str] = None

    @field_validator('trade_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('price', 'vol', 'amount', mode='before')
    def parse_numeric(cls, value):
        # 使用通用工具类进行数值验证
        return NumericValidators.to_decimal(value)
    
    class Config:
        from_attributes = True