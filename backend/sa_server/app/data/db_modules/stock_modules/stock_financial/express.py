import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class ExpressData(BaseModel):
    """
    Pydantic model for express data.
    
    Fields:
    - id: 主键ID
    - ts_code: TS股票代码
    - ann_date: 公告日期
    - end_date: 报告期
    - revenue: 营业收入(元)
    - operate_profit: 营业利润(元)
    - total_profit: 利润总额(元)
    - n_income: 净利润(元)
    - total_assets: 总资产(元)
    - total_hldr_eqy_exc_min_int: 股东权益合计(不含少数股东权益)(元)
    - diluted_eps: 每股收益(摊薄)(元)
    - diluted_roe: 净资产收益率(摊薄)(%)
    - yoy_net_profit: 去年同期修正后净利润
    - bps: 每股净资产
    - yoy_sales: 同比增长率:营业收入
    - yoy_op: 同比增长率:营业利润
    - yoy_tp: 同比增长率:利润总额
    - yoy_dedu_np: 同比增长率:归属母公司股东的净利润
    - yoy_eps: 同比增长率:基本每股收益
    - yoy_roe: 同比增减:加权平均净资产收益率
    - growth_assets: 比年初增长率:总资产
    - yoy_equity: 比年初增长率:归属母公司的股东权益
    - growth_bps: 比年初增长率:归属于母公司股东的每股净资产
    - or_last_year: 去年同期营业收入
    - op_last_year: 去年同期营业利润
    - tp_last_year: 去年同期利润总额
    - np_last_year: 去年同期净利润
    - eps_last_year: 去年同期每股收益
    - open_net_assets: 期初净资产
    - open_bps: 期初每股净资产
    - perf_summary: 业绩简要说明
    - is_audit: 是否审计： 1是 0否
    - remark: 备注
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # TS代码，唯一标识
    ts_code: str
    # 公告日期
    ann_date: Optional[datetime.date] = None
    # 报告期
    end_date: Optional[datetime.date] = None
    
    # 业绩数据
    revenue: Optional[Decimal] = None
    operate_profit: Optional[Decimal] = None
    total_profit: Optional[Decimal] = None
    n_income: Optional[Decimal] = None
    total_assets: Optional[Decimal] = None
    total_hldr_eqy_exc_min_int: Optional[Decimal] = None
    diluted_eps: Optional[Decimal] = None
    diluted_roe: Optional[Decimal] = None
    yoy_net_profit: Optional[Decimal] = None
    bps: Optional[Decimal] = None
    
    # 同比增长率
    yoy_sales: Optional[Decimal] = None
    yoy_op: Optional[Decimal] = None
    yoy_tp: Optional[Decimal] = None
    yoy_dedu_np: Optional[Decimal] = None
    yoy_eps: Optional[Decimal] = None
    yoy_roe: Optional[Decimal] = None
    growth_assets: Optional[Decimal] = None
    yoy_equity: Optional[Decimal] = None
    growth_bps: Optional[Decimal] = None
    
    # 去年同期数据
    or_last_year: Optional[Decimal] = None
    op_last_year: Optional[Decimal] = None
    tp_last_year: Optional[Decimal] = None
    np_last_year: Optional[Decimal] = None
    eps_last_year: Optional[Decimal] = None
    
    # 期初数据
    open_net_assets: Optional[Decimal] = None
    open_bps: Optional[Decimal] = None
    
    # 其他信息
    perf_summary: Optional[str] = None
    is_audit: Optional[int] = None
    remark: Optional[str] = None

    @field_validator('ann_date', 'end_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('revenue', 'operate_profit', 'total_profit', 'n_income', 'total_assets', 
                   'total_hldr_eqy_exc_min_int', 'diluted_eps', 'diluted_roe', 'yoy_net_profit', 
                   'bps', 'yoy_sales', 'yoy_op', 'yoy_tp', 'yoy_dedu_np', 'yoy_eps', 'yoy_roe', 
                   'growth_assets', 'yoy_equity', 'growth_bps', 'or_last_year', 'op_last_year', 
                   'tp_last_year', 'np_last_year', 'eps_last_year', 'open_net_assets', 'open_bps', 
                   mode='before')
    def parse_numeric(cls, value):
        # 使用通用工具类进行数值验证
        return NumericValidators.to_decimal(value)
    
    class Config:
        from_attributes = True