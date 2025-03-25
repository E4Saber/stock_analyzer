import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators


class IndexBasicData(BaseModel):
    """
    Pydantic model for index basic data.
    
    Fields:
    - ts_code: TS code
    - name: Short name
    - fullname: Full index name
    - market: Market
    - publisher: Publisher
    - index_type: Index style
    - category: Index category
    - base_date: Base date
    - base_point: Base point
    - list_date: Listing date
    - weight_rule: Weight rule
    - description: Description
    - exp_date: Expiration date
    """
    # TS代码，唯一标识
    ts_code: str
    # 简称
    name: str
    # 指数全称，非必须字段
    fullname: Optional[str] = None
    # 市场
    market: Optional[str] = None
    # 发布方
    publisher: Optional[str] = None
    # 指数风格
    index_type: Optional[str] = None
    # 指数类别
    category: Optional[str] = None
    # 基期
    base_date: Optional[datetime.date] = None
    # 基点
    base_point: Optional[float] = None
    # 发布日期
    list_date: Optional[datetime.date] = None
    # 加权方式
    weight_rule: Optional[str] = None
    # 描述
    description: Optional[str] = None
    # 终止日期
    exp_date: Optional[datetime.date] = None

    @field_validator('base_date', 'list_date', 'exp_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj
    
    class Config:
        from_attributes = True