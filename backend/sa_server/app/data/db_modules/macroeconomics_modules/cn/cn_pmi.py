import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CnPmiData(BaseModel):
    """
    Pydantic model for China PMI data.
    
    Fields:
    - month: Month in YYYYMM format
    - pmi010000: Manufacturing PMI
    - pmi010100: Manufacturing PMI: Large Enterprises
    - pmi010200: Manufacturing PMI: Medium Enterprises
    - pmi010300: Manufacturing PMI: Small Enterprises
    ...(and other PMI related fields)
    """
    # 月份，格式YYYYMM，主键
    month: str
    
    # 制造业PMI相关字段
    pmi010000: Optional[float] = None  # 制造业PMI
    pmi010100: Optional[float] = None  # 制造业PMI:企业规模/大型企业
    pmi010200: Optional[float] = None  # 制造业PMI:企业规模/中型企业
    pmi010300: Optional[float] = None  # 制造业PMI:企业规模/小型企业
    pmi010400: Optional[float] = None  # 制造业PMI:构成指数/生产指数
    pmi010401: Optional[float] = None  # 制造业PMI:构成指数/生产指数:企业规模/大型企业
    pmi010402: Optional[float] = None  # 制造业PMI:构成指数/生产指数:企业规模/中型企业
    pmi010403: Optional[float] = None  # 制造业PMI:构成指数/生产指数:企业规模/小型企业
    pmi010500: Optional[float] = None  # 制造业PMI:构成指数/新订单指数
    pmi010501: Optional[float] = None  # 制造业PMI:构成指数/新订单指数:企业规模/大型企业
    pmi010502: Optional[float] = None  # 制造业PMI:构成指数/新订单指数:企业规模/中型企业
    pmi010503: Optional[float] = None  # 制造业PMI:构成指数/新订单指数:企业规模/小型企业
    pmi010600: Optional[float] = None  # 制造业PMI:构成指数/供应商配送时间指数
    pmi010601: Optional[float] = None  # 制造业PMI:构成指数/供应商配送时间指数:企业规模/大型企业
    pmi010602: Optional[float] = None  # 制造业PMI:构成指数/供应商配送时间指数:企业规模/中型企业
    pmi010603: Optional[float] = None  # 制造业PMI:构成指数/供应商配送时间指数:企业规模/小型企业
    pmi010700: Optional[float] = None  # 制造业PMI:构成指数/原材料库存指数
    pmi010701: Optional[float] = None  # 制造业PMI:构成指数/原材料库存指数:企业规模/大型企业
    pmi010702: Optional[float] = None  # 制造业PMI:构成指数/原材料库存指数:企业规模/中型企业
    pmi010703: Optional[float] = None  # 制造业PMI:构成指数/原材料库存指数:企业规模/小型企业
    pmi010800: Optional[float] = None  # 制造业PMI:构成指数/从业人员指数
    pmi010801: Optional[float] = None  # 制造业PMI:构成指数/从业人员指数:企业规模/大型企业
    pmi010802: Optional[float] = None  # 制造业PMI:构成指数/从业人员指数:企业规模/中型企业
    pmi010803: Optional[float] = None  # 制造业PMI:构成指数/从业人员指数:企业规模/小型企业
    pmi010900: Optional[float] = None  # 制造业PMI:其他/新出口订单
    pmi011000: Optional[float] = None  # 制造业PMI:其他/进口
    pmi011100: Optional[float] = None  # 制造业PMI:其他/采购量
    pmi011200: Optional[float] = None  # 制造业PMI:其他/主要原材料购进价格
    pmi011300: Optional[float] = None  # 制造业PMI:其他/出厂价格
    pmi011400: Optional[float] = None  # 制造业PMI:其他/产成品库存
    pmi011500: Optional[float] = None  # 制造业PMI:其他/在手订单
    pmi011600: Optional[float] = None  # 制造业PMI:其他/生产经营活动预期
    pmi011700: Optional[float] = None  # 制造业PMI:分行业/装备制造业
    pmi011800: Optional[float] = None  # 制造业PMI:分行业/高技术制造业
    pmi011900: Optional[float] = None  # 制造业PMI:分行业/基础原材料制造业
    pmi012000: Optional[float] = None  # 制造业PMI:分行业/消费品制造业
    
    # 非制造业PMI相关字段
    pmi020100: Optional[float] = None  # 非制造业PMI:商务活动
    pmi020101: Optional[float] = None  # 非制造业PMI:商务活动:分行业/建筑业
    pmi020102: Optional[float] = None  # 非制造业PMI:商务活动:分行业/服务业
    pmi020200: Optional[float] = None  # 非制造业PMI:新订单指数
    pmi020201: Optional[float] = None  # 非制造业PMI:新订单指数:分行业/建筑业
    pmi020202: Optional[float] = None  # 非制造业PMI:新订单指数:分行业/服务业
    pmi020300: Optional[float] = None  # 非制造业PMI:投入品价格指数
    pmi020301: Optional[float] = None  # 非制造业PMI:投入品价格指数:分行业/建筑业
    pmi020302: Optional[float] = None  # 非制造业PMI:投入品价格指数:分行业/服务业
    pmi020400: Optional[float] = None  # 非制造业PMI:销售价格指数
    pmi020401: Optional[float] = None  # 非制造业PMI:销售价格指数:分行业/建筑业
    pmi020402: Optional[float] = None  # 非制造业PMI:销售价格指数:分行业/服务业
    pmi020500: Optional[float] = None  # 非制造业PMI:从业人员指数
    pmi020501: Optional[float] = None  # 非制造业PMI:从业人员指数:分行业/建筑业
    pmi020502: Optional[float] = None  # 非制造业PMI:从业人员指数:分行业/服务业
    pmi020600: Optional[float] = None  # 非制造业PMI:业务活动预期指数
    pmi020601: Optional[float] = None  # 非制造业PMI:业务活动预期指数:分行业/建筑业
    pmi020602: Optional[float] = None  # 非制造业PMI:业务活动预期指数:分行业/服务业
    pmi020700: Optional[float] = None  # 非制造业PMI:新出口订单
    pmi020800: Optional[float] = None  # 非制造业PMI:在手订单
    pmi020900: Optional[float] = None  # 非制造业PMI:存货
    pmi021000: Optional[float] = None  # 非制造业PMI:供应商配送时间
    
    # 综合PMI相关字段
    pmi030000: Optional[float] = None  # 中国综合PMI:产出指数
    
    @field_validator('month')
    def validate_month(cls, value):
        """验证月份格式，必须是YYYYMM格式"""
        if not isinstance(value, str):
            raise ValueError(f"月份必须是字符串: {value}")
        
        if not value.isdigit() or len(value) != 6:
            raise ValueError(f"月份必须是YYYYMM格式: {value}")
        
        # 验证月份范围
        year = int(value[:4])
        month = int(value[4:])
        
        if year < 1949 or year > 2100:
            raise ValueError(f"年份超出有效范围: {year}")
            
        if month < 1 or month > 12:
            raise ValueError(f"月份超出有效范围: {month}")
            
        return value

    class Config:
        from_attributes = True