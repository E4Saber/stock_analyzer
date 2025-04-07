import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class HkMinsData(BaseModel):
    """
    Pydantic model for Hong Kong stock minute-level market data.
    
    Fields:
    - id: 主键ID
    - ts_code: 股票代码
    - trade_time: 交易时间
    - freq: 分钟频度（1min/5min/15min/30min/60min）
    - open: 开盘价
    - high: 最高价
    - low: 最低价
    - close: 收盘价
    - vol: 成交量
    - amount: 成交金额
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # 股票代码
    ts_code: str
    # 交易时间
    trade_time: datetime.datetime
    # 分钟频度
    freq: str
    # 开盘价
    open: Optional[float] = None
    # 最高价
    high: Optional[float] = None
    # 最低价
    low: Optional[float] = None
    # 收盘价
    close: Optional[float] = None
    # 成交量
    vol: Optional[int] = None
    # 成交金额
    amount: Optional[float] = None

    @field_validator('trade_time', mode='before')
    def parse_datetime(cls, value):
        # 使用通用工具类进行日期时间验证
        datetime_obj = DateValidators.to_datetime(value)
        if datetime_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期时间格式: {value}")
        return datetime_obj

    @field_validator('open', 'high', 'low', 'close', 'amount', mode='before')
    def parse_float(cls, value):
        # 将字符串或整数转换为浮点数
        float_obj = NumericValidators.to_float(value)
        if float_obj is None and value is not None and value != '':
            raise ValueError(f"无效的浮点数格式: {value}")
        return float_obj
    
    @field_validator('vol', mode='before')
    def parse_int(cls, value):
        # 将字符串或浮点数转换为整数
        int_obj = NumericValidators.to_int(value)
        if int_obj is None and value is not None and value != '':
            raise ValueError(f"无效的整数格式: {value}")
        return int_obj
    
    @field_validator('freq')
    def validate_freq(cls, v):
        valid_freqs = ['1min', '5min', '15min', '30min', '60min']
        if v not in valid_freqs:
            raise ValueError(f"无效的分钟频度: {v}，必须是 {', '.join(valid_freqs)} 之一")
        return v
    
    class Config:
        from_attributes = True