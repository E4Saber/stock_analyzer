import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class IncomeData(BaseModel):
    """
    Pydantic model for income statement data.
    
    Fields:
    - id: 主键ID
    - ts_code: TS代码
    - ann_date: 公告日期
    - f_ann_date: 实际公告日期
    - end_date: 报告期
    - report_type: 报告类型
    - comp_type: 公司类型(1一般工商业2银行3保险4证券)
    - end_type: 报告期类型
    - ...多个财务指标字段
    """
    # ID主键，自动生成
    id: Optional[int] = None
    # TS代码，唯一标识
    ts_code: str
    # 公告日期
    ann_date: Optional[datetime.date] = None
    # 实际公告日期
    f_ann_date: Optional[datetime.date] = None
    # 报告期
    end_date: Optional[datetime.date] = None
    # 报告类型
    report_type: Optional[str] = None
    # 公司类型
    comp_type: Optional[str] = None
    # 报告期类型
    end_type: Optional[str] = None
    
    # 核心财务指标
    basic_eps: Optional[Decimal] = None
    diluted_eps: Optional[Decimal] = None
    
    # 收入相关字段
    total_revenue: Optional[Decimal] = None
    revenue: Optional[Decimal] = None
    int_income: Optional[Decimal] = None
    prem_earned: Optional[Decimal] = None
    comm_income: Optional[Decimal] = None
    n_commis_income: Optional[Decimal] = None
    n_oth_income: Optional[Decimal] = None
    n_oth_b_income: Optional[Decimal] = None
    prem_income: Optional[Decimal] = None
    out_prem: Optional[Decimal] = None
    une_prem_reser: Optional[Decimal] = None
    reins_income: Optional[Decimal] = None
    n_sec_tb_income: Optional[Decimal] = None
    n_sec_uw_income: Optional[Decimal] = None
    n_asset_mg_income: Optional[Decimal] = None
    oth_b_income: Optional[Decimal] = None
    
    # 投资和估值相关字段
    fv_value_chg_gain: Optional[Decimal] = None
    invest_income: Optional[Decimal] = None
    ass_invest_income: Optional[Decimal] = None
    forex_gain: Optional[Decimal] = None
    
    # 成本相关字段
    total_cogs: Optional[Decimal] = None
    oper_cost: Optional[Decimal] = None
    int_exp: Optional[Decimal] = None
    comm_exp: Optional[Decimal] = None
    biz_tax_surchg: Optional[Decimal] = None
    sell_exp: Optional[Decimal] = None
    admin_exp: Optional[Decimal] = None
    fin_exp: Optional[Decimal] = None
    assets_impair_loss: Optional[Decimal] = None
    
    # 保险相关字段
    prem_refund: Optional[Decimal] = None
    compens_payout: Optional[Decimal] = None
    reser_insur_liab: Optional[Decimal] = None
    div_payt: Optional[Decimal] = None
    reins_exp: Optional[Decimal] = None
    oper_exp: Optional[Decimal] = None
    compens_payout_refu: Optional[Decimal] = None
    insur_reser_refu: Optional[Decimal] = None
    reins_cost_refund: Optional[Decimal] = None
    other_bus_cost: Optional[Decimal] = None
    
    # 利润相关字段
    operate_profit: Optional[Decimal] = None
    non_oper_income: Optional[Decimal] = None
    non_oper_exp: Optional[Decimal] = None
    nca_disploss: Optional[Decimal] = None
    total_profit: Optional[Decimal] = None
    income_tax: Optional[Decimal] = None
    
    # 净收入字段
    n_income: Optional[Decimal] = None
    n_income_attr_p: Optional[Decimal] = None
    minority_gain: Optional[Decimal] = None
    
    # 综合收益字段
    oth_compr_income: Optional[Decimal] = None
    t_compr_income: Optional[Decimal] = None
    compr_inc_attr_p: Optional[Decimal] = None
    compr_inc_attr_m_s: Optional[Decimal] = None
    
    # EBIT和EBITDA
    ebit: Optional[Decimal] = None
    ebitda: Optional[Decimal] = None
    
    # 额外的保险和利润分配字段
    insurance_exp: Optional[Decimal] = None
    undist_profit: Optional[Decimal] = None
    distable_profit: Optional[Decimal] = None
    
    # 研发和利息字段
    rd_exp: Optional[Decimal] = None
    fin_exp_int_exp: Optional[Decimal] = None
    fin_exp_int_inc: Optional[Decimal] = None
    
    # 转移和调整
    transfer_surplus_rese: Optional[Decimal] = None
    transfer_housing_imprest: Optional[Decimal] = None
    transfer_oth: Optional[Decimal] = None
    adj_lossgain: Optional[Decimal] = None
    
    # 储备和基金
    withdra_legal_surplus: Optional[Decimal] = None
    withdra_legal_pubfund: Optional[Decimal] = None
    withdra_biz_devfund: Optional[Decimal] = None
    withdra_rese_fund: Optional[Decimal] = None
    withdra_oth_ersu: Optional[Decimal] = None
    
    # 员工和股东分配
    workers_welfare: Optional[Decimal] = None
    distr_profit_shrder: Optional[Decimal] = None
    prfshare_payable_dvd: Optional[Decimal] = None
    comshare_payable_dvd: Optional[Decimal] = None
    capit_comstock_div: Optional[Decimal] = None
    
    # 额外财务指标
    net_after_nr_lp_correct: Optional[Decimal] = None
    credit_impa_loss: Optional[Decimal] = None
    net_expo_hedging_benefits: Optional[Decimal] = None
    oth_impair_loss_assets: Optional[Decimal] = None
    total_opcost: Optional[Decimal] = None
    amodcost_fin_assets: Optional[Decimal] = None
    oth_income: Optional[Decimal] = None
    asset_disp_income: Optional[Decimal] = None
    continued_net_profit: Optional[Decimal] = None
    end_net_profit: Optional[Decimal] = None
    
    # 元数据
    update_flag: Optional[str] = None

    @field_validator('ann_date', 'f_ann_date', 'end_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    @field_validator('basic_eps', 'diluted_eps', 'total_revenue', 'revenue', 'int_income', 'prem_earned', 'comm_income', 'n_commis_income', 'n_oth_income', 'n_oth_b_income', 'prem_income', 'out_prem', 'une_prem_reser', 'reins_income', 'n_sec_tb_income', 'n_sec_uw_income', 'n_asset_mg_income', 'oth_b_income', 'fv_value_chg_gain', 'invest_income', 'ass_invest_income', 'forex_gain', 'total_cogs', 'oper_cost', 'int_exp', 'comm_exp', 'biz_tax_surchg', 'sell_exp', 'admin_exp', 'fin_exp', 'assets_impair_loss', 'prem_refund', 'compens_payout', 'reser_insur_liab', 'div_payt', 'reins_exp', 'oper_exp', 'compens_payout_refu', 'insur_reser_refu', 'reins_cost_refund', 'other_bus_cost', 'operate_profit', 'non_oper_income', 'non_oper_exp', 'nca_disploss', 'total_profit', 'income_tax', 'n_income', 'n_income_attr_p', 'minority_gain', 'oth_compr_income', 't_compr_income', 'compr_inc_attr_p', 'compr_inc_attr_m_s', 'ebit', 'ebitda', 'insurance_exp', 'undist_profit', 'distable_profit', 'rd_exp', 'fin_exp_int_exp', 'fin_exp_int_inc', 'transfer_surplus_rese', 'transfer_housing_imprest', 'transfer_oth', 'adj_lossgain', 'withdra_legal_surplus', 'withdra_legal_pubfund', 'withdra_biz_devfund', 'withdra_rese_fund', 'withdra_oth_ersu', 'workers_welfare', 'distr_profit_shrder', 'prfshare_payable_dvd', 'comshare_payable_dvd', 'capit_comstock_div', 'net_after_nr_lp_correct', 'credit_impa_loss', 'net_expo_hedging_benefits', 'oth_impair_loss_assets', 'total_opcost', 'amodcost_fin_assets', 'oth_income', 'asset_disp_income', 'continued_net_profit', 'end_net_profit', mode='before')
    def parse_numeric(cls, value):
        # 使用通用工具类进行数值验证
        return NumericValidators.to_decimal(value)
    
    class Config:
        from_attributes = True