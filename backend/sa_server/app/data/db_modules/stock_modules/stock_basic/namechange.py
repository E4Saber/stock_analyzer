import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator


class NameChangeData(BaseModel):
    """
    Pydantic model for stock name change data.
    
    Fields:
    - id: Record ID (auto-increment primary key)
    - ts_code: TS stock code
    - name: Security name
    - start_date: Start date
    - end_date: End date
    - ann_date: Announcement date
    - change_reason: Reason for change
    """
    # 记录ID，自增主键，非必须字段（新增记录时不需要提供）
    id: Optional[int] = None
    # TS股票代码
    ts_code: str
    # 证券名称
    name: str
    # 开始日期
    start_date: datetime.date
    # 结束日期，非必须字段
    end_date: Optional[datetime.date] = None
    # 公告日期，非必须字段
    ann_date: Optional[datetime.date] = None
    # 变更原因，非必须字段
    change_reason: Optional[str] = None

    @field_validator('start_date', 'end_date', 'ann_date', mode='before')
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