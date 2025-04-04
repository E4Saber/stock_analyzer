import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class PledgeStatData(BaseModel):
    """
    Pydantic model for stock pledge statistics data.
    
    Fields:
    - id: 主键ID
    - ts_code: TS股票代码
    - end_date: 截止日期
    - pledge_count: 质押次数
    - unrest_pledge: 无限售股质押数量（万）
    - rest_pledge: 限售股份质押数量（万）
    - total_share: 总股本
    - pledge_ratio: 质押比例
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # TS代码，唯一标识
    ts_code: str
    # 截止日期
    end_date: Optional[datetime.date] = None
    # 质押次数
    pledge_count: Optional[int] = None
    # 无限售股质押数量（万）
    unrest_pledge: Optional[Decimal] = None
    # 限售股份质押数量（万）
    rest_pledge: Optional[Decimal] = None
    # 总股本
    total_share: Optional[Decimal] = None
    # 质押比例
    pledge_ratio: Optional[Decimal] = None

    @field_validator('end_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('unrest_pledge', 'rest_pledge', 'total_share', 'pledge_ratio', mode='before')
    def parse_numeric(cls, value):
        # 使用通用工具类进行数值验证
        return NumericValidators.to_decimal(value)
    
    class Config:
        from_attributes = True