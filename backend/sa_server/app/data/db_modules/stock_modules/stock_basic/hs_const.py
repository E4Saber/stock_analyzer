import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator


class HsConstData(BaseModel):
    """
    Pydantic model for Hong Kong Stock Connect constituent stock data.
    
    Fields:
    - id: Record ID (auto-increment primary key)
    - ts_code: TS stock code
    - hs_type: Shanghai/Shenzhen Stock Connect type (SH for Shanghai, SZ for Shenzhen)
    - in_date: Inclusion date
    - out_date: Exclusion date
    - is_new: Whether it's the latest record (1 for yes, 0 for no)
    """
    # 记录ID，自增主键，非必须字段（新增记录时不需要提供）
    id: Optional[int] = None
    # TS股票代码
    ts_code: str
    # 沪深港通类型 SH沪 SZ深
    hs_type: str
    # 纳入日期
    in_date: datetime.date
    # 剔除日期，非必须字段
    out_date: Optional[datetime.date] = None
    # 是否最新 1是 0否
    is_new: str

    @field_validator('hs_type')
    def validate_hs_type(cls, value):
        if value not in ['SH', 'SZ']:
            raise ValueError("hs_type必须为'SH'或'SZ'")
        return value
    
    @field_validator('is_new')
    def validate_is_new(cls, value):
        if value not in ['0', '1']:
            raise ValueError("is_new必须为'0'或'1'")
        return value
    
    @field_validator('in_date', 'out_date', mode='before')
    def parse_date(cls, value):
        if value is None or value == '':
            return None
        
        if isinstance(value, datetime.date):
            return value
        
        try:
            # 假设日期格式为 'YYYYMMDD'
            if isinstance(value, str) and value.isdigit() and len(value) == 8:
                year = int(value[:4])
                month = int(value[4:6])
                day = int(value[6:8])
                return datetime.date(year, month, day)
            # 其他常见格式
            return datetime.date.fromisoformat(value)
        except (ValueError, TypeError):
            raise ValueError(f"无效的日期格式: {value}")
    
    class Config:
        from_attributes = True