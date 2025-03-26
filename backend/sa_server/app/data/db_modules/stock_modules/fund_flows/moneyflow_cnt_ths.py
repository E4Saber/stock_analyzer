import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator


class MoneyflowCntThsData(BaseModel):
    """
    Pydantic model for THS industry/sector moneyflow data.
    
    Fields:
    - ts_code: Sector code
    - trade_date: Trading date
    - name: Sector name
    - lead_stock: Leading stock name
    - close_price: Latest price
    - pct_change: Industry change percentage
    - index_close: Sector index
    - company_num: Number of companies
    - pct_change_stock: Leading stock change percentage
    - net_buy_amount: Inflow amount (yuan)
    - net_sell_amount: Outflow amount (yuan)
    - net_amount: Net amount (yuan)
    """
    # 板块代码
    ts_code: str
    # 交易日期
    trade_date: datetime.date
    # 板块名称
    name: str
    # 领涨股票名称
    lead_stock: Optional[str] = None
    # 最新价
    close_price: Optional[float] = None
    # 行业涨跌幅
    pct_change: Optional[float] = None
    # 板块指数
    index_close: Optional[float] = None
    # 公司数量
    company_num: Optional[int] = None
    # 领涨股涨跌幅
    pct_change_stock: Optional[float] = None
    # 流入资金(元)
    net_buy_amount: Optional[float] = None
    # 流出资金(元)
    net_sell_amount: Optional[float] = None
    # 净额(元)
    net_amount: Optional[float] = None

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