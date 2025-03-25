import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator


class MoneyflowData(BaseModel):
    """
    Pydantic model for stock moneyflow data.
    
    Fields:
    - ts_code: TS code
    - trade_date: Trading date
    - buy_sm_vol: Small order buy volume (lot)
    - buy_sm_amount: Small order buy amount (10k yuan)
    - sell_sm_vol: Small order sell volume (lot)
    - sell_sm_amount: Small order sell amount (10k yuan)
    - buy_md_vol: Medium order buy volume (lot)
    - buy_md_amount: Medium order buy amount (10k yuan)
    - sell_md_vol: Medium order sell volume (lot)
    - sell_md_amount: Medium order sell amount (10k yuan)
    - buy_lg_vol: Large order buy volume (lot)
    - buy_lg_amount: Large order buy amount (10k yuan)
    - sell_lg_vol: Large order sell volume (lot)
    - sell_lg_amount: Large order sell amount (10k yuan)
    - buy_elg_vol: Extra-large order buy volume (lot)
    - buy_elg_amount: Extra-large order buy amount (10k yuan)
    - sell_elg_vol: Extra-large order sell volume (lot)
    - sell_elg_amount: Extra-large order sell amount (10k yuan)
    - net_mf_vol: Net inflow volume (lot)
    - net_mf_amount: Net inflow amount (10k yuan)
    """
    # TS代码
    ts_code: str
    # 交易日期
    trade_date: datetime.date
    # 小单买入量（手）
    buy_sm_vol: Optional[int] = None
    # 小单买入金额（万元）
    buy_sm_amount: Optional[float] = None
    # 小单卖出量（手）
    sell_sm_vol: Optional[int] = None
    # 小单卖出金额（万元）
    sell_sm_amount: Optional[float] = None
    # 中单买入量（手）
    buy_md_vol: Optional[int] = None
    # 中单买入金额（万元）
    buy_md_amount: Optional[float] = None
    # 中单卖出量（手）
    sell_md_vol: Optional[int] = None
    # 中单卖出金额（万元）
    sell_md_amount: Optional[float] = None
    # 大单买入量（手）
    buy_lg_vol: Optional[int] = None
    # 大单买入金额（万元）
    buy_lg_amount: Optional[float] = None
    # 大单卖出量（手）
    sell_lg_vol: Optional[int] = None
    # 大单卖出金额（万元）
    sell_lg_amount: Optional[float] = None
    # 特大单买入量（手）
    buy_elg_vol: Optional[int] = None
    # 特大单买入金额（万元）
    buy_elg_amount: Optional[float] = None
    # 特大单卖出量（手）
    sell_elg_vol: Optional[int] = None
    # 特大单卖出金额（万元）
    sell_elg_amount: Optional[float] = None
    # 净流入量（手）
    net_mf_vol: Optional[int] = None
    # 净流入额（万元）
    net_mf_amount: Optional[float] = None

    @field_validator('trade_date', mode='before')
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