import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator


class StockManagerData(BaseModel):
    """
    Pydantic model for company managers data.
    
    Fields:
    - id: Auto-incremented primary key
    - ts_code: TS stock code
    - ann_date: Announcement date
    - name: Manager name
    - gender: Gender
    - lev: Position category
    - title: Position title
    - edu: Education
    - national: Nationality
    - birthday: Birth date
    - begin_date: Appointment date
    - end_date: Departure date
    - resume: Personal resume
    """
    # 自增主键，非必须字段，新建时无需提供
    id: Optional[int] = None
    # TS股票代码
    ts_code: str
    # 公告日期，非必须字段
    ann_date: Optional[datetime.date] = None
    # 姓名
    name: str
    # 性别，非必须字段
    gender: Optional[str] = None
    # 岗位类别，非必须字段
    lev: Optional[str] = None
    # 岗位，非必须字段
    title: Optional[str] = None
    # 学历，非必须字段
    edu: Optional[str] = None
    # 国籍，非必须字段
    national: Optional[str] = None
    # 出生年月，非必须字段
    birthday: Optional[str] = None
    # 上任日期，非必须字段
    begin_date: Optional[datetime.date] = None
    # 离任日期，非必须字段
    end_date: Optional[datetime.date] = None
    # 个人简历，非必须字段
    resume: Optional[str] = None

    @field_validator('ann_date', 'begin_date', 'end_date', mode='before')
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