import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class HkDailyData(BaseModel):
    """
    Pydantic model for Hong Kong stock daily market data.
    
    Fields:
    - id: 主键ID
    - ts_code: 股票代码
    - trade_date: 交易日期
    - open: 开盘价
    - high: 最高价
    - low: 最低价
    - close: 收盘价
    - pre_close: 昨收价
    - change: 涨跌额
    - pct_chg: 涨跌幅(%)
    - vol: 成交量(股)
    - amount: 成交额(元)
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # 股票代码
    ts_code: str
    # 交易日期
    trade_date: datetime.date
    # 开盘价
    open: Optional[float] = None
    # 最高价
    high: Optional[float] = None
    # 最低价
    low: Optional[float] = None
    # 收盘价
    close: Optional[float] = None
    # 昨收价
    pre_close: Optional[float] = None
    # 涨跌额
    change: Optional[float] = None
    # 涨跌幅(%)
    pct_chg: Optional[float] = None
    # 成交量(股)
    vol: Optional[float] = None
    # 成交额(元)
    amount: Optional[float] = None

    @field_validator('trade_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol', 'amount', mode='before')
    def parse_float(cls, value):
        # 将字符串或整数转换为浮点数
        float_obj = NumericValidators.to_float(value)
        if float_obj is None and value is not None and value != '':
            raise ValueError(f"无效的浮点数格式: {value}")
        return float_obj
    
    class Config:
        from_attributes = True