import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from pydantic import field_validator
from app.utils.date_validators import DateValidators
from app.utils.numeric_validators import NumericValidators


class BalancesheetData(BaseModel):
    """
    Pydantic model for balance sheet data.
    
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
    
    # 股本与储备
    total_share: Optional[Decimal] = None
    cap_rese: Optional[Decimal] = None
    undistr_porfit: Optional[Decimal] = None
    surplus_rese: Optional[Decimal] = None
    special_rese: Optional[Decimal] = None
    
    # 流动资产
    money_cap: Optional[Decimal] = None
    trad_asset: Optional[Decimal] = None
    notes_receiv: Optional[Decimal] = None
    accounts_receiv: Optional[Decimal] = None
    oth_receiv: Optional[Decimal] = None
    prepayment: Optional[Decimal] = None
    div_receiv: Optional[Decimal] = None
    int_receiv: Optional[Decimal] = None
    inventories: Optional[Decimal] = None
    amor_exp: Optional[Decimal] = None
    nca_within_1y: Optional[Decimal] = None
    sett_rsrv: Optional[Decimal] = None
    loanto_oth_bank_fi: Optional[Decimal] = None
    premium_receiv: Optional[Decimal] = None
    reinsur_receiv: Optional[Decimal] = None
    reinsur_res_receiv: Optional[Decimal] = None
    pur_resale_fa: Optional[Decimal] = None
    oth_cur_assets: Optional[Decimal] = None
    total_cur_assets: Optional[Decimal] = None
    
    # 非流动资产
    fa_avail_for_sale: Optional[Decimal] = None
    htm_invest: Optional[Decimal] = None
    lt_eqt_invest: Optional[Decimal] = None
    invest_real_estate: Optional[Decimal] = None
    time_deposits: Optional[Decimal] = None
    oth_assets: Optional[Decimal] = None
    lt_rec: Optional[Decimal] = None
    fix_assets: Optional[Decimal] = None
    cip: Optional[Decimal] = None
    const_materials: Optional[Decimal] = None
    fixed_assets_disp: Optional[Decimal] = None
    produc_bio_assets: Optional[Decimal] = None
    oil_and_gas_assets: Optional[Decimal] = None
    intan_assets: Optional[Decimal] = None
    r_and_d: Optional[Decimal] = None
    goodwill: Optional[Decimal] = None
    lt_amor_exp: Optional[Decimal] = None
    defer_tax_assets: Optional[Decimal] = None
    decr_in_disbur: Optional[Decimal] = None
    oth_nca: Optional[Decimal] = None
    total_nca: Optional[Decimal] = None
    
    # 特殊金融机构资产项目
    cash_reser_cb: Optional[Decimal] = None
    depos_in_oth_bfi: Optional[Decimal] = None
    prec_metals: Optional[Decimal] = None
    deriv_assets: Optional[Decimal] = None
    rr_reins_une_prem: Optional[Decimal] = None
    rr_reins_outstd_cla: Optional[Decimal] = None
    rr_reins_lins_liab: Optional[Decimal] = None
    rr_reins_lthins_liab: Optional[Decimal] = None
    refund_depos: Optional[Decimal] = None
    ph_pledge_loans: Optional[Decimal] = None
    refund_cap_depos: Optional[Decimal] = None
    indep_acct_assets: Optional[Decimal] = None
    client_depos: Optional[Decimal] = None
    client_prov: Optional[Decimal] = None
    transac_seat_fee: Optional[Decimal] = None
    invest_as_receiv: Optional[Decimal] = None
    
    # 资产总计
    total_assets: Optional[Decimal] = None
    
    # 流动负债
    lt_borr: Optional[Decimal] = None
    st_borr: Optional[Decimal] = None
    cb_borr: Optional[Decimal] = None
    depos_ib_deposits: Optional[Decimal] = None
    loan_oth_bank: Optional[Decimal] = None
    trading_fl: Optional[Decimal] = None
    notes_payable: Optional[Decimal] = None
    acct_payable: Optional[Decimal] = None
    adv_receipts: Optional[Decimal] = None
    sold_for_repur_fa: Optional[Decimal] = None
    comm_payable: Optional[Decimal] = None
    payroll_payable: Optional[Decimal] = None
    taxes_payable: Optional[Decimal] = None
    int_payable: Optional[Decimal] = None
    div_payable: Optional[Decimal] = None
    oth_payable: Optional[Decimal] = None
    acc_exp: Optional[Decimal] = None
    deferred_inc: Optional[Decimal] = None
    st_bonds_payable: Optional[Decimal] = None
    payable_to_reinsurer: Optional[Decimal] = None
    rsrv_insur_cont: Optional[Decimal] = None
    acting_trading_sec: Optional[Decimal] = None
    acting_uw_sec: Optional[Decimal] = None
    non_cur_liab_due_1y: Optional[Decimal] = None
    oth_cur_liab: Optional[Decimal] = None
    total_cur_liab: Optional[Decimal] = None
    
    # 非流动负债
    bond_payable: Optional[Decimal] = None
    lt_payable: Optional[Decimal] = None
    specific_payables: Optional[Decimal] = None
    estimated_liab: Optional[Decimal] = None
    defer_tax_liab: Optional[Decimal] = None
    defer_inc_non_cur_liab: Optional[Decimal] = None
    oth_ncl: Optional[Decimal] = None
    total_ncl: Optional[Decimal] = None
    
    # 特殊金融机构负债项目
    depos_oth_bfi: Optional[Decimal] = None
    deriv_liab: Optional[Decimal] = None
    depos: Optional[Decimal] = None
    agency_bus_liab: Optional[Decimal] = None
    oth_liab: Optional[Decimal] = None
    prem_receiv_adva: Optional[Decimal] = None
    depos_received: Optional[Decimal] = None
    ph_invest: Optional[Decimal] = None
    reser_une_prem: Optional[Decimal] = None
    reser_outstd_claims: Optional[Decimal] = None
    reser_lins_liab: Optional[Decimal] = None
    reser_lthins_liab: Optional[Decimal] = None
    indept_acc_liab: Optional[Decimal] = None
    pledge_borr: Optional[Decimal] = None
    indem_payable: Optional[Decimal] = None
    policy_div_payable: Optional[Decimal] = None
    
    # 负债合计
    total_liab: Optional[Decimal] = None
    
    # 股东权益
    treasury_share: Optional[Decimal] = None
    ordin_risk_reser: Optional[Decimal] = None
    forex_differ: Optional[Decimal] = None
    invest_loss_unconf: Optional[Decimal] = None
    minority_int: Optional[Decimal] = None
    total_hldr_eqy_exc_min_int: Optional[Decimal] = None
    total_hldr_eqy_inc_min_int: Optional[Decimal] = None
    total_liab_hldr_eqy: Optional[Decimal] = None
    
    # 其他权益和负债项目
    lt_payroll_payable: Optional[Decimal] = None
    oth_comp_income: Optional[Decimal] = None
    oth_eqt_tools: Optional[Decimal] = None
    oth_eqt_tools_p_shr: Optional[Decimal] = None
    lending_funds: Optional[Decimal] = None
    acc_receivable: Optional[Decimal] = None
    st_fin_payable: Optional[Decimal] = None
    payables: Optional[Decimal] = None
    hfs_assets: Optional[Decimal] = None
    hfs_sales: Optional[Decimal] = None
    
    # 新金融工具准则相关科目
    cost_fin_assets: Optional[Decimal] = None
    fair_value_fin_assets: Optional[Decimal] = None
    cip_total: Optional[Decimal] = None
    oth_pay_total: Optional[Decimal] = None
    long_pay_total: Optional[Decimal] = None
    debt_invest: Optional[Decimal] = None
    oth_debt_invest: Optional[Decimal] = None
    oth_eq_invest: Optional[Decimal] = None
    oth_illiq_fin_assets: Optional[Decimal] = None
    oth_eq_ppbond: Optional[Decimal] = None
    
    # 新收入准则相关科目
    receiv_financing: Optional[Decimal] = None
    use_right_assets: Optional[Decimal] = None
    lease_liab: Optional[Decimal] = None
    contract_assets: Optional[Decimal] = None
    contract_liab: Optional[Decimal] = None
    
    # 合计项目
    accounts_receiv_bill: Optional[Decimal] = None
    accounts_pay: Optional[Decimal] = None
    oth_rcv_total: Optional[Decimal] = None
    fix_assets_total: Optional[Decimal] = None
    
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
    # 由于字段太多，我们使用一个通用的验证器函数来处理所有数值字段
    @field_validator(
        'total_share', 'cap_rese', 'undistr_porfit', 'surplus_rese', 'special_rese',
        'money_cap', 'trad_asset', 'notes_receiv', 'accounts_receiv', 'oth_receiv',
        'prepayment', 'div_receiv', 'int_receiv', 'inventories', 'amor_exp',
        'nca_within_1y', 'sett_rsrv', 'loanto_oth_bank_fi', 'premium_receiv',
        'reinsur_receiv', 'reinsur_res_receiv', 'pur_resale_fa', 'oth_cur_assets',
        'total_cur_assets', 'fa_avail_for_sale', 'htm_invest', 'lt_eqt_invest',
        'invest_real_estate', 'time_deposits', 'oth_assets', 'lt_rec', 'fix_assets',
        'cip', 'const_materials', 'fixed_assets_disp', 'produc_bio_assets',
        'oil_and_gas_assets', 'intan_assets', 'r_and_d', 'goodwill', 'lt_amor_exp',
        'defer_tax_assets', 'decr_in_disbur', 'oth_nca', 'total_nca', 'cash_reser_cb',
        'depos_in_oth_bfi', 'prec_metals', 'deriv_assets', 'rr_reins_une_prem',
        'rr_reins_outstd_cla', 'rr_reins_lins_liab', 'rr_reins_lthins_liab',
        'refund_depos', 'ph_pledge_loans', 'refund_cap_depos', 'indep_acct_assets',
        'client_depos', 'client_prov', 'transac_seat_fee', 'invest_as_receiv',
        'total_assets', 'lt_borr', 'st_borr', 'cb_borr', 'depos_ib_deposits',
        'loan_oth_bank', 'trading_fl', 'notes_payable', 'acct_payable', 'adv_receipts',
        'sold_for_repur_fa', 'comm_payable', 'payroll_payable', 'taxes_payable',
        'int_payable', 'div_payable', 'oth_payable', 'acc_exp', 'deferred_inc',
        'st_bonds_payable', 'payable_to_reinsurer', 'rsrv_insur_cont',
        'acting_trading_sec', 'acting_uw_sec', 'non_cur_liab_due_1y', 'oth_cur_liab',
        'total_cur_liab', 'bond_payable', 'lt_payable', 'specific_payables',
        'estimated_liab', 'defer_tax_liab', 'defer_inc_non_cur_liab', 'oth_ncl',
        'total_ncl', 'depos_oth_bfi', 'deriv_liab', 'depos', 'agency_bus_liab',
        'oth_liab', 'prem_receiv_adva', 'depos_received', 'ph_invest', 'reser_une_prem',
        'reser_outstd_claims', 'reser_lins_liab', 'reser_lthins_liab', 'indept_acc_liab',
        'pledge_borr', 'indem_payable', 'policy_div_payable', 'total_liab',
        'treasury_share', 'ordin_risk_reser', 'forex_differ', 'invest_loss_unconf',
        'minority_int', 'total_hldr_eqy_exc_min_int', 'total_hldr_eqy_inc_min_int',
        'total_liab_hldr_eqy', 'lt_payroll_payable', 'oth_comp_income', 'oth_eqt_tools',
        'oth_eqt_tools_p_shr', 'lending_funds', 'acc_receivable', 'st_fin_payable',
        'payables', 'hfs_assets', 'hfs_sales', 'cost_fin_assets', 'fair_value_fin_assets',
        'cip_total', 'oth_pay_total', 'long_pay_total', 'debt_invest', 'oth_debt_invest',
        'oth_eq_invest', 'oth_illiq_fin_assets', 'oth_eq_ppbond', 'receiv_financing',
        'use_right_assets', 'lease_liab', 'contract_assets', 'contract_liab',
        'accounts_receiv_bill', 'accounts_pay', 'oth_rcv_total', 'fix_assets_total',
        mode='before'
    )
    def parse_numeric(cls, value):
        # 使用通用工具类进行数值验证
        return NumericValidators.to_decimal(value)
    
    class Config:
        from_attributes = True