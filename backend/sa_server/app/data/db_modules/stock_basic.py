from pydantic import BaseModel
from typing import Optional
import datetime
from pydantic import field_validator


class StockBasicData(BaseModel):
    """
    Pydantic model for stock basic data.
    
    Fields:
    - ts_code: TS code
    - symbol: Stock code
    - name: Stock name
    - area: Region
    - industry: Industry
    - fullname: Full stock name
    - enname: English name
    - cnspell: Pinyin abbreviation
    - market: Market type (Main Board/GEM/STAR Market/CDR)
    - exchange: Exchange code
    - curr_type: Trading currency
    - list_status: Listing status: L-Listed, D-Delisted, P-Suspended
    - list_date: Listing date
    - delist_date: Delisting date
    - is_hs: Whether it's a Hong Kong Stock Connect target, N-No, H-Shanghai Connect, S-Shenzhen Connect
    - act_name: Name of actual controller
    - act_ent_type: Enterprise type of actual controller
    """
    # TS代码，唯一标识
    ts_code: str
    # 股票代码
    symbol: str
    # 股票名称
    name: str
    # 地域
    area: str
    # 所属行业
    industry: str
    # 股票全称，非必须字段
    fullname: Optional[str] = None
    # 英文全称，非必须字段
    enname: Optional[str] = None
    # 拼音缩写
    cnspell: str
    # 市场类型（主板/创业板/科创板/CDR）
    market: str
    # 交易所代码，非必须字段
    exchange: Optional[str] = None
    # 交易货币，非必须字段
    curr_type: Optional[str] = None
    # 上市状态 L上市 D退市 P暂停上市，非必须字段
    list_status: Optional[str] = None
    # 上市日期
    list_date: Optional[datetime.date] = None
    # 退市日期，非必须字段
    delist_date: Optional[datetime.date] = None
    # 是否沪深港通标的，N否 H沪股通 S深股通，非必须字段
    is_hs: Optional[str] = None
    # 实控人名称
    act_name: str
    # 实控人企业性质
    act_ent_type: str

    @field_validator('list_date', 'delist_date', mode='before')
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