import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class PledgeDetailData(BaseModel):
    """
    Pydantic model for stock pledge detail data.
    
    Fields:
    - id: 主键ID
    - ts_code: TS股票代码
    - ann_date: 公告日期
    - holder_name: 股东名称
    - pledge_amount: 质押数量（万股）
    - start_date: 质押开始日期
    - end_date: 质押结束日期
    - is_release: 是否已解押
    - release_date: 解押日期
    - pledgor: 质押方
    - holding_amount: 持股总数（万股）
    - pledged_amount: 质押总数（万股）
    - p_total_ratio: 本次质押占总股本比例
    - h_total_ratio: 持股总数占总股本比例
    - is_buyback: 是否回购
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # TS代码，唯一标识
    ts_code: str
    # 公告日期
    ann_date: Optional[datetime.date] = None
    # 股东名称
    holder_name: str
    # 质押数量（万股）
    pledge_amount: Optional[Decimal] = None
    # 质押开始日期
    start_date: Optional[datetime.date] = None
    # 质押结束日期
    end_date: Optional[datetime.date] = None
    # 是否已解押
    is_release: Optional[str] = None
    # 解押日期
    release_date: Optional[datetime.date] = None
    # 质押方
    pledgor: Optional[str] = None
    # 持股总数（万股）
    holding_amount: Optional[Decimal] = None
    # 质押总数（万股）
    pledged_amount: Optional[Decimal] = None
    # 本次质押占总股本比例
    p_total_ratio: Optional[Decimal] = None
    # 持股总数占总股本比例
    h_total_ratio: Optional[Decimal] = None
    # 是否回购
    is_buyback: Optional[str] = None

    @field_validator('ann_date', 'start_date', 'end_date', 'release_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('pledge_amount', 'holding_amount', 'pledged_amount', 'p_total_ratio', 'h_total_ratio', mode='before')
    def parse_numeric(cls, value):
        # 使用通用工具类进行数值验证
        return NumericValidators.to_decimal(value)
    
    class Config:
        from_attributes = True