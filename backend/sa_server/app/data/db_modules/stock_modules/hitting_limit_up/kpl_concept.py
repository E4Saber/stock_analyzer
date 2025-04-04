import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class KplConceptData(BaseModel):
    """
    Pydantic model for KPL concept data.
    
    Fields:
    - id: 主键ID
    - trade_date: 交易日期
    - ts_code: 题材代码
    - name: 题材名称
    - z_t_num: 涨停数量
    - up_num: 排名上升位数
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # 交易日期
    trade_date: Optional[datetime.date] = None
    # 题材代码
    ts_code: str
    # 题材名称
    name: str
    # 涨停数量
    z_t_num: Optional[int] = None
    # 排名上升位数
    up_num: Optional[int] = None

    @field_validator('trade_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('z_t_num', 'up_num', mode='before')
    def parse_numeric(cls, value):
        # 将字符串或浮点数转换为整数
        num_obj = NumericValidators.to_int(value)
        if num_obj is None and value is not None and value != '':
            raise ValueError(f"无效的数字格式: {value}")
        return num_obj
    
    class Config:
        from_attributes = True