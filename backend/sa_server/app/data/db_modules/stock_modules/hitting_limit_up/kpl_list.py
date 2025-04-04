import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class KplListData(BaseModel):
    """
    Pydantic model for KPL list data.
    
    Fields:
    - id: 主键ID
    - ts_code: 代码
    - name: 名称
    - trade_date: 交易时间
    - lu_time: 涨停时间
    - ld_time: 跌停时间
    - open_time: 开板时间
    - last_time: 最后涨停时间
    - lu_desc: 涨停原因
    - tag: 标签
    - theme: 板块
    - net_change: 主力净额(元)
    - bid_amount: 竞价成交额(元)
    - status: 状态（N连板）
    - bid_change: 竞价净额
    - bid_turnover: 竞价换手%
    - lu_bid_vol: 涨停委买额
    - pct_chg: 涨跌幅%
    - bid_pct_chg: 竞价涨幅%
    - rt_pct_chg: 实时涨幅%
    - limit_order: 封单
    - amount: 成交额
    - turnover_rate: 换手率%
    - free_float: 实际流通
    - lu_limit_order: 最大封单
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # 代码
    ts_code: str
    # 名称
    name: str
    # 交易时间
    trade_date: Optional[datetime.date] = None
    # 涨停时间
    lu_time: Optional[str] = None
    # 跌停时间
    ld_time: Optional[str] = None
    # 开板时间
    open_time: Optional[str] = None
    # 最后涨停时间
    last_time: Optional[str] = None
    # 涨停原因
    lu_desc: Optional[str] = None
    # 标签
    tag: Optional[str] = None
    # 板块
    theme: Optional[str] = None
    # 主力净额(元)
    net_change: Optional[Decimal] = None
    # 竞价成交额(元)
    bid_amount: Optional[Decimal] = None
    # 状态（N连板）
    status: Optional[str] = None
    # 竞价净额
    bid_change: Optional[Decimal] = None
    # 竞价换手%
    bid_turnover: Optional[Decimal] = None
    # 涨停委买额
    lu_bid_vol: Optional[Decimal] = None
    # 涨跌幅%
    pct_chg: Optional[Decimal] = None
    # 竞价涨幅%
    bid_pct_chg: Optional[Decimal] = None
    # 实时涨幅%
    rt_pct_chg: Optional[Decimal] = None
    # 封单
    limit_order: Optional[Decimal] = None
    # 成交额
    amount: Optional[Decimal] = None
    # 换手率%
    turnover_rate: Optional[Decimal] = None
    # 实际流通
    free_float: Optional[Decimal] = None
    # 最大封单
    lu_limit_order: Optional[Decimal] = None

    @field_validator('trade_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('net_change', 'bid_amount', 'bid_change', 'bid_turnover', 
                    'lu_bid_vol', 'pct_chg', 'bid_pct_chg', 'rt_pct_chg', 
                    'limit_order', 'amount', 'turnover_rate', 'free_float', 
                    'lu_limit_order', mode='before')
    def parse_numeric(cls, value):
        # 将字符串或浮点数转换为Decimal
        decimal_obj = NumericValidators.to_decimal(value)
        if decimal_obj is None and value is not None and value != '':
            raise ValueError(f"无效的数字格式: {value}")
        return decimal_obj
    
    class Config:
        from_attributes = True