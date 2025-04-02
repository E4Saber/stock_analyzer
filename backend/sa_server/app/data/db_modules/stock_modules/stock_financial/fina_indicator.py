import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class FinaIndicatorData(BaseModel):
    """
    Pydantic model for financial indicator data.
    
    Fields:
    - id: 主键ID
    - ts_code: TS代码
    - ann_date: 公告日期
    - end_date: 报告期
    - eps: 基本每股收益
    - dt_eps: 稀释每股收益
    - ...多个财务指标字段
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # TS代码，唯一标识
    ts_code: str
    # 公告日期
    ann_date: Optional[datetime.date] = None
    # 报告期
    end_date: Optional[datetime.date] = None
    
    # 每股指标
    eps: Optional[Decimal] = None
    dt_eps: Optional[Decimal] = None
    total_revenue_ps: Optional[Decimal] = None
    revenue_ps: Optional[Decimal] = None
    capital_rese_ps: Optional[Decimal] = None
    surplus_rese_ps: Optional[Decimal] = None
    undist_profit_ps: Optional[Decimal] = None
    extra_item: Optional[Decimal] = None
    profit_dedt: Optional[Decimal] = None
    
    # 盈利能力指标
    gross_margin: Optional[Decimal] = None
    netprofit_margin: Optional[Decimal] = None
    grossprofit_margin: Optional[Decimal] = None
    cogs_of_sales: Optional[Decimal] = None
    expense_of_sales: Optional[Decimal] = None
    profit_to_gr: Optional[Decimal] = None
    saleexp_to_gr: Optional[Decimal] = None
    adminexp_of_gr: Optional[Decimal] = None
    finaexp_of_gr: Optional[Decimal] = None
    impai_ttm: Optional[Decimal] = None
    gc_of_gr: Optional[Decimal] = None
    op_of_gr: Optional[Decimal] = None
    ebit_of_gr: Optional[Decimal] = None
    
    # 偿债能力指标
    current_ratio: Optional[Decimal] = None
    quick_ratio: Optional[Decimal] = None
    cash_ratio: Optional[Decimal] = None
    debt_to_assets: Optional[Decimal] = None
    assets_to_eqt: Optional[Decimal] = None
    dp_assets_to_eqt: Optional[Decimal] = None
    debt_to_eqt: Optional[Decimal] = None
    eqt_to_debt: Optional[Decimal] = None
    
    # 运营能力指标
    invturn_days: Optional[Decimal] = None
    arturn_days: Optional[Decimal] = None
    inv_turn: Optional[Decimal] = None
    ar_turn: Optional[Decimal] = None
    ca_turn: Optional[Decimal] = None
    fa_turn: Optional[Decimal] = None
    assets_turn: Optional[Decimal] = None
    turn_days: Optional[Decimal] = None
    total_fa_trun: Optional[Decimal] = None
    
    # 现金流指标
    op_income: Optional[Decimal] = None
    valuechange_income: Optional[Decimal] = None
    interst_income: Optional[Decimal] = None
    daa: Optional[Decimal] = None
    ebit: Optional[Decimal] = None
    ebitda: Optional[Decimal] = None
    fcff: Optional[Decimal] = None
    fcfe: Optional[Decimal] = None
    
    # 负债结构指标
    current_exint: Optional[Decimal] = None
    noncurrent_exint: Optional[Decimal] = None
    interestdebt: Optional[Decimal] = None
    netdebt: Optional[Decimal] = None
    tangible_asset: Optional[Decimal] = None
    working_capital: Optional[Decimal] = None
    networking_capital: Optional[Decimal] = None
    invest_capital: Optional[Decimal] = None
    retained_earnings: Optional[Decimal] = None
    
    # 每股指标(扩展)
    diluted2_eps: Optional[Decimal] = None
    bps: Optional[Decimal] = None
    ocfps: Optional[Decimal] = None
    retainedps: Optional[Decimal] = None
    cfps: Optional[Decimal] = None
    ebit_ps: Optional[Decimal] = None
    fcff_ps: Optional[Decimal] = None
    fcfe_ps: Optional[Decimal] = None
    
    # 收益率指标
    roe: Optional[Decimal] = None
    roe_waa: Optional[Decimal] = None
    roe_dt: Optional[Decimal] = None
    roa: Optional[Decimal] = None
    npta: Optional[Decimal] = None
    roic: Optional[Decimal] = None
    roe_yearly: Optional[Decimal] = None
    roa_yearly: Optional[Decimal] = None
    roa_dp: Optional[Decimal] = None
    roe_avg: Optional[Decimal] = None
    
    # 利润构成指标
    opincome_of_ebt: Optional[Decimal] = None
    investincome_of_ebt: Optional[Decimal] = None
    n_op_profit_of_ebt: Optional[Decimal] = None
    tax_to_ebt: Optional[Decimal] = None
    dtprofit_to_profit: Optional[Decimal] = None
    
    # 现金流构成指标
    salescash_to_or: Optional[Decimal] = None
    ocf_to_or: Optional[Decimal] = None
    ocf_to_opincome: Optional[Decimal] = None
    capitalized_to_da: Optional[Decimal] = None
    
    # 资产构成指标
    ca_to_assets: Optional[Decimal] = None
    nca_to_assets: Optional[Decimal] = None
    tbassets_to_totalassets: Optional[Decimal] = None
    int_to_talcap: Optional[Decimal] = None
    eqt_to_talcapital: Optional[Decimal] = None
    
    # 负债构成指标
    currentdebt_to_debt: Optional[Decimal] = None
    longdeb_to_debt: Optional[Decimal] = None
    ocf_to_shortdebt: Optional[Decimal] = None
    eqt_to_interestdebt: Optional[Decimal] = None
    tangibleasset_to_debt: Optional[Decimal] = None
    tangasset_to_intdebt: Optional[Decimal] = None
    tangibleasset_to_netdebt: Optional[Decimal] = None
    ocf_to_debt: Optional[Decimal] = None
    ocf_to_interestdebt: Optional[Decimal] = None
    ocf_to_netdebt: Optional[Decimal] = None
    
    # 偿债能力指标(扩展)
    ebit_to_interest: Optional[Decimal] = None
    longdebt_to_workingcapital: Optional[Decimal] = None
    ebitda_to_debt: Optional[Decimal] = None
    
    # 营运资产相关
    fixed_assets: Optional[Decimal] = None
    profit_prefin_exp: Optional[Decimal] = None
    non_op_profit: Optional[Decimal] = None
    op_to_ebt: Optional[Decimal] = None
    nop_to_ebt: Optional[Decimal] = None
    ocf_to_profit: Optional[Decimal] = None
    cash_to_liqdebt: Optional[Decimal] = None
    cash_to_liqdebt_withinterest: Optional[Decimal] = None
    op_to_liqdebt: Optional[Decimal] = None
    op_to_debt: Optional[Decimal] = None
    roic_yearly: Optional[Decimal] = None
    profit_to_op: Optional[Decimal] = None
    
    # 单季度指标
    q_opincome: Optional[Decimal] = None
    q_investincome: Optional[Decimal] = None
    q_dtprofit: Optional[Decimal] = None
    q_eps: Optional[Decimal] = None
    q_netprofit_margin: Optional[Decimal] = None
    q_gsprofit_margin: Optional[Decimal] = None
    q_exp_to_sales: Optional[Decimal] = None
    q_profit_to_gr: Optional[Decimal] = None
    q_saleexp_to_gr: Optional[Decimal] = None
    q_adminexp_to_gr: Optional[Decimal] = None
    q_finaexp_to_gr: Optional[Decimal] = None
    q_impair_to_gr_ttm: Optional[Decimal] = None
    q_gc_to_gr: Optional[Decimal] = None
    q_op_to_gr: Optional[Decimal] = None
    q_roe: Optional[Decimal] = None
    q_dt_roe: Optional[Decimal] = None
    q_npta: Optional[Decimal] = None
    q_opincome_to_ebt: Optional[Decimal] = None
    q_investincome_to_ebt: Optional[Decimal] = None
    q_dtprofit_to_profit: Optional[Decimal] = None
    q_salescash_to_or: Optional[Decimal] = None
    q_ocf_to_sales: Optional[Decimal] = None
    q_ocf_to_or: Optional[Decimal] = None
    
    # 同比增长指标
    basic_eps_yoy: Optional[Decimal] = None
    dt_eps_yoy: Optional[Decimal] = None
    cfps_yoy: Optional[Decimal] = None
    op_yoy: Optional[Decimal] = None
    ebt_yoy: Optional[Decimal] = None
    netprofit_yoy: Optional[Decimal] = None
    dt_netprofit_yoy: Optional[Decimal] = None
    ocf_yoy: Optional[Decimal] = None
    roe_yoy: Optional[Decimal] = None
    bps_yoy: Optional[Decimal] = None
    assets_yoy: Optional[Decimal] = None
    eqt_yoy: Optional[Decimal] = None
    tr_yoy: Optional[Decimal] = None
    or_yoy: Optional[Decimal] = None
    
    # 单季度同比环比指标
    q_gr_yoy: Optional[Decimal] = None
    q_gr_qoq: Optional[Decimal] = None
    q_sales_yoy: Optional[Decimal] = None
    q_sales_qoq: Optional[Decimal] = None
    q_op_yoy: Optional[Decimal] = None
    q_op_qoq: Optional[Decimal] = None
    q_profit_yoy: Optional[Decimal] = None
    q_profit_qoq: Optional[Decimal] = None
    q_netprofit_yoy: Optional[Decimal] = None
    q_netprofit_qoq: Optional[Decimal] = None
    
    # 其他指标
    equity_yoy: Optional[Decimal] = None
    rd_exp: Optional[Decimal] = None
    
    # 更新标识
    update_flag: Optional[str] = None

    @field_validator('ann_date', 'end_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('eps', 'dt_eps', 'total_revenue_ps', 'revenue_ps', 'capital_rese_ps', 'surplus_rese_ps', 
                   'undist_profit_ps', 'extra_item', 'profit_dedt', 'gross_margin', 'current_ratio', 'quick_ratio', 
                   'cash_ratio', 'invturn_days', 'arturn_days', 'inv_turn', 'ar_turn', 'ca_turn', 'fa_turn', 
                   'assets_turn', 'op_income', 'valuechange_income', 'interst_income', 'daa', 'ebit', 'ebitda', 
                   'fcff', 'fcfe', 'current_exint', 'noncurrent_exint', 'interestdebt', 'netdebt', 'tangible_asset', 
                   'working_capital', 'networking_capital', 'invest_capital', 'retained_earnings', 'diluted2_eps', 
                   'bps', 'ocfps', 'retainedps', 'cfps', 'ebit_ps', 'fcff_ps', 'fcfe_ps', 'netprofit_margin', 
                   'grossprofit_margin', 'cogs_of_sales', 'expense_of_sales', 'profit_to_gr', 'saleexp_to_gr', 
                   'adminexp_of_gr', 'finaexp_of_gr', 'impai_ttm', 'gc_of_gr', 'op_of_gr', 'ebit_of_gr', 'roe', 
                   'roe_waa', 'roe_dt', 'roa', 'npta', 'roic', 'roe_yearly', 'roa_yearly', 'roa_dp', 'roe_avg', 
                   'opincome_of_ebt', 'investincome_of_ebt', 'n_op_profit_of_ebt', 'tax_to_ebt', 'dtprofit_to_profit', 
                   'salescash_to_or', 'ocf_to_or', 'ocf_to_opincome', 'capitalized_to_da', 'ca_to_assets', 
                   'nca_to_assets', 'tbassets_to_totalassets', 'int_to_talcap', 'eqt_to_talcapital', 
                   'currentdebt_to_debt', 'longdeb_to_debt', 'ocf_to_shortdebt', 'eqt_to_interestdebt', 
                   'tangibleasset_to_debt', 'tangasset_to_intdebt', 'tangibleasset_to_netdebt', 'ocf_to_debt', 
                   'ocf_to_interestdebt', 'ocf_to_netdebt', 'ebit_to_interest', 'longdebt_to_workingcapital', 
                   'ebitda_to_debt', 'fixed_assets', 'profit_prefin_exp', 'non_op_profit', 'op_to_ebt', 
                   'nop_to_ebt', 'ocf_to_profit', 'cash_to_liqdebt', 'cash_to_liqdebt_withinterest', 
                   'op_to_liqdebt', 'op_to_debt', 'roic_yearly', 'profit_to_op', 'q_opincome', 'q_investincome', 
                   'q_dtprofit', 'q_eps', 'q_netprofit_margin', 'q_gsprofit_margin', 'q_exp_to_sales', 
                   'q_profit_to_gr', 'q_saleexp_to_gr', 'q_adminexp_to_gr', 'q_finaexp_to_gr', 'q_impair_to_gr_ttm', 
                   'q_gc_to_gr', 'q_op_to_gr', 'q_roe', 'q_dt_roe', 'q_npta', 'q_opincome_to_ebt', 
                   'q_investincome_to_ebt', 'q_dtprofit_to_profit', 'q_salescash_to_or', 'q_ocf_to_sales', 
                   'q_ocf_to_or', 'basic_eps_yoy', 'dt_eps_yoy', 'cfps_yoy', 'op_yoy', 'ebt_yoy', 'netprofit_yoy', 
                   'dt_netprofit_yoy', 'ocf_yoy', 'roe_yoy', 'bps_yoy', 'assets_yoy', 'eqt_yoy', 'tr_yoy', 'or_yoy', 
                   'q_gr_yoy', 'q_gr_qoq', 'q_sales_yoy', 'q_sales_qoq', 'q_op_yoy', 'q_op_qoq', 'q_profit_yoy', 
                   'q_profit_qoq', 'q_netprofit_yoy', 'q_netprofit_qoq', 'equity_yoy', 'rd_exp', 'debt_to_assets', 
                   'assets_to_eqt', 'dp_assets_to_eqt', 'debt_to_eqt', 'eqt_to_debt', 'turn_days', 'total_fa_trun', 
                   mode='before')
    def parse_numeric(cls, value):
        # 使用通用工具类进行数值验证
        return NumericValidators.to_decimal(value)
    
    class Config:
        from_attributes = True