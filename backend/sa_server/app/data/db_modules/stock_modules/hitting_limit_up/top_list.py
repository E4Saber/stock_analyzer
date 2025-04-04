import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class TopListData(BaseModel):
    """
    Pydantic model for top list data.
    
    Fields:
    - id: 主键ID
    - trade_date: 交易日期
    - ts_code: TS代码
    - name: 名称
    - close: 收盘价
    - pct_change: 涨跌幅
    - turnover_rate: 换手率
    - amount: 总成交额
    - l_sell: 龙虎榜卖出额
    - l_buy: 龙虎榜买入额
    - l_amount: 龙虎榜成交额
    - net_amount: 龙虎榜净买入额
    - net_rate: 龙虎榜净买额占比
    - amount_rate: 龙虎榜成交额占比
    - float_values: 当日流通市值
    - reason: 上榜理由
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # 交易日期
    trade_date: Optional[datetime.date] = None
    # TS代码
    ts_code: str
    # 名称
    name: str
    # 收盘价
    close: Optional[Decimal] = None
    # 涨跌幅
    pct_change: Optional[Decimal] = None
    # 换手率
    turnover_rate: Optional[Decimal] = None
    # 总成交额
    amount: Optional[Decimal] = None
    # 龙虎榜卖出额
    l_sell: Optional[Decimal] = None
    # 龙虎榜买入额
    l_buy: Optional[Decimal] = None
    # 龙虎榜成交额
    l_amount: Optional[Decimal] = None
    # 龙虎榜净买入额
    net_amount: Optional[Decimal] = None
    # 龙虎榜净买额占比
    net_rate: Optional[Decimal] = None
    # 龙虎榜成交额占比
    amount_rate: Optional[Decimal] = None
    # 当日流通市值
    float_values: Optional[Decimal] = None
    # 上榜理由
    reason: Optional[str] = None

    @field_validator('trade_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('close', 'pct_change', 'turnover_rate', 'amount', 
                    'l_sell', 'l_buy', 'l_amount', 'net_amount', 
                    'net_rate', 'amount_rate', 'float_values', mode='before')
    def parse_numeric(cls, value):
        # 将字符串或浮点数转换为Decimal
        decimal_obj = NumericValidators.to_decimal(value)
        if decimal_obj is None and value is not None and value != '':
            raise ValueError(f"无效的数字格式: {value}")
        return decimal_obj
    
    class Config:
        from_attributes = True