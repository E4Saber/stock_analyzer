import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class NewShareData(BaseModel):
    """
    Pydantic model for IPO new shares data.
    
    Fields:
    - ts_code: TS stock code
    - sub_code: Subscription code
    - name: Stock name
    - ipo_date: IPO date
    - issue_date: Listing date
    - amount: Total issuance (10,000 shares)
    - market_amount: Public issuance (10,000 shares)
    - price: Issue price (CNY)
    - pe: Price-earnings ratio
    - limit_amount: Individual subscription limit (10,000 shares)
    - funds: Raised funds (100 million CNY)
    - ballot: Winning rate
    """
    # TS股票代码
    ts_code: str
    # 申购代码，非必须字段
    sub_code: Optional[str] = None
    # 股票名称
    name: str
    # 上网发行日期，非必须字段
    ipo_date: Optional[datetime.date] = None
    # 上市日期，非必须字段
    issue_date: Optional[datetime.date] = None
    # 发行总量（万股），非必须字段
    amount: Optional[Decimal] = None
    # 上网发行总量（万股），非必须字段
    market_amount: Optional[Decimal] = None
    # 发行价格（元），非必须字段
    price: Optional[Decimal] = None
    # 市盈率，非必须字段
    pe: Optional[Decimal] = None
    # 个人申购上限（万股），非必须字段
    limit_amount: Optional[Decimal] = None
    # 募集资金（亿元），非必须字段
    funds: Optional[Decimal] = None
    # 中签率，非必须字段
    ballot: Optional[Decimal] = None

    @field_validator('ipo_date', 'issue_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj
    
    @field_validator('amount', 'market_amount', 'price', 'pe', 'limit_amount', 'funds', 'ballot', mode='before')
    def parse_numeric(cls, value):
        # 使用通用工具类进行数值验证
        return NumericValidators.to_decimal(value)
    
    class Config:
        from_attributes = True