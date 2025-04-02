import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class FinaAuditData(BaseModel):
    """
    Pydantic model for financial audit data.
    
    Fields:
    - id: 主键ID
    - ts_code: TS股票代码
    - ann_date: 公告日期
    - end_date: 报告期
    - audit_result: 审计结果
    - audit_fees: 审计总费用（元）
    - audit_agency: 会计事务所
    - audit_sign: 签字会计师
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # TS代码，唯一标识
    ts_code: str
    # 公告日期
    ann_date: Optional[datetime.date] = None
    # 报告期
    end_date: Optional[datetime.date] = None
    
    # 审计相关字段
    audit_result: Optional[str] = None
    audit_fees: Optional[Decimal] = None
    audit_agency: Optional[str] = None
    audit_sign: Optional[str] = None

    @field_validator('ann_date', 'end_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('audit_fees', mode='before')
    def parse_numeric(cls, value):
        # 使用通用工具类进行数值验证
        return NumericValidators.to_decimal(value)
    
    class Config:
        from_attributes = True