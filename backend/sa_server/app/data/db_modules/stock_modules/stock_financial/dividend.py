import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class DividendData(BaseModel):
    """
    Pydantic model for dividend data.
    
    Fields:
    - id: 主键ID
    - ts_code: TS代码
    - end_date: 分红年度
    - ann_date: 预案公告日
    - div_proc: 实施进度
    - stk_div: 每股送转
    - stk_bo_rate: 每股送股比例
    - stk_co_rate: 每股转增比例
    - cash_div: 每股分红（税后）
    - cash_div_tax: 每股分红（税前）
    - record_date: 股权登记日
    - ex_date: 除权除息日
    - pay_date: 派息日
    - div_listdate: 红股上市日
    - imp_ann_date: 实施公告日
    - base_date: 基准日
    - base_share: 基准股本（万）
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # TS代码，唯一标识
    ts_code: str
    # 分红年度
    end_date: Optional[datetime.date] = None
    # 预案公告日
    ann_date: Optional[datetime.date] = None
    # 实施进度
    div_proc: Optional[str] = None
    
    # 股票分红相关字段
    stk_div: Optional[Decimal] = None
    stk_bo_rate: Optional[Decimal] = None
    stk_co_rate: Optional[Decimal] = None
    
    # 现金分红相关字段
    cash_div: Optional[Decimal] = None
    cash_div_tax: Optional[Decimal] = None
    
    # 重要日期
    record_date: Optional[datetime.date] = None
    ex_date: Optional[datetime.date] = None
    pay_date: Optional[datetime.date] = None
    div_listdate: Optional[datetime.date] = None
    imp_ann_date: Optional[datetime.date] = None
    
    # 额外字段
    base_date: Optional[datetime.date] = None
    base_share: Optional[Decimal] = None

    @field_validator('end_date', 'ann_date', 'record_date', 'ex_date', 'pay_date', 'div_listdate', 'imp_ann_date', 'base_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('stk_div', 'stk_bo_rate', 'stk_co_rate', 'cash_div', 'cash_div_tax', 'base_share', mode='before')
    def parse_numeric(cls, value):
        # 使用通用工具类进行数值验证
        return NumericValidators.to_decimal(value)
    
    class Config:
        from_attributes = True