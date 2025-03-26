import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator


class MoneyflowThsData(BaseModel):
    """
    Pydantic model for THS stock moneyflow data.
    
    Fields:
    - ts_code: Stock code
    - trade_date: Trading date
    - name: Stock name
    - pct_change: Price change percentage
    - latest: Latest price
    - net_amount: Net inflow amount (10,000 yuan)
    - net_d5_amount: 5-day main force net amount (10,000 yuan)
    - buy_lg_amount: Today's large order net inflow amount (10,000 yuan)
    - buy_lg_amount_rate: Today's large order net inflow percentage (%)
    - buy_md_amount: Today's medium order net inflow amount (10,000 yuan)
    - buy_md_amount_rate: Today's medium order net inflow percentage (%)
    - buy_sm_amount: Today's small order net inflow amount (10,000 yuan)
    - buy_sm_amount_rate: Today's small order net inflow percentage (%)
    """
    # 股票代码
    ts_code: str
    # 交易日期
    trade_date: datetime.date
    # 股票名称
    name: str
    # 涨跌幅
    pct_change: Optional[float] = None
    # 最新价
    latest: Optional[float] = None
    # 资金净流入(万元)
    net_amount: Optional[float] = None
    # 5日主力净额(万元)
    net_d5_amount: Optional[float] = None
    # 今日大单净流入额(万元)
    buy_lg_amount: Optional[float] = None
    # 今日大单净流入占比(%)
    buy_lg_amount_rate: Optional[float] = None
    # 今日中单净流入额(万元)
    buy_md_amount: Optional[float] = None
    # 今日中单净流入占比(%)
    buy_md_amount_rate: Optional[float] = None
    # 今日小单净流入额(万元)
    buy_sm_amount: Optional[float] = None
    # 今日小单净流入占比(%)
    buy_sm_amount_rate: Optional[float] = None

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