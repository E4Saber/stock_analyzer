import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class HkTradecalData(BaseModel):
    """
    Pydantic model for Hong Kong trading calendar data.
    
    Fields:
    - id: 主键ID
    - cal_date: 日历日期
    - is_open: 是否交易 0-休市 1-交易
    - pretrade_date: 上一个交易日
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # 日历日期
    cal_date: datetime.date
    # 是否交易 0-休市 1-交易
    is_open: int
    # 上一个交易日
    pretrade_date: Optional[datetime.date] = None

    @field_validator('cal_date', 'pretrade_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('is_open', mode='before')
    def parse_numeric(cls, value):
        # 将字符串或浮点数转换为整数
        num_obj = NumericValidators.to_int(value)
        if num_obj is None and value is not None and value != '':
            raise ValueError(f"无效的数字格式: {value}")
        return num_obj
    
    class Config:
        from_attributes = True