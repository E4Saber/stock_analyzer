-- 股票数据 - 财务数据

-- 资产负债表（balancesheet）
CREATE TABLE balancesheet (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL,
    ann_date DATE,
    f_ann_date DATE,
    end_date DATE,
    report_type VARCHAR(10),
    comp_type CHAR(1),
    end_type VARCHAR(10),
    
    -- 股本与储备
    total_share NUMERIC(20,4),
    cap_rese NUMERIC(20,4),
    undistr_porfit NUMERIC(20,4),
    surplus_rese NUMERIC(20,4),
    special_rese NUMERIC(20,4),
    
    -- 流动资产
    money_cap NUMERIC(20,4),
    trad_asset NUMERIC(20,4),
    notes_receiv NUMERIC(20,4),
    accounts_receiv NUMERIC(20,4),
    oth_receiv NUMERIC(20,4),
    prepayment NUMERIC(20,4),
    div_receiv NUMERIC(20,4),
    int_receiv NUMERIC(20,4),
    inventories NUMERIC(20,4),
    amor_exp NUMERIC(20,4),
    nca_within_1y NUMERIC(20,4),
    sett_rsrv NUMERIC(20,4),
    loanto_oth_bank_fi NUMERIC(20,4),
    premium_receiv NUMERIC(20,4),
    reinsur_receiv NUMERIC(20,4),
    reinsur_res_receiv NUMERIC(20,4),
    pur_resale_fa NUMERIC(20,4),
    oth_cur_assets NUMERIC(20,4),
    total_cur_assets NUMERIC(20,4),
    
    -- 非流动资产
    fa_avail_for_sale NUMERIC(20,4),
    htm_invest NUMERIC(20,4),
    lt_eqt_invest NUMERIC(20,4),
    invest_real_estate NUMERIC(20,4),
    time_deposits NUMERIC(20,4),
    oth_assets NUMERIC(20,4),
    lt_rec NUMERIC(20,4),
    fix_assets NUMERIC(20,4),
    cip NUMERIC(20,4),
    const_materials NUMERIC(20,4),
    fixed_assets_disp NUMERIC(20,4),
    produc_bio_assets NUMERIC(20,4),
    oil_and_gas_assets NUMERIC(20,4),
    intan_assets NUMERIC(20,4),
    r_and_d NUMERIC(20,4),
    goodwill NUMERIC(20,4),
    lt_amor_exp NUMERIC(20,4),
    defer_tax_assets NUMERIC(20,4),
    decr_in_disbur NUMERIC(20,4),
    oth_nca NUMERIC(20,4),
    total_nca NUMERIC(20,4),
    
    -- 特殊金融机构资产项目
    cash_reser_cb NUMERIC(20,4),
    depos_in_oth_bfi NUMERIC(20,4),
    prec_metals NUMERIC(20,4),
    deriv_assets NUMERIC(20,4),
    rr_reins_une_prem NUMERIC(20,4),
    rr_reins_outstd_cla NUMERIC(20,4),
    rr_reins_lins_liab NUMERIC(20,4),
    rr_reins_lthins_liab NUMERIC(20,4),
    refund_depos NUMERIC(20,4),
    ph_pledge_loans NUMERIC(20,4),
    refund_cap_depos NUMERIC(20,4),
    indep_acct_assets NUMERIC(20,4),
    client_depos NUMERIC(20,4),
    client_prov NUMERIC(20,4),
    transac_seat_fee NUMERIC(20,4),
    invest_as_receiv NUMERIC(20,4),
    
    -- 资产总计
    total_assets NUMERIC(20,4),
    
    -- 流动负债
    lt_borr NUMERIC(20,4),
    st_borr NUMERIC(20,4),
    cb_borr NUMERIC(20,4),
    depos_ib_deposits NUMERIC(20,4),
    loan_oth_bank NUMERIC(20,4),
    trading_fl NUMERIC(20,4),
    notes_payable NUMERIC(20,4),
    acct_payable NUMERIC(20,4),
    adv_receipts NUMERIC(20,4),
    sold_for_repur_fa NUMERIC(20,4),
    comm_payable NUMERIC(20,4),
    payroll_payable NUMERIC(20,4),
    taxes_payable NUMERIC(20,4),
    int_payable NUMERIC(20,4),
    div_payable NUMERIC(20,4),
    oth_payable NUMERIC(20,4),
    acc_exp NUMERIC(20,4),
    deferred_inc NUMERIC(20,4),
    st_bonds_payable NUMERIC(20,4),
    payable_to_reinsurer NUMERIC(20,4),
    rsrv_insur_cont NUMERIC(20,4),
    acting_trading_sec NUMERIC(20,4),
    acting_uw_sec NUMERIC(20,4),
    non_cur_liab_due_1y NUMERIC(20,4),
    oth_cur_liab NUMERIC(20,4),
    total_cur_liab NUMERIC(20,4),
    
    -- 非流动负债
    bond_payable NUMERIC(20,4),
    lt_payable NUMERIC(20,4),
    specific_payables NUMERIC(20,4),
    estimated_liab NUMERIC(20,4),
    defer_tax_liab NUMERIC(20,4),
    defer_inc_non_cur_liab NUMERIC(20,4),
    oth_ncl NUMERIC(20,4),
    total_ncl NUMERIC(20,4),
    
    -- 特殊金融机构负债项目
    depos_oth_bfi NUMERIC(20,4),
    deriv_liab NUMERIC(20,4),
    depos NUMERIC(20,4),
    agency_bus_liab NUMERIC(20,4),
    oth_liab NUMERIC(20,4),
    prem_receiv_adva NUMERIC(20,4),
    depos_received NUMERIC(20,4),
    ph_invest NUMERIC(20,4),
    reser_une_prem NUMERIC(20,4),
    reser_outstd_claims NUMERIC(20,4),
    reser_lins_liab NUMERIC(20,4),
    reser_lthins_liab NUMERIC(20,4),
    indept_acc_liab NUMERIC(20,4),
    pledge_borr NUMERIC(20,4),
    indem_payable NUMERIC(20,4),
    policy_div_payable NUMERIC(20,4),
    
    -- 负债合计
    total_liab NUMERIC(20,4),
    
    -- 股东权益
    treasury_share NUMERIC(20,4),
    ordin_risk_reser NUMERIC(20,4),
    forex_differ NUMERIC(20,4),
    invest_loss_unconf NUMERIC(20,4),
    minority_int NUMERIC(20,4),
    total_hldr_eqy_exc_min_int NUMERIC(20,4),
    total_hldr_eqy_inc_min_int NUMERIC(20,4),
    total_liab_hldr_eqy NUMERIC(20,4),
    
    -- 其他权益和负债项目
    lt_payroll_payable NUMERIC(20,4),
    oth_comp_income NUMERIC(20,4),
    oth_eqt_tools NUMERIC(20,4),
    oth_eqt_tools_p_shr NUMERIC(20,4),
    lending_funds NUMERIC(20,4),
    acc_receivable NUMERIC(20,4),
    st_fin_payable NUMERIC(20,4),
    payables NUMERIC(20,4),
    hfs_assets NUMERIC(20,4),
    hfs_sales NUMERIC(20,4),
    
    -- 新金融工具准则相关科目
    cost_fin_assets NUMERIC(20,4),
    fair_value_fin_assets NUMERIC(20,4),
    cip_total NUMERIC(20,4),
    oth_pay_total NUMERIC(20,4),
    long_pay_total NUMERIC(20,4),
    debt_invest NUMERIC(20,4),
    oth_debt_invest NUMERIC(20,4),
    oth_eq_invest NUMERIC(20,4),
    oth_illiq_fin_assets NUMERIC(20,4),
    oth_eq_ppbond NUMERIC(20,4),
    
    -- 新收入准则相关科目
    receiv_financing NUMERIC(20,4),
    use_right_assets NUMERIC(20,4),
    lease_liab NUMERIC(20,4),
    contract_assets NUMERIC(20,4),
    contract_liab NUMERIC(20,4),
    
    -- 合计项目
    accounts_receiv_bill NUMERIC(20,4),
    accounts_pay NUMERIC(20,4),
    oth_rcv_total NUMERIC(20,4),
    fix_assets_total NUMERIC(20,4),
    
    -- 元数据
    update_flag VARCHAR(10)
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_balancesheet_ts_code ON balancesheet(ts_code);
CREATE INDEX idx_balancesheet_end_date ON balancesheet(end_date);
CREATE INDEX idx_balancesheet_report_type ON balancesheet(report_type);

-- Add unique constraint for upsert operations
ALTER TABLE balancesheet ADD CONSTRAINT balancesheet_ts_code_end_date_report_type_key 
UNIQUE (ts_code, end_date, report_type);

-- Add table comment
COMMENT ON TABLE balancesheet IS '资产负债表';

-- Add column comments
COMMENT ON COLUMN balancesheet.ts_code IS 'TS代码';
COMMENT ON COLUMN balancesheet.ann_date IS '公告日期';
COMMENT ON COLUMN balancesheet.f_ann_date IS '实际公告日期';
COMMENT ON COLUMN balancesheet.end_date IS '报告期';
COMMENT ON COLUMN balancesheet.report_type IS '报告类型';
COMMENT ON COLUMN balancesheet.comp_type IS '公司类型(1一般工商业2银行3保险4证券)';
COMMENT ON COLUMN balancesheet.end_type IS '报告期类型';
COMMENT ON COLUMN balancesheet.total_share IS '期末总股本';
COMMENT ON COLUMN balancesheet.cap_rese IS '资本公积金';
COMMENT ON COLUMN balancesheet.undistr_porfit IS '未分配利润';
COMMENT ON COLUMN balancesheet.surplus_rese IS '盈余公积金';
COMMENT ON COLUMN balancesheet.special_rese IS '专项储备';
COMMENT ON COLUMN balancesheet.money_cap IS '货币资金';
COMMENT ON COLUMN balancesheet.trad_asset IS '交易性金融资产';
COMMENT ON COLUMN balancesheet.notes_receiv IS '应收票据';
COMMENT ON COLUMN balancesheet.accounts_receiv IS '应收账款';
COMMENT ON COLUMN balancesheet.oth_receiv IS '其他应收款';
COMMENT ON COLUMN balancesheet.prepayment IS '预付款项';
COMMENT ON COLUMN balancesheet.div_receiv IS '应收股利';
COMMENT ON COLUMN balancesheet.int_receiv IS '应收利息';
COMMENT ON COLUMN balancesheet.inventories IS '存货';
COMMENT ON COLUMN balancesheet.amor_exp IS '待摊费用';
COMMENT ON COLUMN balancesheet.nca_within_1y IS '一年内到期的非流动资产';
COMMENT ON COLUMN balancesheet.sett_rsrv IS '结算备付金';
COMMENT ON COLUMN balancesheet.loanto_oth_bank_fi IS '拆出资金';
COMMENT ON COLUMN balancesheet.premium_receiv IS '应收保费';
COMMENT ON COLUMN balancesheet.reinsur_receiv IS '应收分保账款';
COMMENT ON COLUMN balancesheet.reinsur_res_receiv IS '应收分保合同准备金';
COMMENT ON COLUMN balancesheet.pur_resale_fa IS '买入返售金融资产';
COMMENT ON COLUMN balancesheet.oth_cur_assets IS '其他流动资产';
COMMENT ON COLUMN balancesheet.total_cur_assets IS '流动资产合计';
COMMENT ON COLUMN balancesheet.fa_avail_for_sale IS '可供出售金融资产';
COMMENT ON COLUMN balancesheet.htm_invest IS '持有至到期投资';
COMMENT ON COLUMN balancesheet.lt_eqt_invest IS '长期股权投资';
COMMENT ON COLUMN balancesheet.invest_real_estate IS '投资性房地产';
COMMENT ON COLUMN balancesheet.time_deposits IS '定期存款';
COMMENT ON COLUMN balancesheet.oth_assets IS '其他资产';
COMMENT ON COLUMN balancesheet.lt_rec IS '长期应收款';
COMMENT ON COLUMN balancesheet.fix_assets IS '固定资产';
COMMENT ON COLUMN balancesheet.cip IS '在建工程';
COMMENT ON COLUMN balancesheet.const_materials IS '工程物资';
COMMENT ON COLUMN balancesheet.fixed_assets_disp IS '固定资产清理';
COMMENT ON COLUMN balancesheet.produc_bio_assets IS '生产性生物资产';
COMMENT ON COLUMN balancesheet.oil_and_gas_assets IS '油气资产';
COMMENT ON COLUMN balancesheet.intan_assets IS '无形资产';
COMMENT ON COLUMN balancesheet.r_and_d IS '研发支出';
COMMENT ON COLUMN balancesheet.goodwill IS '商誉';
COMMENT ON COLUMN balancesheet.lt_amor_exp IS '长期待摊费用';
COMMENT ON COLUMN balancesheet.defer_tax_assets IS '递延所得税资产';
COMMENT ON COLUMN balancesheet.decr_in_disbur IS '发放贷款及垫款';
COMMENT ON COLUMN balancesheet.oth_nca IS '其他非流动资产';
COMMENT ON COLUMN balancesheet.total_nca IS '非流动资产合计';
COMMENT ON COLUMN balancesheet.cash_reser_cb IS '现金及存放中央银行款项';
COMMENT ON COLUMN balancesheet.depos_in_oth_bfi IS '存放同业和其它金融机构款项';
COMMENT ON COLUMN balancesheet.prec_metals IS '贵金属';
COMMENT ON COLUMN balancesheet.deriv_assets IS '衍生金融资产';
COMMENT ON COLUMN balancesheet.rr_reins_une_prem IS '应收分保未到期责任准备金';
COMMENT ON COLUMN balancesheet.rr_reins_outstd_cla IS '应收分保未决赔款准备金';
COMMENT ON COLUMN balancesheet.rr_reins_lins_liab IS '应收分保寿险责任准备金';
COMMENT ON COLUMN balancesheet.rr_reins_lthins_liab IS '应收分保长期健康险责任准备金';
COMMENT ON COLUMN balancesheet.refund_depos IS '存出保证金';
COMMENT ON COLUMN balancesheet.ph_pledge_loans IS '保户质押贷款';
COMMENT ON COLUMN balancesheet.refund_cap_depos IS '存出资本保证金';
COMMENT ON COLUMN balancesheet.indep_acct_assets IS '独立账户资产';
COMMENT ON COLUMN balancesheet.client_depos IS '其中：客户资金存款';
COMMENT ON COLUMN balancesheet.client_prov IS '其中：客户备付金';
COMMENT ON COLUMN balancesheet.transac_seat_fee IS '其中:交易席位费';
COMMENT ON COLUMN balancesheet.invest_as_receiv IS '应收款项类投资';
COMMENT ON COLUMN balancesheet.total_assets IS '资产总计';
COMMENT ON COLUMN balancesheet.lt_borr IS '长期借款';
COMMENT ON COLUMN balancesheet.st_borr IS '短期借款';
COMMENT ON COLUMN balancesheet.cb_borr IS '向中央银行借款';
COMMENT ON COLUMN balancesheet.depos_ib_deposits IS '吸收存款及同业存放';
COMMENT ON COLUMN balancesheet.loan_oth_bank IS '拆入资金';
COMMENT ON COLUMN balancesheet.trading_fl IS '交易性金融负债';
COMMENT ON COLUMN balancesheet.notes_payable IS '应付票据';
COMMENT ON COLUMN balancesheet.acct_payable IS '应付账款';
COMMENT ON COLUMN balancesheet.adv_receipts IS '预收款项';
COMMENT ON COLUMN balancesheet.sold_for_repur_fa IS '卖出回购金融资产款';
COMMENT ON COLUMN balancesheet.comm_payable IS '应付手续费及佣金';
COMMENT ON COLUMN balancesheet.payroll_payable IS '应付职工薪酬';
COMMENT ON COLUMN balancesheet.taxes_payable IS '应交税费';
COMMENT ON COLUMN balancesheet.int_payable IS '应付利息';
COMMENT ON COLUMN balancesheet.div_payable IS '应付股利';
COMMENT ON COLUMN balancesheet.oth_payable IS '其他应付款';
COMMENT ON COLUMN balancesheet.acc_exp IS '预提费用';
COMMENT ON COLUMN balancesheet.deferred_inc IS '递延收益';
COMMENT ON COLUMN balancesheet.st_bonds_payable IS '应付短期债券';
COMMENT ON COLUMN balancesheet.payable_to_reinsurer IS '应付分保账款';
COMMENT ON COLUMN balancesheet.rsrv_insur_cont IS '保险合同准备金';
COMMENT ON COLUMN balancesheet.acting_trading_sec IS '代理买卖证券款';
COMMENT ON COLUMN balancesheet.acting_uw_sec IS '代理承销证券款';
COMMENT ON COLUMN balancesheet.non_cur_liab_due_1y IS '一年内到期的非流动负债';
COMMENT ON COLUMN balancesheet.oth_cur_liab IS '其他流动负债';
COMMENT ON COLUMN balancesheet.total_cur_liab IS '流动负债合计';
COMMENT ON COLUMN balancesheet.bond_payable IS '应付债券';
COMMENT ON COLUMN balancesheet.lt_payable IS '长期应付款';
COMMENT ON COLUMN balancesheet.specific_payables IS '专项应付款';
COMMENT ON COLUMN balancesheet.estimated_liab IS '预计负债';
COMMENT ON COLUMN balancesheet.defer_tax_liab IS '递延所得税负债';
COMMENT ON COLUMN balancesheet.defer_inc_non_cur_liab IS '递延收益-非流动负债';
COMMENT ON COLUMN balancesheet.oth_ncl IS '其他非流动负债';
COMMENT ON COLUMN balancesheet.total_ncl IS '非流动负债合计';
COMMENT ON COLUMN balancesheet.depos_oth_bfi IS '同业和其它金融机构存放款项';
COMMENT ON COLUMN balancesheet.deriv_liab IS '衍生金融负债';
COMMENT ON COLUMN balancesheet.depos IS '吸收存款';
COMMENT ON COLUMN balancesheet.agency_bus_liab IS '代理业务负债';
COMMENT ON COLUMN balancesheet.oth_liab IS '其他负债';
COMMENT ON COLUMN balancesheet.prem_receiv_adva IS '预收保费';
COMMENT ON COLUMN balancesheet.depos_received IS '存入保证金';
COMMENT ON COLUMN balancesheet.ph_invest IS '保户储金及投资款';
COMMENT ON COLUMN balancesheet.reser_une_prem IS '未到期责任准备金';
COMMENT ON COLUMN balancesheet.reser_outstd_claims IS '未决赔款准备金';
COMMENT ON COLUMN balancesheet.reser_lins_liab IS '寿险责任准备金';
COMMENT ON COLUMN balancesheet.reser_lthins_liab IS '长期健康险责任准备金';
COMMENT ON COLUMN balancesheet.indept_acc_liab IS '独立账户负债';
COMMENT ON COLUMN balancesheet.pledge_borr IS '其中:质押借款';
COMMENT ON COLUMN balancesheet.indem_payable IS '应付赔付款';
COMMENT ON COLUMN balancesheet.policy_div_payable IS '应付保单红利';
COMMENT ON COLUMN balancesheet.total_liab IS '负债合计';
COMMENT ON COLUMN balancesheet.treasury_share IS '减:库存股';
COMMENT ON COLUMN balancesheet.ordin_risk_reser IS '一般风险准备';
COMMENT ON COLUMN balancesheet.forex_differ IS '外币报表折算差额';
COMMENT ON COLUMN balancesheet.invest_loss_unconf IS '未确认的投资损失';
COMMENT ON COLUMN balancesheet.minority_int IS '少数股东权益';
COMMENT ON COLUMN balancesheet.total_hldr_eqy_exc_min_int IS '股东权益合计(不含少数股东权益)';
COMMENT ON COLUMN balancesheet.total_hldr_eqy_inc_min_int IS '股东权益合计(含少数股东权益)';
COMMENT ON COLUMN balancesheet.total_liab_hldr_eqy IS '负债及股东权益总计';
COMMENT ON COLUMN balancesheet.lt_payroll_payable IS '长期应付职工薪酬';
COMMENT ON COLUMN balancesheet.oth_comp_income IS '其他综合收益';
COMMENT ON COLUMN balancesheet.oth_eqt_tools IS '其他权益工具';
COMMENT ON COLUMN balancesheet.oth_eqt_tools_p_shr IS '其他权益工具(优先股)';
COMMENT ON COLUMN balancesheet.lending_funds IS '融出资金';
COMMENT ON COLUMN balancesheet.acc_receivable IS '应收款项';
COMMENT ON COLUMN balancesheet.st_fin_payable IS '应付短期融资款';
COMMENT ON COLUMN balancesheet.payables IS '应付款项';
COMMENT ON COLUMN balancesheet.hfs_assets IS '持有待售的资产';
COMMENT ON COLUMN balancesheet.hfs_sales IS '持有待售的负债';
COMMENT ON COLUMN balancesheet.cost_fin_assets IS '以摊余成本计量的金融资产';
COMMENT ON COLUMN balancesheet.fair_value_fin_assets IS '以公允价值计量且其变动计入其他综合收益的金融资产';
COMMENT ON COLUMN balancesheet.cip_total IS '在建工程(合计)(元)';
COMMENT ON COLUMN balancesheet.oth_pay_total IS '其他应付款(合计)(元)';
COMMENT ON COLUMN balancesheet.long_pay_total IS '长期应付款(合计)(元)';
COMMENT ON COLUMN balancesheet.debt_invest IS '债权投资(元)';
COMMENT ON COLUMN balancesheet.oth_debt_invest IS '其他债权投资(元)';
COMMENT ON COLUMN balancesheet.oth_eq_invest IS '其他权益工具投资(元)';
COMMENT ON COLUMN balancesheet.oth_illiq_fin_assets IS '其他非流动金融资产(元)';
COMMENT ON COLUMN balancesheet.oth_eq_ppbond IS '其他权益工具:永续债(元)';
COMMENT ON COLUMN balancesheet.receiv_financing IS '应收款项融资';
COMMENT ON COLUMN balancesheet.use_right_assets IS '使用权资产';
COMMENT ON COLUMN balancesheet.lease_liab IS '租赁负债';
COMMENT ON COLUMN balancesheet.contract_assets IS '合同资产';
COMMENT ON COLUMN balancesheet.contract_liab IS '合同负债';
COMMENT ON COLUMN balancesheet.accounts_receiv_bill IS '应收票据及应收账款';
COMMENT ON COLUMN balancesheet.accounts_pay IS '应付票据及应付账款';
COMMENT ON COLUMN balancesheet.oth_rcv_total IS '其他应收款(合计)（元）';
COMMENT ON COLUMN balancesheet.fix_assets_total IS '固定资产(合计)(元)';
COMMENT ON COLUMN balancesheet.update_flag IS '更新标识';


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	TS股票代码
-- ann_date	str	Y	公告日期
-- f_ann_date	str	Y	实际公告日期
-- end_date	str	Y	报告期
-- report_type	str	Y	报表类型
-- comp_type	str	Y	公司类型(1一般工商业2银行3保险4证券)
-- end_type	str	Y	报告期类型
-- total_share	float	Y	期末总股本
-- cap_rese	float	Y	资本公积金
-- undistr_porfit	float	Y	未分配利润
-- surplus_rese	float	Y	盈余公积金
-- special_rese	float	Y	专项储备
-- money_cap	float	Y	货币资金
-- trad_asset	float	Y	交易性金融资产
-- notes_receiv	float	Y	应收票据
-- accounts_receiv	float	Y	应收账款
-- oth_receiv	float	Y	其他应收款
-- prepayment	float	Y	预付款项
-- div_receiv	float	Y	应收股利
-- int_receiv	float	Y	应收利息
-- inventories	float	Y	存货
-- amor_exp	float	Y	待摊费用
-- nca_within_1y	float	Y	一年内到期的非流动资产
-- sett_rsrv	float	Y	结算备付金
-- loanto_oth_bank_fi	float	Y	拆出资金
-- premium_receiv	float	Y	应收保费
-- reinsur_receiv	float	Y	应收分保账款
-- reinsur_res_receiv	float	Y	应收分保合同准备金
-- pur_resale_fa	float	Y	买入返售金融资产
-- oth_cur_assets	float	Y	其他流动资产
-- total_cur_assets	float	Y	流动资产合计
-- fa_avail_for_sale	float	Y	可供出售金融资产
-- htm_invest	float	Y	持有至到期投资
-- lt_eqt_invest	float	Y	长期股权投资
-- invest_real_estate	float	Y	投资性房地产
-- time_deposits	float	Y	定期存款
-- oth_assets	float	Y	其他资产
-- lt_rec	float	Y	长期应收款
-- fix_assets	float	Y	固定资产
-- cip	float	Y	在建工程
-- const_materials	float	Y	工程物资
-- fixed_assets_disp	float	Y	固定资产清理
-- produc_bio_assets	float	Y	生产性生物资产
-- oil_and_gas_assets	float	Y	油气资产
-- intan_assets	float	Y	无形资产
-- r_and_d	float	Y	研发支出
-- goodwill	float	Y	商誉
-- lt_amor_exp	float	Y	长期待摊费用
-- defer_tax_assets	float	Y	递延所得税资产
-- decr_in_disbur	float	Y	发放贷款及垫款
-- oth_nca	float	Y	其他非流动资产
-- total_nca	float	Y	非流动资产合计
-- cash_reser_cb	float	Y	现金及存放中央银行款项
-- depos_in_oth_bfi	float	Y	存放同业和其它金融机构款项
-- prec_metals	float	Y	贵金属
-- deriv_assets	float	Y	衍生金融资产
-- rr_reins_une_prem	float	Y	应收分保未到期责任准备金
-- rr_reins_outstd_cla	float	Y	应收分保未决赔款准备金
-- rr_reins_lins_liab	float	Y	应收分保寿险责任准备金
-- rr_reins_lthins_liab	float	Y	应收分保长期健康险责任准备金
-- refund_depos	float	Y	存出保证金
-- ph_pledge_loans	float	Y	保户质押贷款
-- refund_cap_depos	float	Y	存出资本保证金
-- indep_acct_assets	float	Y	独立账户资产
-- client_depos	float	Y	其中：客户资金存款
-- client_prov	float	Y	其中：客户备付金
-- transac_seat_fee	float	Y	其中:交易席位费
-- invest_as_receiv	float	Y	应收款项类投资
-- total_assets	float	Y	资产总计
-- lt_borr	float	Y	长期借款
-- st_borr	float	Y	短期借款
-- cb_borr	float	Y	向中央银行借款
-- depos_ib_deposits	float	Y	吸收存款及同业存放
-- loan_oth_bank	float	Y	拆入资金
-- trading_fl	float	Y	交易性金融负债
-- notes_payable	float	Y	应付票据
-- acct_payable	float	Y	应付账款
-- adv_receipts	float	Y	预收款项
-- sold_for_repur_fa	float	Y	卖出回购金融资产款
-- comm_payable	float	Y	应付手续费及佣金
-- payroll_payable	float	Y	应付职工薪酬
-- taxes_payable	float	Y	应交税费
-- int_payable	float	Y	应付利息
-- div_payable	float	Y	应付股利
-- oth_payable	float	Y	其他应付款
-- acc_exp	float	Y	预提费用
-- deferred_inc	float	Y	递延收益
-- st_bonds_payable	float	Y	应付短期债券
-- payable_to_reinsurer	float	Y	应付分保账款
-- rsrv_insur_cont	float	Y	保险合同准备金
-- acting_trading_sec	float	Y	代理买卖证券款
-- acting_uw_sec	float	Y	代理承销证券款
-- non_cur_liab_due_1y	float	Y	一年内到期的非流动负债
-- oth_cur_liab	float	Y	其他流动负债
-- total_cur_liab	float	Y	流动负债合计
-- bond_payable	float	Y	应付债券
-- lt_payable	float	Y	长期应付款
-- specific_payables	float	Y	专项应付款
-- estimated_liab	float	Y	预计负债
-- defer_tax_liab	float	Y	递延所得税负债
-- defer_inc_non_cur_liab	float	Y	递延收益-非流动负债
-- oth_ncl	float	Y	其他非流动负债
-- total_ncl	float	Y	非流动负债合计
-- depos_oth_bfi	float	Y	同业和其它金融机构存放款项
-- deriv_liab	float	Y	衍生金融负债
-- depos	float	Y	吸收存款
-- agency_bus_liab	float	Y	代理业务负债
-- oth_liab	float	Y	其他负债
-- prem_receiv_adva	float	Y	预收保费
-- depos_received	float	Y	存入保证金
-- ph_invest	float	Y	保户储金及投资款
-- reser_une_prem	float	Y	未到期责任准备金
-- reser_outstd_claims	float	Y	未决赔款准备金
-- reser_lins_liab	float	Y	寿险责任准备金
-- reser_lthins_liab	float	Y	长期健康险责任准备金
-- indept_acc_liab	float	Y	独立账户负债
-- pledge_borr	float	Y	其中:质押借款
-- indem_payable	float	Y	应付赔付款
-- policy_div_payable	float	Y	应付保单红利
-- total_liab	float	Y	负债合计
-- treasury_share	float	Y	减:库存股
-- ordin_risk_reser	float	Y	一般风险准备
-- forex_differ	float	Y	外币报表折算差额
-- invest_loss_unconf	float	Y	未确认的投资损失
-- minority_int	float	Y	少数股东权益
-- total_hldr_eqy_exc_min_int	float	Y	股东权益合计(不含少数股东权益)
-- total_hldr_eqy_inc_min_int	float	Y	股东权益合计(含少数股东权益)
-- total_liab_hldr_eqy	float	Y	负债及股东权益总计
-- lt_payroll_payable	float	Y	长期应付职工薪酬
-- oth_comp_income	float	Y	其他综合收益
-- oth_eqt_tools	float	Y	其他权益工具
-- oth_eqt_tools_p_shr	float	Y	其他权益工具(优先股)
-- lending_funds	float	Y	融出资金
-- acc_receivable	float	Y	应收款项
-- st_fin_payable	float	Y	应付短期融资款
-- payables	float	Y	应付款项
-- hfs_assets	float	Y	持有待售的资产
-- hfs_sales	float	Y	持有待售的负债
-- cost_fin_assets	float	Y	以摊余成本计量的金融资产
-- fair_value_fin_assets	float	Y	以公允价值计量且其变动计入其他综合收益的金融资产
-- cip_total	float	Y	在建工程(合计)(元)
-- oth_pay_total	float	Y	其他应付款(合计)(元)
-- long_pay_total	float	Y	长期应付款(合计)(元)
-- debt_invest	float	Y	债权投资(元)
-- oth_debt_invest	float	Y	其他债权投资(元)
-- oth_eq_invest	float	N	其他权益工具投资(元)
-- oth_illiq_fin_assets	float	N	其他非流动金融资产(元)
-- oth_eq_ppbond	float	N	其他权益工具:永续债(元)
-- receiv_financing	float	N	应收款项融资
-- use_right_assets	float	N	使用权资产
-- lease_liab	float	N	租赁负债
-- contract_assets	float	Y	合同资产
-- contract_liab	float	Y	合同负债
-- accounts_receiv_bill	float	Y	应收票据及应收账款
-- accounts_pay	float	Y	应付票据及应付账款
-- oth_rcv_total	float	Y	其他应收款(合计)（元）
-- fix_assets_total	float	Y	固定资产(合计)(元)
-- update_flag	str	Y	更新标识