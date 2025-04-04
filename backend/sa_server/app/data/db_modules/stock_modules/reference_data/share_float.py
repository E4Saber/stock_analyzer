import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class ShareFloatData(BaseModel):
    """
    Pydantic model for share float (limited sale share unlocked) data.
    
    Fields:
    - id: 主键ID
    - ts_code: TS股票代码
    - ann_date: 公告日期
    - float_date: 解禁日期
    - float_share: 流通股份(股)
    - float_ratio: 流通股份占总股本比率
    - holder_name: 股东名称
    - share_type: 股份类型
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # TS代码，唯一标识
    ts_code: str
    # 公告日期
    ann_date: Optional[datetime.date] = None
    # 解禁日期
    float_date: Optional[datetime.date] = None
    # 流通股份(股)
    float_share: Optional[Decimal] = None
    # 流通股份占总股本比率
    float_ratio: Optional[Decimal] = None
    # 股东名称
    holder_name: Optional[str] = None
    # 股份类型
    share_type: Optional[str] = None

    @field_validator('ann_date', 'float_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('float_share', 'float_ratio', mode='before')
    def parse_numeric(cls, value):
        # 使用通用工具类进行数值验证
        return NumericValidators.to_decimal(value)
    
    class Config:
        from_attributes = True