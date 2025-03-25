import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class StockBakBasicData(BaseModel):
    """
    Pydantic model for historical daily stock data.
    
    Fields:
    - trade_date: Trading date
    - ts_code: TS stock code
    - name: Stock name
    - industry: Industry
    - area: Region
    - pe: Price-earnings ratio (dynamic)
    - float_share: Circulating shares (100 million)
    - total_share: Total shares (100 million)
    - total_assets: Total assets (100 million)
    - liquid_assets: Liquid assets (100 million)
    - fixed_assets: Fixed assets (100 million)
    - reserved: Reserve fund (CNY)
    - reserved_pershare: Reserve fund per share (CNY/share)
    - eps: Earnings per share (CNY/share)
    - bvps: Book value per share (CNY/share)
    - pb: Price-book ratio
    - list_date: Listing date
    - undp: Undistributed profit (CNY)
    - per_undp: Undistributed profit per share (CNY/share)
    - rev_yoy: Revenue year-on-year (%)
    - profit_yoy: Profit year-on-year (%)
    - gpr: Gross profit ratio (%)
    - npr: Net profit ratio (%)
    - holder_num: Number of shareholders
    """
    # 交易日期
    trade_date: datetime.date
    # TS股票代码
    ts_code: str
    # 股票名称
    name: str
    # 行业，非必须字段
    industry: Optional[str] = None
    # 地域，非必须字段
    area: Optional[str] = None
    # 市盈率（动），非必须字段
    pe: Optional[Decimal] = None
    # 流通股本（亿），非必须字段
    float_share: Optional[Decimal] = None
    # 总股本（亿），非必须字段
    total_share: Optional[Decimal] = None
    # 总资产（亿），非必须字段
    total_assets: Optional[Decimal] = None
    # 流动资产（亿），非必须字段
    liquid_assets: Optional[Decimal] = None
    # 固定资产（亿），非必须字段
    fixed_assets: Optional[Decimal] = None
    # 公积金（元），非必须字段
    reserved: Optional[Decimal] = None
    # 每股公积金（元/股），非必须字段
    reserved_pershare: Optional[Decimal] = None
    # 每股收益（元/股），非必须字段
    eps: Optional[Decimal] = None
    # 每股净资产（元/股），非必须字段
    bvps: Optional[Decimal] = None
    # 市净率，非必须字段
    pb: Optional[Decimal] = None
    # 上市日期，非必须字段
    list_date: Optional[datetime.date] = None
    # 未分配利润（元），非必须字段
    undp: Optional[Decimal] = None
    # 每股未分配利润（元/股），非必须字段
    per_undp: Optional[Decimal] = None
    # 收入同比（%），非必须字段
    rev_yoy: Optional[Decimal] = None
    # 利润同比（%），非必须字段
    profit_yoy: Optional[Decimal] = None
    # 毛利率（%），非必须字段
    gpr: Optional[Decimal] = None
    # 净利润率（%），非必须字段
    npr: Optional[Decimal] = None
    # 股东人数，非必须字段
    holder_num: Optional[int] = None

    @field_validator('trade_date', 'list_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj
    
    @field_validator('pe', 'float_share', 'total_share', 'total_assets', 'liquid_assets', 
                     'fixed_assets', 'reserved', 'reserved_pershare', 'eps', 'bvps', 
                     'pb', 'undp', 'per_undp', 'rev_yoy', 'profit_yoy', 'gpr', 'npr', mode='before')
    def parse_numeric(cls, value):
        # 使用通用工具类进行数值验证
        return NumericValidators.to_decimal(value)
    
    @field_validator('holder_num', mode='before')
    def parse_integer(cls, value):
        # 处理整数字段
        if value is None or value == '':
            return None
        
        # 处理NaN和Infinity
        if isinstance(value, float) and (float('nan') == value or float('inf') == value or float('-inf') == value):
            return None
            
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    class Config:
        from_attributes = True