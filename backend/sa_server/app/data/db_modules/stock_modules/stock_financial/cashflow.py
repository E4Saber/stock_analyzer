import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class CashflowData(BaseModel):
    """
    Pydantic model for cash flow statement data.
    
    Fields:
    - id: 主键ID
    - ts_code: TS代码
    - ann_date: 公告日期
    - f_ann_date: 实际公告日期
    - end_date: 报告期
    - comp_type: 公司类型(1一般工商业2银行3保险4证券)
    - report_type: 报告类型
    - end_type: 报告期类型
    - ...多个现金流量表指标字段
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
    # 公司类型
    comp_type: Optional[str] = None
    # 报告类型
    report_type: Optional[str] = None
    # 报告期类型
    end_type: Optional[str] = None
    
    # 利润相关数据
    net_profit: Optional[Decimal] = None
    finan_exp: Optional[Decimal] = None
    
    # 经营活动现金流入
    c_fr_sale_sg: Optional[Decimal] = None
    recp_tax_rends: Optional[Decimal] = None
    n_depos_incr_fi: Optional[Decimal] = None
    n_incr_loans_cb: Optional[Decimal] = None
    n_inc_borr_oth_fi: Optional[Decimal] = None
    prem_fr_orig_contr: Optional[Decimal] = None
    n_incr_insured_dep: Optional[Decimal] = None
    n_reinsur_prem: Optional[Decimal] = None
    n_incr_disp_tfa: Optional[Decimal] = None
    ifc_cash_incr: Optional[Decimal] = None
    n_incr_disp_faas: Optional[Decimal] = None
    n_incr_loans_oth_bank: Optional[Decimal] = None
    n_cap_incr_repur: Optional[Decimal] = None
    c_fr_oth_operate_a: Optional[Decimal] = None
    c_inf_fr_operate_a: Optional[Decimal] = None
    
    # 经营活动现金流出
    c_paid_goods_s: Optional[Decimal] = None
    c_paid_to_for_empl: Optional[Decimal] = None
    c_paid_for_taxes: Optional[Decimal] = None
    n_incr_clt_loan_adv: Optional[Decimal] = None
    n_incr_dep_cbob: Optional[Decimal] = None
    c_pay_claims_orig_inco: Optional[Decimal] = None
    pay_handling_chrg: Optional[Decimal] = None
    pay_comm_insur_plcy: Optional[Decimal] = None
    oth_cash_pay_oper_act: Optional[Decimal] = None
    st_cash_out_act: Optional[Decimal] = None
    
    # 经营活动现金流量净额
    n_cashflow_act: Optional[Decimal] = None
    
    # 投资活动现金流入
    oth_recp_ral_inv_act: Optional[Decimal] = None
    c_disp_withdrwl_invest: Optional[Decimal] = None
    c_recp_return_invest: Optional[Decimal] = None
    n_recp_disp_fiolta: Optional[Decimal] = None
    n_recp_disp_sobu: Optional[Decimal] = None
    stot_inflows_inv_act: Optional[Decimal] = None
    
    # 投资活动现金流出
    c_pay_acq_const_fiolta: Optional[Decimal] = None
    c_paid_invest: Optional[Decimal] = None
    n_disp_subs_oth_biz: Optional[Decimal] = None
    oth_pay_ral_inv_act: Optional[Decimal] = None
    n_incr_pledge_loan: Optional[Decimal] = None
    stot_out_inv_act: Optional[Decimal] = None
    
    # 投资活动现金流量净额
    n_cashflow_inv_act: Optional[Decimal] = None
    
    # 筹资活动现金流入
    c_recp_borrow: Optional[Decimal] = None
    proc_issue_bonds: Optional[Decimal] = None
    oth_cash_recp_ral_fnc_act: Optional[Decimal] = None
    stot_cash_in_fnc_act: Optional[Decimal] = None
    
    # 企业自由现金流
    free_cashflow: Optional[Decimal] = None
    
    # 筹资活动现金流出
    c_prepay_amt_borr: Optional[Decimal] = None
    c_pay_dist_dpcp_int_exp: Optional[Decimal] = None
    incl_dvd_profit_paid_sc_ms: Optional[Decimal] = None
    oth_cashpay_ral_fnc_act: Optional[Decimal] = None
    stot_cashout_fnc_act: Optional[Decimal] = None
    
    # 筹资活动现金流量净额
    n_cash_flows_fnc_act: Optional[Decimal] = None
    
    # 现金及现金等价物
    eff_fx_flu_cash: Optional[Decimal] = None
    n_incr_cash_cash_equ: Optional[Decimal] = None
    c_cash_equ_beg_period: Optional[Decimal] = None
    c_cash_equ_end_period: Optional[Decimal] = None
    
    # 其他筹资信息
    c_recp_cap_contrib: Optional[Decimal] = None
    incl_cash_rec_saims: Optional[Decimal] = None
    
    # 间接法计算现金流量的调整项目
    uncon_invest_loss: Optional[Decimal] = None
    prov_depr_assets: Optional[Decimal] = None
    depr_fa_coga_dpba: Optional[Decimal] = None
    amort_intang_assets: Optional[Decimal] = None
    lt_amort_deferred_exp: Optional[Decimal] = None
    decr_deferred_exp: Optional[Decimal] = None
    incr_acc_exp: Optional[Decimal] = None
    loss_disp_fiolta: Optional[Decimal] = None
    loss_scr_fa: Optional[Decimal] = None
    loss_fv_chg: Optional[Decimal] = None
    invest_loss: Optional[Decimal] = None
    decr_def_inc_tax_assets: Optional[Decimal] = None
    incr_def_inc_tax_liab: Optional[Decimal] = None
    decr_inventories: Optional[Decimal] = None
    decr_oper_payable: Optional[Decimal] = None
    incr_oper_payable: Optional[Decimal] = None
    others: Optional[Decimal] = None
    
    # 间接法计算的现金流量
    im_net_cashflow_oper_act: Optional[Decimal] = None
    
    # 不涉及现金收支的投资和筹资活动
    conv_debt_into_cap: Optional[Decimal] = None
    conv_copbonds_due_within_1y: Optional[Decimal] = None
    fa_fnc_leases: Optional[Decimal] = None
    
    # 间接法计算的现金净增加额
    im_n_incr_cash_equ: Optional[Decimal] = None
    
    # 其他现金流相关科目
    net_dism_capital_add: Optional[Decimal] = None
    net_cash_rece_sec: Optional[Decimal] = None
    credit_impa_loss: Optional[Decimal] = None
    use_right_asset_dep: Optional[Decimal] = None
    oth_loss_asset: Optional[Decimal] = None
    
    # 现金和现金等价物的期初期末余额
    end_bal_cash: Optional[Decimal] = None
    beg_bal_cash: Optional[Decimal] = None
    end_bal_cash_equ: Optional[Decimal] = None
    beg_bal_cash_equ: Optional[Decimal] = None
    
    # 元数据
    update_flag: Optional[str] = None

    @field_validator('ann_date', 'f_ann_date', 'end_date', mode='before')
    def parse_date(cls, value):
        # 使用通用工具类进行日期验证
        date_obj = DateValidators.to_date(value)
        if date_obj is None and value is not None and value != '':
            raise ValueError(f"无效的日期格式: {value}")
        return date_obj

    # 创建一个处理所有数值字段的验证器
    @field_validator(
        'net_profit', 'finan_exp', 'c_fr_sale_sg', 'recp_tax_rends', 'n_depos_incr_fi', 
        'n_incr_loans_cb', 'n_inc_borr_oth_fi', 'prem_fr_orig_contr', 'n_incr_insured_dep', 
        'n_reinsur_prem', 'n_incr_disp_tfa', 'ifc_cash_incr', 'n_incr_disp_faas', 
        'n_incr_loans_oth_bank', 'n_cap_incr_repur', 'c_fr_oth_operate_a', 'c_inf_fr_operate_a', 
        'c_paid_goods_s', 'c_paid_to_for_empl', 'c_paid_for_taxes', 'n_incr_clt_loan_adv', 
        'n_incr_dep_cbob', 'c_pay_claims_orig_inco', 'pay_handling_chrg', 'pay_comm_insur_plcy', 
        'oth_cash_pay_oper_act', 'st_cash_out_act', 'n_cashflow_act', 'oth_recp_ral_inv_act', 
        'c_disp_withdrwl_invest', 'c_recp_return_invest', 'n_recp_disp_fiolta', 'n_recp_disp_sobu', 
        'stot_inflows_inv_act', 'c_pay_acq_const_fiolta', 'c_paid_invest', 'n_disp_subs_oth_biz', 
        'oth_pay_ral_inv_act', 'n_incr_pledge_loan', 'stot_out_inv_act', 'n_cashflow_inv_act', 
        'c_recp_borrow', 'proc_issue_bonds', 'oth_cash_recp_ral_fnc_act', 'stot_cash_in_fnc_act', 
        'free_cashflow', 'c_prepay_amt_borr', 'c_pay_dist_dpcp_int_exp', 'incl_dvd_profit_paid_sc_ms', 
        'oth_cashpay_ral_fnc_act', 'stot_cashout_fnc_act', 'n_cash_flows_fnc_act', 'eff_fx_flu_cash', 
        'n_incr_cash_cash_equ', 'c_cash_equ_beg_period', 'c_cash_equ_end_period', 'c_recp_cap_contrib', 
        'incl_cash_rec_saims', 'uncon_invest_loss', 'prov_depr_assets', 'depr_fa_coga_dpba', 
        'amort_intang_assets', 'lt_amort_deferred_exp', 'decr_deferred_exp', 'incr_acc_exp', 
        'loss_disp_fiolta', 'loss_scr_fa', 'loss_fv_chg', 'invest_loss', 'decr_def_inc_tax_assets', 
        'incr_def_inc_tax_liab', 'decr_inventories', 'decr_oper_payable', 'incr_oper_payable', 
        'others', 'im_net_cashflow_oper_act', 'conv_debt_into_cap', 'conv_copbonds_due_within_1y', 
        'fa_fnc_leases', 'im_n_incr_cash_equ', 'net_dism_capital_add', 'net_cash_rece_sec', 
        'credit_impa_loss', 'use_right_asset_dep', 'oth_loss_asset', 'end_bal_cash', 
        'beg_bal_cash', 'end_bal_cash_equ', 'beg_bal_cash_equ',
        mode='before'
    )
    def parse_numeric(cls, value):
        # 使用通用工具类进行数值验证
        return NumericValidators.to_decimal(value)
    
    class Config:
        from_attributes = True