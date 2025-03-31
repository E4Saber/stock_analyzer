import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class WzIndexData(BaseModel):
    """
    Pydantic model for Wenzhou Private Financing Index data.
    
    Fields:
    - date: Date of the index
    - comp_rate: Composite index of Wenzhou private financing rates (%)
    - center_rate: Private lending service center rate
    - micro_rate: Micro lending company loan rate
    - cm_rate: Private capital management company financing rate
    - sdb_rate: Direct social lending rate
    - om_rate: Other market entities rate
    - aa_rate: Rural mutual aid association rate
    - m1_rate: Wenzhou private lending rate (1-month term)
    - m3_rate: Wenzhou private lending rate (3-month term)
    - m6_rate: Wenzhou private lending rate (6-month term)
    - m12_rate: Wenzhou private lending rate (12-month term)
    - long_rate: Wenzhou private lending rate (long-term)
    """
    # 日期
    date: datetime.date
    # 温州民间融资综合利率指数 (%)
    comp_rate: Optional[float] = None
    # 民间借贷服务中心利率
    center_rate: Optional[float] = None
    # 小额贷款公司放款利率
    micro_rate: Optional[float] = None
    # 民间资本管理公司融资价格
    cm_rate: Optional[float] = None
    # 社会直接借贷利率
    sdb_rate: Optional[float] = None
    # 其他市场主体利率
    om_rate: Optional[float] = None
    # 农村互助会互助金费率
    aa_rate: Optional[float] = None
    # 温州地区民间借贷分期限利率（一月期）
    m1_rate: Optional[float] = None
    # 温州地区民间借贷分期限利率（三月期）
    m3_rate: Optional[float] = None
    # 温州地区民间借贷分期限利率（六月期）
    m6_rate: Optional[float] = None
    # 温州地区民间借贷分期限利率（一年期）
    m12_rate: Optional[float] = None
    # 温州地区民间借贷分期限利率（长期）
    long_rate: Optional[float] = None

    @field_validator('date', mode='before')
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