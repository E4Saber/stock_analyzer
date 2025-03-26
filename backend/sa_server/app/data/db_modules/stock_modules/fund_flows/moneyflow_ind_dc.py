import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator


class MoneyflowIndDcData(BaseModel):
    """
    Pydantic model for DC industry/concept/region moneyflow data.
    
    Fields:
    - ts_code: DC sector code
    - trade_date: Trading date
    - content_type: Data type (industry, concept, region)
    - name: Sector name
    - pct_change: Sector change percentage (%)
    - close: Sector latest index
    - net_amount: Main force net inflow amount today (yuan)
    - net_amount_rate: Main force net inflow percentage today (%)
    - buy_elg_amount: Extra-large order net inflow amount today (yuan)
    - buy_elg_amount_rate: Extra-large order net inflow percentage today (%)
    - buy_lg_amount: Large order net inflow amount today (yuan)
    - buy_lg_amount_rate: Large order net inflow percentage today (%)
    - buy_md_amount: Medium order net inflow amount today (yuan)
    - buy_md_amount_rate: Medium order net inflow percentage today (%)
    - buy_sm_amount: Small order net inflow amount today (yuan)
    - buy_sm_amount_rate: Small order net inflow percentage today (%)
    - buy_sm_amount_stock: Stock with highest main force net inflow today
    - rank: Ranking
    """
    # DC板块代码
    ts_code: str
    # 交易日期
    trade_date: datetime.date
    # 数据类型（行业、概念、地域）
    content_type: str
    # 板块名称
    name: str
    # 板块涨跌幅（%）
    pct_change: Optional[float] = None
    # 板块最新指数
    close: Optional[float] = None
    # 今日主力净流入 净额（元）
    net_amount: Optional[float] = None
    # 今日主力净流入净占比%
    net_amount_rate: Optional[float] = None
    # 今日超大单净流入 净额（元）
    buy_elg_amount: Optional[float] = None
    # 今日超大单净流入 净占比%
    buy_elg_amount_rate: Optional[float] = None
    # 今日大单净流入 净额（元）
    buy_lg_amount: Optional[float] = None
    # 今日大单净流入 净占比%
    buy_lg_amount_rate: Optional[float] = None
    # 今日中单净流入 净额（元）
    buy_md_amount: Optional[float] = None
    # 今日中单净流入 净占比%
    buy_md_amount_rate: Optional[float] = None
    # 今日小单净流入 净额（元）
    buy_sm_amount: Optional[float] = None
    # 今日小单净流入 净占比%
    buy_sm_amount_rate: Optional[float] = None
    # 今日主力净流入最大股
    buy_sm_amount_stock: Optional[str] = None
    # 序号
    rank: Optional[int] = None

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