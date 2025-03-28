-- 股票数据 - 财务数据

-- 现金流量表（cashflow）
CREATE TABLE cashflow (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL COMMENT 'TS股票代码',
    ann_date DATE COMMENT '公告日期',
    f_ann_date DATE COMMENT '实际公告日期',
    end_date DATE COMMENT '报告期',
    comp_type CHAR(1) COMMENT '公司类型(1一般工商业2银行3保险4证券)',
    report_type VARCHAR(10) COMMENT '报表类型',
    end_type VARCHAR(10) COMMENT '报告期类型',
    
    -- Basic fields
    net_profit NUMERIC(20,4) COMMENT '净利润',
    finan_exp NUMERIC(20,4) COMMENT '财务费用',
    
    -- Operating activities cash inflow
    c_fr_sale_sg NUMERIC(20,4) COMMENT '销售商品、提供劳务收到的现金',
    recp_tax_rends NUMERIC(20,4) COMMENT '收到的税费返还',
    n_depos_incr_fi NUMERIC(20,4) COMMENT '客户存款和同业存放款项净增加额',
    n_incr_loans_cb NUMERIC(20,4) COMMENT '向中央银行借款净增加额',
    n_inc_borr_oth_fi NUMERIC(20,4) COMMENT '向其他金融机构拆入资金净增加额',
    prem_fr_orig_contr NUMERIC(20,4) COMMENT '收到原保险合同保费取得的现金',
    n_incr_insured_dep NUMERIC(20,4) COMMENT '保户储金净增加额',
    n_reinsur_prem NUMERIC(20,4) COMMENT '收到再保业务现金净额',
    n_incr_disp_tfa NUMERIC(20,4) COMMENT '处置交易性金融资产净增加额',
    ifc_cash_incr NUMERIC(20,4) COMMENT '收取利息和手续费净增加额',
    n_incr_disp_faas NUMERIC(20,4) COMMENT '处置可供出售金融资产净增加额',
    n_incr_loans_oth_bank NUMERIC(20,4) COMMENT '拆入资金净增加额',
    n_cap_incr_repur NUMERIC(20,4) COMMENT '回购业务资金净增加额',
    c_fr_oth_operate_a NUMERIC(20,4) COMMENT '收到其他与经营活动有关的现金',
    c_inf_fr_operate_a NUMERIC(20,4) COMMENT '经营活动现金流入小计',
    
    -- Operating activities cash outflow
    c_paid_goods_s NUMERIC(20,4) COMMENT '购买商品、接受劳务支付的现金',
    c_paid_to_for_empl NUMERIC(20,4) COMMENT '支付给职工以及为职工支付的现金',
    c_paid_for_taxes NUMERIC(20,4) COMMENT '支付的各项税费',
    n_incr_clt_loan_adv NUMERIC(20,4) COMMENT '客户贷款及垫款净增加额',
    n_incr_dep_cbob NUMERIC(20,4) COMMENT '存放央行和同业款项净增加额',
    c_pay_claims_orig_inco NUMERIC(20,4) COMMENT '支付原保险合同赔付款项的现金',
    pay_handling_chrg NUMERIC(20,4) COMMENT '支付手续费的现金',
    pay_comm_insur_plcy NUMERIC(20,4) COMMENT '支付保单红利的现金',
    oth_cash_pay_oper_act NUMERIC(20,4) COMMENT '支付其他与经营活动有关的现金',
    st_cash_out_act NUMERIC(20,4) COMMENT '经营活动现金流出小计',
    n_cashflow_act NUMERIC(20,4) COMMENT '经营活动产生的现金流量净额',
    
    -- Investing activities cash inflow
    oth_recp_ral_inv_act NUMERIC(20,4) COMMENT '收到其他与投资活动有关的现金',
    c_disp_withdrwl_invest NUMERIC(20,4) COMMENT '收回投资收到的现金',
    c_recp_return_invest NUMERIC(20,4) COMMENT '取得投资收益收到的现金',
    n_recp_disp_fiolta NUMERIC(20,4) COMMENT '处置固定资产、无形资产和其他长期资产收回的现金净额',
    n_recp_disp_sobu NUMERIC(20,4) COMMENT '处置子公司及其他营业单位收到的现金净额',
    stot_inflows_inv_act NUMERIC(20,4) COMMENT '投资活动现金流入小计',
    
    -- Investing activities cash outflow
    c_pay_acq_const_fiolta NUMERIC(20,4) COMMENT '购建固定资产、无形资产和其他长期资产支付的现金',
    c_paid_invest NUMERIC(20,4) COMMENT '投资支付的现金',
    n_disp_subs_oth_biz NUMERIC(20,4) COMMENT '取得子公司及其他营业单位支付的现金净额',
    oth_pay_ral_inv_act NUMERIC(20,4) COMMENT '支付其他与投资活动有关的现金',
    n_incr_pledge_loan NUMERIC(20,4) COMMENT '质押贷款净增加额',
    stot_out_inv_act NUMERIC(20,4) COMMENT '投资活动现金流出小计',
    n_cashflow_inv_act NUMERIC(20,4) COMMENT '投资活动产生的现金流量净额',
    
    -- Financing activities cash inflow
    c_recp_borrow NUMERIC(20,4) COMMENT '取得借款收到的现金',
    proc_issue_bonds NUMERIC(20,4) COMMENT '发行债券收到的现金',
    oth_cash_recp_ral_fnc_act NUMERIC(20,4) COMMENT '收到其他与筹资活动有关的现金',
    stot_cash_in_fnc_act NUMERIC(20,4) COMMENT '筹资活动现金流入小计',
    free_cashflow NUMERIC(20,4) COMMENT '企业自由现金流量',
    
    -- Financing activities cash outflow
    c_prepay_amt_borr NUMERIC(20,4) COMMENT '偿还债务支付的现金',
    c_pay_dist_dpcp_int_exp NUMERIC(20,4) COMMENT '分配股利、利润或偿付利息支付的现金',
    incl_dvd_profit_paid_sc_ms NUMERIC(20,4) COMMENT '其中:子公司支付给少数股东的股利、利润',
    oth_cashpay_ral_fnc_act NUMERIC(20,4) COMMENT '支付其他与筹资活动有关的现金',
    stot_cashout_fnc_act NUMERIC(20,4) COMMENT '筹资活动现金流出小计',
    n_cash_flows_fnc_act NUMERIC(20,4) COMMENT '筹资活动产生的现金流量净额',
    
    -- Foreign exchange impact and cash summary
    eff_fx_flu_cash NUMERIC(20,4) COMMENT '汇率变动对现金的影响',
    n_incr_cash_cash_equ NUMERIC(20,4) COMMENT '现金及现金等价物净增加额',
    c_cash_equ_beg_period NUMERIC(20,4) COMMENT '期初现金及现金等价物余额',
    c_cash_equ_end_period NUMERIC(20,4) COMMENT '期末现金及现金等价物余额',
    
    -- Additional financing activities
    c_recp_cap_contrib NUMERIC(20,4) COMMENT '吸收投资收到的现金',
    incl_cash_rec_saims NUMERIC(20,4) COMMENT '其中:子公司吸收少数股东投资收到的现金',
    
    -- Indirect method adjustments
    uncon_invest_loss NUMERIC(20,4) COMMENT '未确认投资损失',
    prov_depr_assets NUMERIC(20,4) COMMENT '加:资产减值准备',
    depr_fa_coga_dpba NUMERIC(20,4) COMMENT '固定资产折旧、油气资产折耗、生产性生物资产折旧',
    amort_intang_assets NUMERIC(20,4) COMMENT '无形资产摊销',
    lt_amort_deferred_exp NUMERIC(20,4) COMMENT '长期待摊费用摊销',
    decr_deferred_exp NUMERIC(20,4) COMMENT '待摊费用减少',
    incr_acc_exp NUMERIC(20,4) COMMENT '预提费用增加',
    loss_disp_fiolta NUMERIC(20,4) COMMENT '处置固定、无形资产和其他长期资产的损失',
    loss_scr_fa NUMERIC(20,4) COMMENT '固定资产报废损失',
    loss_fv_chg NUMERIC(20,4) COMMENT '公允价值变动损失',
    invest_loss NUMERIC(20,4) COMMENT '投资损失',
    decr_def_inc_tax_assets NUMERIC(20,4) COMMENT '递延所得税资产减少',
    incr_def_inc_tax_liab NUMERIC(20,4) COMMENT '递延所得税负债增加',
    decr_inventories NUMERIC(20,4) COMMENT '存货的减少',
    decr_oper_payable NUMERIC(20,4) COMMENT '经营性应收项目的减少',
    incr_oper_payable NUMERIC(20,4) COMMENT '经营性应付项目的增加',
    others NUMERIC(20,4) COMMENT '其他',
    im_net_cashflow_oper_act NUMERIC(20,4) COMMENT '经营活动产生的现金流量净额(间接法)',
    
    -- Debt related adjustments
    conv_debt_into_cap NUMERIC(20,4) COMMENT '债务转为资本',
    conv_copbonds_due_within_1y NUMERIC(20,4) COMMENT '一年内到期的可转换公司债券',
    fa_fnc_leases NUMERIC(20,4) COMMENT '融资租入固定资产',
    im_n_incr_cash_equ NUMERIC(20,4) COMMENT '现金及现金等价物净增加额(间接法)',
    
    -- Additional fields for financial institutions
    net_dism_capital_add NUMERIC(20,4) COMMENT '拆出资金净增加额',
    net_cash_rece_sec NUMERIC(20,4) COMMENT '代理买卖证券收到的现金净额(元)',
    
    -- New accounting standards fields
    credit_impa_loss NUMERIC(20,4) COMMENT '信用减值损失',
    use_right_asset_dep NUMERIC(20,4) COMMENT '使用权资产折旧',
    oth_loss_asset NUMERIC(20,4) COMMENT '其他资产减值损失',
    
    -- Cash reconciliation
    end_bal_cash NUMERIC(20,4) COMMENT '现金的期末余额',
    beg_bal_cash NUMERIC(20,4) COMMENT '减:现金的期初余额',
    end_bal_cash_equ NUMERIC(20,4) COMMENT '加:现金等价物的期末余额',
    beg_bal_cash_equ NUMERIC(20,4) COMMENT '减:现金等价物的期初余额',
    
    -- Metadata
    update_flag VARCHAR(10) COMMENT '更新标志(1最新）',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_cashflow_ts_code ON cashflow(ts_code);
CREATE INDEX idx_cashflow_end_date ON cashflow(end_date);
CREATE INDEX idx_cashflow_report_type ON cashflow(report_type);

-- Add table comment
COMMENT ON TABLE cashflow IS '金流量表';


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	TS股票代码
-- ann_date	str	Y	公告日期
-- f_ann_date	str	Y	实际公告日期
-- end_date	str	Y	报告期
-- comp_type	str	Y	公司类型(1一般工商业2银行3保险4证券)
-- report_type	str	Y	报表类型
-- end_type	str	Y	报告期类型
-- net_profit	float	Y	净利润
-- finan_exp	float	Y	财务费用
-- c_fr_sale_sg	float	Y	销售商品、提供劳务收到的现金
-- recp_tax_rends	float	Y	收到的税费返还
-- n_depos_incr_fi	float	Y	客户存款和同业存放款项净增加额
-- n_incr_loans_cb	float	Y	向中央银行借款净增加额
-- n_inc_borr_oth_fi	float	Y	向其他金融机构拆入资金净增加额
-- prem_fr_orig_contr	float	Y	收到原保险合同保费取得的现金
-- n_incr_insured_dep	float	Y	保户储金净增加额
-- n_reinsur_prem	float	Y	收到再保业务现金净额
-- n_incr_disp_tfa	float	Y	处置交易性金融资产净增加额
-- ifc_cash_incr	float	Y	收取利息和手续费净增加额
-- n_incr_disp_faas	float	Y	处置可供出售金融资产净增加额
-- n_incr_loans_oth_bank	float	Y	拆入资金净增加额
-- n_cap_incr_repur	float	Y	回购业务资金净增加额
-- c_fr_oth_operate_a	float	Y	收到其他与经营活动有关的现金
-- c_inf_fr_operate_a	float	Y	经营活动现金流入小计
-- c_paid_goods_s	float	Y	购买商品、接受劳务支付的现金
-- c_paid_to_for_empl	float	Y	支付给职工以及为职工支付的现金
-- c_paid_for_taxes	float	Y	支付的各项税费
-- n_incr_clt_loan_adv	float	Y	客户贷款及垫款净增加额
-- n_incr_dep_cbob	float	Y	存放央行和同业款项净增加额
-- c_pay_claims_orig_inco	float	Y	支付原保险合同赔付款项的现金
-- pay_handling_chrg	float	Y	支付手续费的现金
-- pay_comm_insur_plcy	float	Y	支付保单红利的现金
-- oth_cash_pay_oper_act	float	Y	支付其他与经营活动有关的现金
-- st_cash_out_act	float	Y	经营活动现金流出小计
-- n_cashflow_act	float	Y	经营活动产生的现金流量净额
-- oth_recp_ral_inv_act	float	Y	收到其他与投资活动有关的现金
-- c_disp_withdrwl_invest	float	Y	收回投资收到的现金
-- c_recp_return_invest	float	Y	取得投资收益收到的现金
-- n_recp_disp_fiolta	float	Y	处置固定资产、无形资产和其他长期资产收回的现金净额
-- n_recp_disp_sobu	float	Y	处置子公司及其他营业单位收到的现金净额
-- stot_inflows_inv_act	float	Y	投资活动现金流入小计
-- c_pay_acq_const_fiolta	float	Y	购建固定资产、无形资产和其他长期资产支付的现金
-- c_paid_invest	float	Y	投资支付的现金
-- n_disp_subs_oth_biz	float	Y	取得子公司及其他营业单位支付的现金净额
-- oth_pay_ral_inv_act	float	Y	支付其他与投资活动有关的现金
-- n_incr_pledge_loan	float	Y	质押贷款净增加额
-- stot_out_inv_act	float	Y	投资活动现金流出小计
-- n_cashflow_inv_act	float	Y	投资活动产生的现金流量净额
-- c_recp_borrow	float	Y	取得借款收到的现金
-- proc_issue_bonds	float	Y	发行债券收到的现金
-- oth_cash_recp_ral_fnc_act	float	Y	收到其他与筹资活动有关的现金
-- stot_cash_in_fnc_act	float	Y	筹资活动现金流入小计
-- free_cashflow	float	Y	企业自由现金流量
-- c_prepay_amt_borr	float	Y	偿还债务支付的现金
-- c_pay_dist_dpcp_int_exp	float	Y	分配股利、利润或偿付利息支付的现金
-- incl_dvd_profit_paid_sc_ms	float	Y	其中:子公司支付给少数股东的股利、利润
-- oth_cashpay_ral_fnc_act	float	Y	支付其他与筹资活动有关的现金
-- stot_cashout_fnc_act	float	Y	筹资活动现金流出小计
-- n_cash_flows_fnc_act	float	Y	筹资活动产生的现金流量净额
-- eff_fx_flu_cash	float	Y	汇率变动对现金的影响
-- n_incr_cash_cash_equ	float	Y	现金及现金等价物净增加额
-- c_cash_equ_beg_period	float	Y	期初现金及现金等价物余额
-- c_cash_equ_end_period	float	Y	期末现金及现金等价物余额
-- c_recp_cap_contrib	float	Y	吸收投资收到的现金
-- incl_cash_rec_saims	float	Y	其中:子公司吸收少数股东投资收到的现金
-- uncon_invest_loss	float	Y	未确认投资损失
-- prov_depr_assets	float	Y	加:资产减值准备
-- depr_fa_coga_dpba	float	Y	固定资产折旧、油气资产折耗、生产性生物资产折旧
-- amort_intang_assets	float	Y	无形资产摊销
-- lt_amort_deferred_exp	float	Y	长期待摊费用摊销
-- decr_deferred_exp	float	Y	待摊费用减少
-- incr_acc_exp	float	Y	预提费用增加
-- loss_disp_fiolta	float	Y	处置固定、无形资产和其他长期资产的损失
-- loss_scr_fa	float	Y	固定资产报废损失
-- loss_fv_chg	float	Y	公允价值变动损失
-- invest_loss	float	Y	投资损失
-- decr_def_inc_tax_assets	float	Y	递延所得税资产减少
-- incr_def_inc_tax_liab	float	Y	递延所得税负债增加
-- decr_inventories	float	Y	存货的减少
-- decr_oper_payable	float	Y	经营性应收项目的减少
-- incr_oper_payable	float	Y	经营性应付项目的增加
-- others	float	Y	其他
-- im_net_cashflow_oper_act	float	Y	经营活动产生的现金流量净额(间接法)
-- conv_debt_into_cap	float	Y	债务转为资本
-- conv_copbonds_due_within_1y	float	Y	一年内到期的可转换公司债券
-- fa_fnc_leases	float	Y	融资租入固定资产
-- im_n_incr_cash_equ	float	Y	现金及现金等价物净增加额(间接法)
-- net_dism_capital_add	float	Y	拆出资金净增加额
-- net_cash_rece_sec	float	Y	代理买卖证券收到的现金净额(元)
-- credit_impa_loss	float	Y	信用减值损失
-- use_right_asset_dep	float	Y	使用权资产折旧
-- oth_loss_asset	float	Y	其他资产减值损失
-- end_bal_cash	float	Y	现金的期末余额
-- beg_bal_cash	float	Y	减:现金的期初余额
-- end_bal_cash_equ	float	Y	加:现金等价物的期末余额
-- beg_bal_cash_equ	float	Y	减:现金等价物的期初余额
-- update_flag	str	Y	更新标志(1最新）
