import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class HkBasicData(BaseModel):
    """
    Pydantic model for Hong Kong stock basic information data.
    
    Fields:
    - id: 主键ID
    - ts_code: TS代码
    - name: 股票简称
    - fullname: 公司全称
    - enname: 英文名称
    - cn_spell: 拼音
    - market: 市场类别
    - list_status: 上市状态 L上市 D退市 P暂停上市
    - list_date: 上市日期
    - delist_date: 退市日期
    - trade_unit: 交易单位
    - isin: ISIN代码
    - curr_type: 货币代码
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # TS代码
    ts_code: str
    # 股票简称
    name: Optional[str] = None
    # 公司全称
    fullname: Optional[str] = None
    # 英文名称
    enname: Optional[str] = None
    # 拼音
    cn_spell: Optional[str] = None
    # 市场类别
    market: Optional[str] = None
    # 上市状态 L上市 D退市 P暂停上市
    list_status: Optional[str] = None
    # 上市日期
    list_date: Optional[datetime.date] = None
    # 退市日期
    delist_date: Optional[datetime.date] = None
    # 交易单位
    trade_unit: Optional[float] = None
    # ISIN代码
    isin: Optional[str] = None
    # 货币代码
    curr_type: Optional[str] = None

    @field_validator('list_date', 'delist_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('trade_unit', mode='before')
    def parse_float(cls, value):
        # 将字符串或整数转换为浮点数
        float_obj = NumericValidators.to_float(value)
        if float_obj is None and value is not None and value != '':
            raise ValueError(f"无效的浮点数格式: {value}")
        return float_obj
    
    class Config:
        from_attributes = True