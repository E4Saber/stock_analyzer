import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators


class StkHoldernumberData(BaseModel):
    """
    Pydantic model for stock holder number data.
    
    Fields:
    - id: 主键ID
    - ts_code: TS股票代码
    - ann_date: 公告日期
    - end_date: 截止日期
    - holder_num: 股东户数
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # TS代码，唯一标识
    ts_code: str
    # 公告日期
    ann_date: Optional[datetime.date] = None
    # 截止日期
    end_date: Optional[datetime.date] = None
    # 股东户数
    holder_num: Optional[int] = None

    @field_validator('ann_date', 'end_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj
    
    class Config:
        from_attributes = True