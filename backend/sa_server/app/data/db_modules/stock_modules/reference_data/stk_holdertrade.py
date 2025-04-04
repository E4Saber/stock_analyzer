import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class StkHoldertradeData(BaseModel):
    """
    Pydantic model for stock holder trade data.
    
    Fields:
    - id: 主键ID
    - ts_code: TS股票代码
    - ann_date: 公告日期
    - holder_name: 股东名称
    - holder_type: 股东类型G高管P个人C公司
    - in_de: 类型IN增持DE减持
    - change_vol: 变动数量
    - change_ratio: 占流通比例（%）
    - after_share: 变动后持股
    - after_ratio: 变动后占流通比例（%）
    - avg_price: 平均价格
    - total_share: 持股总数
    - begin_date: 增减持开始日期
    - close_date: 增减持结束日期
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # TS代码，唯一标识
    ts_code: str
    # 公告日期
    ann_date: Optional[datetime.date] = None
    # 股东名称
    holder_name: str
    # 股东类型G高管P个人C公司
    holder_type: Optional[str] = None
    # 类型IN增持DE减持
    in_de: Optional[str] = None
    # 变动数量
    change_vol: Optional[Decimal] = None
    # 占流通比例（%）
    change_ratio: Optional[Decimal] = None
    # 变动后持股
    after_share: Optional[Decimal] = None
    # 变动后占流通比例（%）
    after_ratio: Optional[Decimal] = None
    # 平均价格
    avg_price: Optional[Decimal] = None
    # 持股总数
    total_share: Optional[Decimal] = None
    # 增减持开始日期
    begin_date: Optional[datetime.date] = None
    # 增减持结束日期
    close_date: Optional[datetime.date] = None

    @field_validator('ann_date', 'begin_date', 'close_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('change_vol', 'change_ratio', 'after_share', 'after_ratio', 'avg_price', 'total_share', mode='before')
    def parse_numeric(cls, value):
        # 使用通用工具类进行数值验证
        return NumericValidators.to_decimal(value)
    
    class Config:
        from_attributes = True