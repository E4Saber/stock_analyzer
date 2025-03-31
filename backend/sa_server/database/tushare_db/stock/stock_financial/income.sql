-- 股票数据 - 财务数据

-- 利润表（income）
CREATE TABLE income (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL,
    ann_date DATE,
    f_ann_date DATE,
    end_date DATE,
    report_type VARCHAR(10),
    comp_type CHAR(1),
    end_type VARCHAR(10),
    
    -- Core financial metrics
    basic_eps NUMERIC(20,4),
    diluted_eps NUMERIC(20,4),
    
    -- Revenue related fields
    total_revenue NUMERIC(20,4),
    revenue NUMERIC(20,4),
    int_income NUMERIC(20,4),
    prem_earned NUMERIC(20,4),
    comm_income NUMERIC(20,4),
    n_commis_income NUMERIC(20,4),
    n_oth_income NUMERIC(20,4),
    n_oth_b_income NUMERIC(20,4),
    prem_income NUMERIC(20,4),
    out_prem NUMERIC(20,4),
    une_prem_reser NUMERIC(20,4),
    reins_income NUMERIC(20,4),
    n_sec_tb_income NUMERIC(20,4),
    n_sec_uw_income NUMERIC(20,4),
    n_asset_mg_income NUMERIC(20,4),
    oth_b_income NUMERIC(20,4),
    
    -- Investment and valuation related fields
    fv_value_chg_gain NUMERIC(20,4),
    invest_income NUMERIC(20,4),
    ass_invest_income NUMERIC(20,4),
    forex_gain NUMERIC(20,4),
    
    -- Cost related fields
    total_cogs NUMERIC(20,4),
    oper_cost NUMERIC(20,4),
    int_exp NUMERIC(20,4),
    comm_exp NUMERIC(20,4),
    biz_tax_surchg NUMERIC(20,4),
    sell_exp NUMERIC(20,4),
    admin_exp NUMERIC(20,4),
    fin_exp NUMERIC(20,4),
    assets_impair_loss NUMERIC(20,4),
    
    -- Insurance related fields
    prem_refund NUMERIC(20,4),
    compens_payout NUMERIC(20,4),
    reser_insur_liab NUMERIC(20,4),
    div_payt NUMERIC(20,4),
    reins_exp NUMERIC(20,4),
    oper_exp NUMERIC(20,4),
    compens_payout_refu NUMERIC(20,4),
    insur_reser_refu NUMERIC(20,4),
    reins_cost_refund NUMERIC(20,4),
    other_bus_cost NUMERIC(20,4),
    
    -- Profit related fields
    operate_profit NUMERIC(20,4),
    non_oper_income NUMERIC(20,4),
    non_oper_exp NUMERIC(20,4),
    nca_disploss NUMERIC(20,4),
    total_profit NUMERIC(20,4),
    income_tax NUMERIC(20,4),
    
    -- Net income fields
    n_income NUMERIC(20,4),
    n_income_attr_p NUMERIC(20,4),
    minority_gain NUMERIC(20,4),
    
    -- Comprehensive income fields
    oth_compr_income NUMERIC(20,4),
    t_compr_income NUMERIC(20,4),
    compr_inc_attr_p NUMERIC(20,4),
    compr_inc_attr_m_s NUMERIC(20,4),
    
    -- EBIT and EBITDA
    ebit NUMERIC(20,4),
    ebitda NUMERIC(20,4),
    
    -- Additional insurance and profit distribution fields
    insurance_exp NUMERIC(20,4),
    undist_profit NUMERIC(20,4),
    distable_profit NUMERIC(20,4),
    
    -- R&D and interest fields
    rd_exp NUMERIC(20,4),
    fin_exp_int_exp NUMERIC(20,4),
    fin_exp_int_inc NUMERIC(20,4),
    
    -- Transfers and adjustments
    transfer_surplus_rese NUMERIC(20,4),
    transfer_housing_imprest NUMERIC(20,4),
    transfer_oth NUMERIC(20,4),
    adj_lossgain NUMERIC(20,4),
    
    -- Reserves and funds
    withdra_legal_surplus NUMERIC(20,4),
    withdra_legal_pubfund NUMERIC(20,4),
    withdra_biz_devfund NUMERIC(20,4),
    withdra_rese_fund NUMERIC(20,4),
    withdra_oth_ersu NUMERIC(20,4),
    
    -- Employee and shareholder distributions
    workers_welfare NUMERIC(20,4),
    distr_profit_shrder NUMERIC(20,4),
    prfshare_payable_dvd NUMERIC(20,4),
    comshare_payable_dvd NUMERIC(20,4),
    capit_comstock_div NUMERIC(20,4),
    
    -- Additional financial metrics
    net_after_nr_lp_correct NUMERIC(20,4),
    credit_impa_loss NUMERIC(20,4),
    net_expo_hedging_benefits NUMERIC(20,4),
    oth_impair_loss_assets NUMERIC(20,4),
    total_opcost NUMERIC(20,4),
    amodcost_fin_assets NUMERIC(20,4),
    oth_income NUMERIC(20,4),
    asset_disp_income NUMERIC(20,4),
    continued_net_profit NUMERIC(20,4),
    end_net_profit NUMERIC(20,4),
    
    -- Metadata
    update_flag VARCHAR(10)
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_income_ts_code ON income(ts_code);
CREATE INDEX idx_income_end_date ON income(end_date);
CREATE INDEX idx_income_report_type ON income(report_type);

-- Add unique constraint for upsert operations
ALTER TABLE income ADD CONSTRAINT income_ts_code_end_date_report_type_key 
UNIQUE (ts_code, end_date, report_type);

-- Add table comment
COMMENT ON TABLE income IS '利润表';

-- Add column comments
COMMENT ON COLUMN income.ts_code IS 'TS代码';
COMMENT ON COLUMN income.ann_date IS '公告日期';
COMMENT ON COLUMN income.f_ann_date IS '实际公告日期';
COMMENT ON COLUMN income.end_date IS '报告期';
COMMENT ON COLUMN income.report_type IS '报告类型';
COMMENT ON COLUMN income.comp_type IS '公司类型(1一般工商业2银行3保险4证券)';
COMMENT ON COLUMN income.end_type IS '报告期类型';
COMMENT ON COLUMN income.basic_eps IS '基本每股收益';
COMMENT ON COLUMN income.diluted_eps IS '稀释每股收益';
COMMENT ON COLUMN income.total_revenue IS '营业总收入';
COMMENT ON COLUMN income.revenue IS '营业收入';
COMMENT ON COLUMN income.int_income IS '利息收入';
COMMENT ON COLUMN income.prem_earned IS '已赚保费';
COMMENT ON COLUMN income.comm_income IS '手续费及佣金收入';
COMMENT ON COLUMN income.n_commis_income IS '手续费及佣金净收入';
COMMENT ON COLUMN income.n_oth_income IS '其他经营净收益';
COMMENT ON COLUMN income.n_oth_b_income IS '加:其他业务净收益';
COMMENT ON COLUMN income.prem_income IS '保险业务收入';
COMMENT ON COLUMN income.out_prem IS '减:分出保费';
COMMENT ON COLUMN income.une_prem_reser IS '提取未到期责任准备金';
COMMENT ON COLUMN income.reins_income IS '其中:分保费收入';
COMMENT ON COLUMN income.n_sec_tb_income IS '代理买卖证券业务净收入';
COMMENT ON COLUMN income.n_sec_uw_income IS '证券承销业务净收入';
COMMENT ON COLUMN income.n_asset_mg_income IS '受托客户资产管理业务净收入';
COMMENT ON COLUMN income.oth_b_income IS '其他业务收入';
COMMENT ON COLUMN income.fv_value_chg_gain IS '加:公允价值变动净收益';
COMMENT ON COLUMN income.invest_income IS '加:投资净收益';
COMMENT ON COLUMN income.ass_invest_income IS '其中:对联营企业和合营企业的投资收益';
COMMENT ON COLUMN income.forex_gain IS '加:汇兑净收益';
COMMENT ON COLUMN income.total_cogs IS '营业总成本';
COMMENT ON COLUMN income.oper_cost IS '减:营业成本';
COMMENT ON COLUMN income.int_exp IS '减:利息支出';
COMMENT ON COLUMN income.comm_exp IS '减:手续费及佣金支出';
COMMENT ON COLUMN income.biz_tax_surchg IS '减:营业税金及附加';
COMMENT ON COLUMN income.sell_exp IS '减:销售费用';
COMMENT ON COLUMN income.admin_exp IS '减:管理费用';
COMMENT ON COLUMN income.fin_exp IS '减:财务费用';
COMMENT ON COLUMN income.assets_impair_loss IS '减:资产减值损失';
COMMENT ON COLUMN income.prem_refund IS '退保金';
COMMENT ON COLUMN income.compens_payout IS '赔付总支出';
COMMENT ON COLUMN income.reser_insur_liab IS '提取保险责任准备金';
COMMENT ON COLUMN income.div_payt IS '保户红利支出';
COMMENT ON COLUMN income.reins_exp IS '分保费用';
COMMENT ON COLUMN income.oper_exp IS '营业支出';
COMMENT ON COLUMN income.compens_payout_refu IS '减:摊回赔付支出';
COMMENT ON COLUMN income.insur_reser_refu IS '减:摊回保险责任准备金';
COMMENT ON COLUMN income.reins_cost_refund IS '减:摊回分保费用';
COMMENT ON COLUMN income.other_bus_cost IS '其他业务成本';
COMMENT ON COLUMN income.operate_profit IS '营业利润';
COMMENT ON COLUMN income.non_oper_income IS '加:营业外收入';
COMMENT ON COLUMN income.non_oper_exp IS '减:营业外支出';
COMMENT ON COLUMN income.nca_disploss IS '其中:减:非流动资产处置净损失';
COMMENT ON COLUMN income.total_profit IS '利润总额';
COMMENT ON COLUMN income.income_tax IS '所得税费用';
COMMENT ON COLUMN income.n_income IS '净利润(含少数股东损益)';
COMMENT ON COLUMN income.n_income_attr_p IS '净利润(不含少数股东损益)';
COMMENT ON COLUMN income.minority_gain IS '少数股东损益';
COMMENT ON COLUMN income.oth_compr_income IS '其他综合收益';
COMMENT ON COLUMN income.t_compr_income IS '综合收益总额';
COMMENT ON COLUMN income.compr_inc_attr_p IS '归属于母公司(或股东)的综合收益总额';
COMMENT ON COLUMN income.compr_inc_attr_m_s IS '归属于少数股东的综合收益总额';
COMMENT ON COLUMN income.ebit IS '息税前利润';
COMMENT ON COLUMN income.ebitda IS '息税折旧摊销前利润';
COMMENT ON COLUMN income.insurance_exp IS '保险业务支出';
COMMENT ON COLUMN income.undist_profit IS '年初未分配利润';
COMMENT ON COLUMN income.distable_profit IS '可分配利润';
COMMENT ON COLUMN income.rd_exp IS '研发费用';
COMMENT ON COLUMN income.fin_exp_int_exp IS '财务费用:利息费用';
COMMENT ON COLUMN income.fin_exp_int_inc IS '财务费用:利息收入';
COMMENT ON COLUMN income.transfer_surplus_rese IS '盈余公积转入';
COMMENT ON COLUMN income.transfer_housing_imprest IS '住房周转金转入';
COMMENT ON COLUMN income.transfer_oth IS '其他转入';
COMMENT ON COLUMN income.adj_lossgain IS '调整以前年度损益';
COMMENT ON COLUMN income.withdra_legal_surplus IS '提取法定盈余公积';
COMMENT ON COLUMN income.withdra_legal_pubfund IS '提取法定公益金';
COMMENT ON COLUMN income.withdra_biz_devfund IS '提取企业发展基金';
COMMENT ON COLUMN income.withdra_rese_fund IS '提取储备基金';
COMMENT ON COLUMN income.withdra_oth_ersu IS '提取任意盈余公积金';
COMMENT ON COLUMN income.workers_welfare IS '职工奖金福利';
COMMENT ON COLUMN income.distr_profit_shrder IS '可供股东分配的利润';
COMMENT ON COLUMN income.prfshare_payable_dvd IS '应付优先股股利';
COMMENT ON COLUMN income.comshare_payable_dvd IS '应付普通股股利';
COMMENT ON COLUMN income.capit_comstock_div IS '转作股本的普通股股利';
COMMENT ON COLUMN income.net_after_nr_lp_correct IS '扣除非经常性损益后的净利润（更正前）';
COMMENT ON COLUMN income.credit_impa_loss IS '信用减值损失';
COMMENT ON COLUMN income.net_expo_hedging_benefits IS '净敞口套期收益';
COMMENT ON COLUMN income.oth_impair_loss_assets IS '其他资产减值损失';
COMMENT ON COLUMN income.total_opcost IS '营业总成本（二）';
COMMENT ON COLUMN income.amodcost_fin_assets IS '以摊余成本计量的金融资产终止确认收益';
COMMENT ON COLUMN income.oth_income IS '其他收益';
COMMENT ON COLUMN income.asset_disp_income IS '资产处置收益';
COMMENT ON COLUMN income.continued_net_profit IS '持续经营净利润';
COMMENT ON COLUMN income.end_net_profit IS '终止经营净利润';
COMMENT ON COLUMN income.update_flag IS '更新标识';


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	TS代码
-- ann_date	str	Y	公告日期
-- f_ann_date	str	Y	实际公告日期
-- end_date	str	Y	报告期
-- report_type	str	Y	报告类型 见底部表
-- comp_type	str	Y	公司类型(1一般工商业2银行3保险4证券)
-- end_type	str	Y	报告期类型
-- basic_eps	float	Y	基本每股收益
-- diluted_eps	float	Y	稀释每股收益
-- total_revenue	float	Y	营业总收入
-- revenue	float	Y	营业收入
-- int_income	float	Y	利息收入
-- prem_earned	float	Y	已赚保费
-- comm_income	float	Y	手续费及佣金收入
-- n_commis_income	float	Y	手续费及佣金净收入
-- n_oth_income	float	Y	其他经营净收益
-- n_oth_b_income	float	Y	加:其他业务净收益
-- prem_income	float	Y	保险业务收入
-- out_prem	float	Y	减:分出保费
-- une_prem_reser	float	Y	提取未到期责任准备金
-- reins_income	float	Y	其中:分保费收入
-- n_sec_tb_income	float	Y	代理买卖证券业务净收入
-- n_sec_uw_income	float	Y	证券承销业务净收入
-- n_asset_mg_income	float	Y	受托客户资产管理业务净收入
-- oth_b_income	float	Y	其他业务收入
-- fv_value_chg_gain	float	Y	加:公允价值变动净收益
-- invest_income	float	Y	加:投资净收益
-- ass_invest_income	float	Y	其中:对联营企业和合营企业的投资收益
-- forex_gain	float	Y	加:汇兑净收益
-- total_cogs	float	Y	营业总成本
-- oper_cost	float	Y	减:营业成本
-- int_exp	float	Y	减:利息支出
-- comm_exp	float	Y	减:手续费及佣金支出
-- biz_tax_surchg	float	Y	减:营业税金及附加
-- sell_exp	float	Y	减:销售费用
-- admin_exp	float	Y	减:管理费用
-- fin_exp	float	Y	减:财务费用
-- assets_impair_loss	float	Y	减:资产减值损失
-- prem_refund	float	Y	退保金
-- compens_payout	float	Y	赔付总支出
-- reser_insur_liab	float	Y	提取保险责任准备金
-- div_payt	float	Y	保户红利支出
-- reins_exp	float	Y	分保费用
-- oper_exp	float	Y	营业支出
-- compens_payout_refu	float	Y	减:摊回赔付支出
-- insur_reser_refu	float	Y	减:摊回保险责任准备金
-- reins_cost_refund	float	Y	减:摊回分保费用
-- other_bus_cost	float	Y	其他业务成本
-- operate_profit	float	Y	营业利润
-- non_oper_income	float	Y	加:营业外收入
-- non_oper_exp	float	Y	减:营业外支出
-- nca_disploss	float	Y	其中:减:非流动资产处置净损失
-- total_profit	float	Y	利润总额
-- income_tax	float	Y	所得税费用
-- n_income	float	Y	净利润(含少数股东损益)
-- n_income_attr_p	float	Y	净利润(不含少数股东损益)
-- minority_gain	float	Y	少数股东损益
-- oth_compr_income	float	Y	其他综合收益
-- t_compr_income	float	Y	综合收益总额
-- compr_inc_attr_p	float	Y	归属于母公司(或股东)的综合收益总额
-- compr_inc_attr_m_s	float	Y	归属于少数股东的综合收益总额
-- ebit	float	Y	息税前利润
-- ebitda	float	Y	息税折旧摊销前利润
-- insurance_exp	float	Y	保险业务支出
-- undist_profit	float	Y	年初未分配利润
-- distable_profit	float	Y	可分配利润
-- rd_exp	float	Y	研发费用
-- fin_exp_int_exp	float	Y	财务费用:利息费用
-- fin_exp_int_inc	float	Y	财务费用:利息收入
-- transfer_surplus_rese	float	Y	盈余公积转入
-- transfer_housing_imprest	float	Y	住房周转金转入
-- transfer_oth	float	Y	其他转入
-- adj_lossgain	float	Y	调整以前年度损益
-- withdra_legal_surplus	float	Y	提取法定盈余公积
-- withdra_legal_pubfund	float	Y	提取法定公益金
-- withdra_biz_devfund	float	Y	提取企业发展基金
-- withdra_rese_fund	float	Y	提取储备基金
-- withdra_oth_ersu	float	Y	提取任意盈余公积金
-- workers_welfare	float	Y	职工奖金福利
-- distr_profit_shrhder	float	Y	可供股东分配的利润
-- prfshare_payable_dvd	float	Y	应付优先股股利
-- comshare_payable_dvd	float	Y	应付普通股股利
-- capit_comstock_div	float	Y	转作股本的普通股股利
-- net_after_nr_lp_correct	float	N	扣除非经常性损益后的净利润（更正前）
-- credit_impa_loss	float	N	信用减值损失
-- net_expo_hedging_benefits	float	N	净敞口套期收益
-- oth_impair_loss_assets	float	N	其他资产减值损失
-- total_opcost	float	N	营业总成本（二）
-- amodcost_fin_assets	float	N	以摊余成本计量的金融资产终止确认收益
-- oth_income	float	N	其他收益
-- asset_disp_income	float	N	资产处置收益
-- continued_net_profit	float	N	持续经营净利润
-- end_net_profit	float	N	终止经营净利润
-- update_flag	str	Y	更新标识