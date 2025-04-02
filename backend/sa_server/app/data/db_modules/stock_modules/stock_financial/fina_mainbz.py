import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class FinaMainbzData(BaseModel):
    """
    Pydantic model for financial main business data.
    
    Fields:
    - id: 主键ID
    - ts_code: TS代码
    - end_date: 报告期
    - bz_item: 主营业务来源
    - bz_sales: 主营业务收入(元)
    - bz_profit: 主营业务利润(元)
    - bz_cost: 主营业务成本(元)
    - curr_type: 货币代码
    - type: 类型（P按产品 D按地区 I按行业）
    - update_flag: 是否更新
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # TS代码，唯一标识
    ts_code: str
    # 报告期
    end_date: Optional[datetime.date] = None
    
    # 主营业务构成字段
    bz_item: Optional[str] = None
    bz_sales: Optional[Decimal] = None
    bz_profit: Optional[Decimal] = None
    bz_cost: Optional[Decimal] = None
    curr_type: Optional[str] = None
    
    # 类型区分
    type: Optional[str] = None
    
    # 更新标识
    update_flag: Optional[str] = None

    @field_validator('end_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('bz_sales', 'bz_profit', 'bz_cost', mode='before')
    def parse_numeric(cls, value):
        # 使用通用工具类进行数值验证
        return NumericValidators.to_decimal(value)
    
    class Config:
        from_attributes = True