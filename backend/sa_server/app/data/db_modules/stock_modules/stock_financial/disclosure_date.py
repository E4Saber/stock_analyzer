import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators


class DisclosureDateData(BaseModel):
    """
    Pydantic model for disclosure date data.
    
    Fields:
    - id: 主键ID
    - ts_code: TS代码
    - end_date: 报告期
    - ann_date: 最新披露公告日
    - pre_date: 预计披露日期
    - actual_date: 实际披露日期
    - modify_date: 披露日期修正记录
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # TS代码，唯一标识
    ts_code: str
    # 报告期
    end_date: Optional[datetime.date] = None
    
    # 披露日期相关字段
    ann_date: Optional[datetime.date] = None
    pre_date: Optional[datetime.date] = None
    actual_date: Optional[datetime.date] = None
    modify_date: Optional[datetime.date] = None

    @field_validator('end_date', 'ann_date', 'pre_date', 'actual_date', 'modify_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj
    
    class Config:
        from_attributes = True