import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class ForecastData(BaseModel):
    """
    Pydantic model for forecast data.
    
    Fields:
    - id: 主键ID
    - ts_code: TS股票代码
    - ann_date: 公告日期
    - end_date: 报告期
    - type: 业绩预告类型(预增/预减/扭亏/首亏/续亏/续盈/略增/略减)
    - p_change_min: 预告净利润变动幅度下限（%）
    - p_change_max: 预告净利润变动幅度上限（%）
    - net_profit_min: 预告净利润下限（万元）
    - net_profit_max: 预告净利润上限（万元）
    - last_parent_net: 上年同期归属母公司净利润（万元）
    - first_ann_date: 首次公告日
    - summary: 业绩预告摘要
    - change_reason: 业绩变动原因
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # TS代码，唯一标识
    ts_code: str
    # 公告日期
    ann_date: Optional[datetime.date] = None
    # 报告期
    end_date: Optional[datetime.date] = None
    # 业绩预告类型
    type: Optional[str] = None
    
    # 预告净利润变动幅度
    p_change_min: Optional[Decimal] = None
    p_change_max: Optional[Decimal] = None
    
    # 预告净利润金额
    net_profit_min: Optional[Decimal] = None
    net_profit_max: Optional[Decimal] = None
    
    # 上年同期数据
    last_parent_net: Optional[Decimal] = None
    
    # 公告信息
    first_ann_date: Optional[datetime.date] = None
    summary: Optional[str] = None
    change_reason: Optional[str] = None

    @field_validator('ann_date', 'end_date', 'first_ann_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('p_change_min', 'p_change_max', 'net_profit_min', 'net_profit_max', 'last_parent_net', mode='before')
    def parse_numeric(cls, value):
        # 使用通用工具类进行数值验证
        return NumericValidators.to_decimal(value)
    
    class Config:
        from_attributes = True