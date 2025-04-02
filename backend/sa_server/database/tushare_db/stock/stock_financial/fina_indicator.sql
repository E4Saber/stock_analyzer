-- 股票数据 - 财务指标数据

-- 财务指标表（fina_indicator）
CREATE TABLE fina_indicator (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL,
    ann_date DATE,
    end_date DATE,
    
    -- 每股指标
    eps NUMERIC(20,4),
    dt_eps NUMERIC(20,4),
    total_revenue_ps NUMERIC(20,4),
    revenue_ps NUMERIC(20,4),
    capital_rese_ps NUMERIC(20,4),
    surplus_rese_ps NUMERIC(20,4),
    undist_profit_ps NUMERIC(20,4),
    extra_item NUMERIC(20,4),
    profit_dedt NUMERIC(20,4),
    
    -- 盈利能力指标
    gross_margin NUMERIC(20,4),
    netprofit_margin NUMERIC(20,4),
    grossprofit_margin NUMERIC(20,4),
    cogs_of_sales NUMERIC(20,4),
    expense_of_sales NUMERIC(20,4),
    profit_to_gr NUMERIC(20,4),
    saleexp_to_gr NUMERIC(20,4),
    adminexp_of_gr NUMERIC(20,4),
    finaexp_of_gr NUMERIC(20,4),
    impai_ttm NUMERIC(20,4),
    gc_of_gr NUMERIC(20,4),
    op_of_gr NUMERIC(20,4),
    ebit_of_gr NUMERIC(20,4),
    
    -- 偿债能力指标
    current_ratio NUMERIC(20,4),
    quick_ratio NUMERIC(20,4),
    cash_ratio NUMERIC(20,4),
    debt_to_assets NUMERIC(20,4),
    assets_to_eqt NUMERIC(20,4),
    dp_assets_to_eqt NUMERIC(20,4),
    debt_to_eqt NUMERIC(20,4),
    eqt_to_debt NUMERIC(20,4),
    
    -- 运营能力指标
    invturn_days NUMERIC(20,4),
    arturn_days NUMERIC(20,4),
    inv_turn NUMERIC(20,4),
    ar_turn NUMERIC(20,4),
    ca_turn NUMERIC(20,4),
    fa_turn NUMERIC(20,4),
    assets_turn NUMERIC(20,4),
    turn_days NUMERIC(20,4),
    total_fa_trun NUMERIC(20,4),
    
    -- 现金流指标
    op_income NUMERIC(20,4),
    valuechange_income NUMERIC(20,4),
    interst_income NUMERIC(20,4),
    daa NUMERIC(20,4),
    ebit NUMERIC(20,4),
    ebitda NUMERIC(20,4),
    fcff NUMERIC(20,4),
    fcfe NUMERIC(20,4),
    
    -- 负债结构指标
    current_exint NUMERIC(20,4),
    noncurrent_exint NUMERIC(20,4),
    interestdebt NUMERIC(20,4),
    netdebt NUMERIC(20,4),
    tangible_asset NUMERIC(20,4),
    working_capital NUMERIC(20,4),
    networking_capital NUMERIC(20,4),
    invest_capital NUMERIC(20,4),
    retained_earnings NUMERIC(20,4),
    
    -- 每股指标(扩展)
    diluted2_eps NUMERIC(20,4),
    bps NUMERIC(20,4),
    ocfps NUMERIC(20,4),
    retainedps NUMERIC(20,4),
    cfps NUMERIC(20,4),
    ebit_ps NUMERIC(20,4),
    fcff_ps NUMERIC(20,4),
    fcfe_ps NUMERIC(20,4),
    
    -- 收益率指标
    roe NUMERIC(20,4),
    roe_waa NUMERIC(20,4),
    roe_dt NUMERIC(20,4),
    roa NUMERIC(20,4),
    npta NUMERIC(20,4),
    roic NUMERIC(20,4),
    roe_yearly NUMERIC(20,4),
    roa_yearly NUMERIC(20,4),
    roa_dp NUMERIC(20,4),
    roe_avg NUMERIC(20,4),
    
    -- 利润构成指标
    opincome_of_ebt NUMERIC(20,4),
    investincome_of_ebt NUMERIC(20,4),
    n_op_profit_of_ebt NUMERIC(20,4),
    tax_to_ebt NUMERIC(20,4),
    dtprofit_to_profit NUMERIC(20,4),
    
    -- 现金流构成指标
    salescash_to_or NUMERIC(20,4),
    ocf_to_or NUMERIC(20,4),
    ocf_to_opincome NUMERIC(20,4),
    capitalized_to_da NUMERIC(20,4),
    
    -- 资产构成指标
    ca_to_assets NUMERIC(20,4),
    nca_to_assets NUMERIC(20,4),
    tbassets_to_totalassets NUMERIC(20,4),
    int_to_talcap NUMERIC(20,4),
    eqt_to_talcapital NUMERIC(20,4),
    
    -- 负债构成指标
    currentdebt_to_debt NUMERIC(20,4),
    longdeb_to_debt NUMERIC(20,4),
    ocf_to_shortdebt NUMERIC(20,4),
    eqt_to_interestdebt NUMERIC(20,4),
    tangibleasset_to_debt NUMERIC(20,4),
    tangasset_to_intdebt NUMERIC(20,4),
    tangibleasset_to_netdebt NUMERIC(20,4),
    ocf_to_debt NUMERIC(20,4),
    ocf_to_interestdebt NUMERIC(20,4),
    ocf_to_netdebt NUMERIC(20,4),
    
    -- 偿债能力指标(扩展)
    ebit_to_interest NUMERIC(20,4),
    longdebt_to_workingcapital NUMERIC(20,4),
    ebitda_to_debt NUMERIC(20,4),
    
    -- 营运资产相关
    fixed_assets NUMERIC(20,4),
    profit_prefin_exp NUMERIC(20,4),
    non_op_profit NUMERIC(20,4),
    op_to_ebt NUMERIC(20,4),
    nop_to_ebt NUMERIC(20,4),
    ocf_to_profit NUMERIC(20,4),
    cash_to_liqdebt NUMERIC(20,4),
    cash_to_liqdebt_withinterest NUMERIC(20,4),
    op_to_liqdebt NUMERIC(20,4),
    op_to_debt NUMERIC(20,4),
    roic_yearly NUMERIC(20,4),
    profit_to_op NUMERIC(20,4),
    
    -- 单季度指标
    q_opincome NUMERIC(20,4),
    q_investincome NUMERIC(20,4),
    q_dtprofit NUMERIC(20,4),
    q_eps NUMERIC(20,4),
    q_netprofit_margin NUMERIC(20,4),
    q_gsprofit_margin NUMERIC(20,4),
    q_exp_to_sales NUMERIC(20,4),
    q_profit_to_gr NUMERIC(20,4),
    q_saleexp_to_gr NUMERIC(20,4),
    q_adminexp_to_gr NUMERIC(20,4),
    q_finaexp_to_gr NUMERIC(20,4),
    q_impair_to_gr_ttm NUMERIC(20,4),
    q_gc_to_gr NUMERIC(20,4),
    q_op_to_gr NUMERIC(20,4),
    q_roe NUMERIC(20,4),
    q_dt_roe NUMERIC(20,4),
    q_npta NUMERIC(20,4),
    q_opincome_to_ebt NUMERIC(20,4),
    q_investincome_to_ebt NUMERIC(20,4),
    q_dtprofit_to_profit NUMERIC(20,4),
    q_salescash_to_or NUMERIC(20,4),
    q_ocf_to_sales NUMERIC(20,4),
    q_ocf_to_or NUMERIC(20,4),
    
    -- 同比增长指标
    basic_eps_yoy NUMERIC(20,4),
    dt_eps_yoy NUMERIC(20,4),
    cfps_yoy NUMERIC(20,4),
    op_yoy NUMERIC(20,4),
    ebt_yoy NUMERIC(20,4),
    netprofit_yoy NUMERIC(20,4),
    dt_netprofit_yoy NUMERIC(20,4),
    ocf_yoy NUMERIC(20,4),
    roe_yoy NUMERIC(20,4),
    bps_yoy NUMERIC(20,4),
    assets_yoy NUMERIC(20,4),
    eqt_yoy NUMERIC(20,4),
    tr_yoy NUMERIC(20,4),
    or_yoy NUMERIC(20,4),
    
    -- 单季度同比环比指标
    q_gr_yoy NUMERIC(20,4),
    q_gr_qoq NUMERIC(20,4),
    q_sales_yoy NUMERIC(20,4),
    q_sales_qoq NUMERIC(20,4),
    q_op_yoy NUMERIC(20,4),
    q_op_qoq NUMERIC(20,4),
    q_profit_yoy NUMERIC(20,4),
    q_profit_qoq NUMERIC(20,4),
    q_netprofit_yoy NUMERIC(20,4),
    q_netprofit_qoq NUMERIC(20,4),
    
    -- 其他指标
    equity_yoy NUMERIC(20,4),
    rd_exp NUMERIC(20,4),
    
    -- 更新标识
    update_flag VARCHAR(10)
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_fina_indicator_ts_code ON fina_indicator(ts_code);
CREATE INDEX idx_fina_indicator_end_date ON fina_indicator(end_date);
CREATE INDEX idx_fina_indicator_ann_date ON fina_indicator(ann_date);

-- Add unique constraint for upsert operations
ALTER TABLE fina_indicator ADD CONSTRAINT fina_indicator_ts_code_end_date_key 
UNIQUE (ts_code, end_date);

-- Add table comment
COMMENT ON TABLE fina_indicator IS '财务指标表';

-- Add column comments
COMMENT ON COLUMN fina_indicator.ts_code IS 'TS代码';
COMMENT ON COLUMN fina_indicator.ann_date IS '公告日期';
COMMENT ON COLUMN fina_indicator.end_date IS '报告期';
COMMENT ON COLUMN fina_indicator.eps IS '基本每股收益';
COMMENT ON COLUMN fina_indicator.dt_eps IS '稀释每股收益';
COMMENT ON COLUMN fina_indicator.total_revenue_ps IS '每股营业总收入';
COMMENT ON COLUMN fina_indicator.revenue_ps IS '每股营业收入';
COMMENT ON COLUMN fina_indicator.capital_rese_ps IS '每股资本公积';
COMMENT ON COLUMN fina_indicator.surplus_rese_ps IS '每股盈余公积';
COMMENT ON COLUMN fina_indicator.undist_profit_ps IS '每股未分配利润';
COMMENT ON COLUMN fina_indicator.extra_item IS '非经常性损益';
COMMENT ON COLUMN fina_indicator.profit_dedt IS '扣除非经常性损益后的净利润（扣非净利润）';
COMMENT ON COLUMN fina_indicator.gross_margin IS '毛利';
COMMENT ON COLUMN fina_indicator.current_ratio IS '流动比率';
COMMENT ON COLUMN fina_indicator.quick_ratio IS '速动比率';
COMMENT ON COLUMN fina_indicator.cash_ratio IS '保守速动比率';
COMMENT ON COLUMN fina_indicator.invturn_days IS '存货周转天数';
COMMENT ON COLUMN fina_indicator.arturn_days IS '应收账款周转天数';
COMMENT ON COLUMN fina_indicator.inv_turn IS '存货周转率';
COMMENT ON COLUMN fina_indicator.ar_turn IS '应收账款周转率';
COMMENT ON COLUMN fina_indicator.ca_turn IS '流动资产周转率';
COMMENT ON COLUMN fina_indicator.fa_turn IS '固定资产周转率';
COMMENT ON COLUMN fina_indicator.assets_turn IS '总资产周转率';
COMMENT ON COLUMN fina_indicator.op_income IS '经营活动净收益';
COMMENT ON COLUMN fina_indicator.valuechange_income IS '价值变动净收益';
COMMENT ON COLUMN fina_indicator.interst_income IS '利息费用';
COMMENT ON COLUMN fina_indicator.daa IS '折旧与摊销';
COMMENT ON COLUMN fina_indicator.ebit IS '息税前利润';
COMMENT ON COLUMN fina_indicator.ebitda IS '息税折旧摊销前利润';
COMMENT ON COLUMN fina_indicator.fcff IS '企业自由现金流量';
COMMENT ON COLUMN fina_indicator.fcfe IS '股权自由现金流量';
COMMENT ON COLUMN fina_indicator.current_exint IS '无息流动负债';
COMMENT ON COLUMN fina_indicator.noncurrent_exint IS '无息非流动负债';
COMMENT ON COLUMN fina_indicator.interestdebt IS '带息债务';
COMMENT ON COLUMN fina_indicator.netdebt IS '净债务';
COMMENT ON COLUMN fina_indicator.tangible_asset IS '有形资产';
COMMENT ON COLUMN fina_indicator.working_capital IS '营运资金';
COMMENT ON COLUMN fina_indicator.networking_capital IS '营运流动资本';
COMMENT ON COLUMN fina_indicator.invest_capital IS '全部投入资本';
COMMENT ON COLUMN fina_indicator.retained_earnings IS '留存收益';
COMMENT ON COLUMN fina_indicator.diluted2_eps IS '期末摊薄每股收益';
COMMENT ON COLUMN fina_indicator.bps IS '每股净资产';
COMMENT ON COLUMN fina_indicator.ocfps IS '每股经营活动产生的现金流量净额';
COMMENT ON COLUMN fina_indicator.retainedps IS '每股留存收益';
COMMENT ON COLUMN fina_indicator.cfps IS '每股现金流量净额';
COMMENT ON COLUMN fina_indicator.ebit_ps IS '每股息税前利润';
COMMENT ON COLUMN fina_indicator.fcff_ps IS '每股企业自由现金流量';
COMMENT ON COLUMN fina_indicator.fcfe_ps IS '每股股东自由现金流量';
COMMENT ON COLUMN fina_indicator.netprofit_margin IS '销售净利率';
COMMENT ON COLUMN fina_indicator.grossprofit_margin IS '销售毛利率';
COMMENT ON COLUMN fina_indicator.cogs_of_sales IS '销售成本率';
COMMENT ON COLUMN fina_indicator.expense_of_sales IS '销售期间费用率';
COMMENT ON COLUMN fina_indicator.profit_to_gr IS '净利润/营业总收入';
COMMENT ON COLUMN fina_indicator.saleexp_to_gr IS '销售费用/营业总收入';
COMMENT ON COLUMN fina_indicator.adminexp_of_gr IS '管理费用/营业总收入';
COMMENT ON COLUMN fina_indicator.finaexp_of_gr IS '财务费用/营业总收入';
COMMENT ON COLUMN fina_indicator.impai_ttm IS '资产减值损失/营业总收入';
COMMENT ON COLUMN fina_indicator.gc_of_gr IS '营业总成本/营业总收入';
COMMENT ON COLUMN fina_indicator.op_of_gr IS '营业利润/营业总收入';
COMMENT ON COLUMN fina_indicator.ebit_of_gr IS '息税前利润/营业总收入';
COMMENT ON COLUMN fina_indicator.roe IS '净资产收益率';
COMMENT ON COLUMN fina_indicator.roe_waa IS '加权平均净资产收益率';
COMMENT ON COLUMN fina_indicator.roe_dt IS '净资产收益率(扣除非经常损益)';
COMMENT ON COLUMN fina_indicator.roa IS '总资产报酬率';
COMMENT ON COLUMN fina_indicator.npta IS '总资产净利润';
COMMENT ON COLUMN fina_indicator.roic IS '投入资本回报率';
COMMENT ON COLUMN fina_indicator.roe_yearly IS '年化净资产收益率';
COMMENT ON COLUMN fina_indicator.roa2_yearly IS '年化总资产报酬率';
COMMENT ON COLUMN fina_indicator.roe_avg IS '平均净资产收益率(增发条件)';
COMMENT ON COLUMN fina_indicator.update_flag IS '更新标识';


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	TS代码
-- ann_date	str	Y	公告日期
-- end_date	str	Y	报告期
-- eps	float	Y	基本每股收益
-- dt_eps	float	Y	稀释每股收益
-- total_revenue_ps	float	Y	每股营业总收入
-- revenue_ps	float	Y	每股营业收入
-- capital_rese_ps	float	Y	每股资本公积
-- surplus_rese_ps	float	Y	每股盈余公积
-- undist_profit_ps	float	Y	每股未分配利润
-- extra_item	float	Y	非经常性损益
-- profit_dedt	float	Y	扣除非经常性损益后的净利润（扣非净利润）
-- gross_margin	float	Y	毛利
-- current_ratio	float	Y	流动比率
-- quick_ratio	float	Y	速动比率
-- cash_ratio	float	Y	保守速动比率
-- invturn_days	float	N	存货周转天数
-- arturn_days	float	N	应收账款周转天数
-- inv_turn	float	N	存货周转率
-- ar_turn	float	Y	应收账款周转率
-- ca_turn	float	Y	流动资产周转率
-- fa_turn	float	Y	固定资产周转率
-- assets_turn	float	Y	总资产周转率
-- op_income	float	Y	经营活动净收益
-- valuechange_income	float	N	价值变动净收益
-- interst_income	float	N	利息费用
-- daa	float	N	折旧与摊销
-- ebit	float	Y	息税前利润
-- ebitda	float	Y	息税折旧摊销前利润
-- fcff	float	Y	企业自由现金流量
-- fcfe	float	Y	股权自由现金流量
-- current_exint	float	Y	无息流动负债
-- noncurrent_exint	float	Y	无息非流动负债
-- interestdebt	float	Y	带息债务
-- netdebt	float	Y	净债务
-- tangible_asset	float	Y	有形资产
-- working_capital	float	Y	营运资金
-- networking_capital	float	Y	营运流动资本
-- invest_capital	float	Y	全部投入资本
-- retained_earnings	float	Y	留存收益
-- diluted2_eps	float	Y	期末摊薄每股收益
-- bps	float	Y	每股净资产
-- ocfps	float	Y	每股经营活动产生的现金流量净额
-- retainedps	float	Y	每股留存收益
-- cfps	float	Y	每股现金流量净额
-- ebit_ps	float	Y	每股息税前利润
-- fcff_ps	float	Y	每股企业自由现金流量
-- fcfe_ps	float	Y	每股股东自由现金流量
-- netprofit_margin	float	Y	销售净利率
-- grossprofit_margin	float	Y	销售毛利率
-- cogs_of_sales	float	Y	销售成本率
-- expense_of_sales	float	Y	销售期间费用率
-- profit_to_gr	float	Y	净利润/营业总收入
-- saleexp_to_gr	float	Y	销售费用/营业总收入
-- adminexp_of_gr	float	Y	管理费用/营业总收入
-- finaexp_of_gr	float	Y	财务费用/营业总收入
-- impai_ttm	float	Y	资产减值损失/营业总收入
-- gc_of_gr	float	Y	营业总成本/营业总收入
-- op_of_gr	float	Y	营业利润/营业总收入
-- ebit_of_gr	float	Y	息税前利润/营业总收入
-- roe	float	Y	净资产收益率
-- roe_waa	float	Y	加权平均净资产收益率
-- roe_dt	float	Y	净资产收益率(扣除非经常损益)
-- roa	float	Y	总资产报酬率
-- npta	float	Y	总资产净利润
-- roic	float	Y	投入资本回报率
-- roe_yearly	float	Y	年化净资产收益率
-- roa2_yearly	float	Y	年化总资产报酬率
-- roe_avg	float	N	平均净资产收益率(增发条件)
-- opincome_of_ebt	float	N	经营活动净收益/利润总额
-- investincome_of_ebt	float	N	价值变动净收益/利润总额
-- n_op_profit_of_ebt	float	N	营业外收支净额/利润总额
-- tax_to_ebt	float	N	所得税/利润总额
-- dtprofit_to_profit	float	N	扣除非经常损益后的净利润/净利润
-- salescash_to_or	float	N	销售商品提供劳务收到的现金/营业收入
-- ocf_to_or	float	N	经营活动产生的现金流量净额/营业收入
-- ocf_to_opincome	float	N	经营活动产生的现金流量净额/经营活动净收益
-- capitalized_to_da	float	N	资本支出/折旧和摊销
-- debt_to_assets	float	Y	资产负债率
-- assets_to_eqt	float	Y	权益乘数
-- dp_assets_to_eqt	float	Y	权益乘数(杜邦分析)
-- ca_to_assets	float	Y	流动资产/总资产
-- nca_to_assets	float	Y	非流动资产/总资产
-- tbassets_to_totalassets	float	Y	有形资产/总资产
-- int_to_talcap	float	Y	带息债务/全部投入资本
-- eqt_to_talcapital	float	Y	归属于母公司的股东权益/全部投入资本
-- currentdebt_to_debt	float	Y	流动负债/负债合计
-- longdeb_to_debt	float	Y	非流动负债/负债合计
-- ocf_to_shortdebt	float	Y	经营活动产生的现金流量净额/流动负债
-- debt_to_eqt	float	Y	产权比率
-- eqt_to_debt	float	Y	归属于母公司的股东权益/负债合计
-- eqt_to_interestdebt	float	Y	归属于母公司的股东权益/带息债务
-- tangibleasset_to_debt	float	Y	有形资产/负债合计
-- tangasset_to_intdebt	float	Y	有形资产/带息债务
-- tangibleasset_to_netdebt	float	Y	有形资产/净债务
-- ocf_to_debt	float	Y	经营活动产生的现金流量净额/负债合计
-- ocf_to_interestdebt	float	N	经营活动产生的现金流量净额/带息债务
-- ocf_to_netdebt	float	N	经营活动产生的现金流量净额/净债务
-- ebit_to_interest	float	N	已获利息倍数(EBIT/利息费用)
-- longdebt_to_workingcapital	float	N	长期债务与营运资金比率
-- ebitda_to_debt	float	N	息税折旧摊销前利润/负债合计
-- turn_days	float	Y	营业周期
-- roa_yearly	float	Y	年化总资产净利率
-- roa_dp	float	Y	总资产净利率(杜邦分析)
-- fixed_assets	float	Y	固定资产合计
-- profit_prefin_exp	float	N	扣除财务费用前营业利润
-- non_op_profit	float	N	非营业利润
-- op_to_ebt	float	N	营业利润／利润总额
-- nop_to_ebt	float	N	非营业利润／利润总额
-- ocf_to_profit	float	N	经营活动产生的现金流量净额／营业利润
-- cash_to_liqdebt	float	N	货币资金／流动负债
-- cash_to_liqdebt_withinterest	float	N	货币资金／带息流动负债
-- op_to_liqdebt	float	N	营业利润／流动负债
-- op_to_debt	float	N	营业利润／负债合计
-- roic_yearly	float	N	年化投入资本回报率
-- total_fa_trun	float	N	固定资产合计周转率
-- profit_to_op	float	Y	利润总额／营业收入
-- q_opincome	float	N	经营活动单季度净收益
-- q_investincome	float	N	价值变动单季度净收益
-- q_dtprofit	float	N	扣除非经常损益后的单季度净利润
-- q_eps	float	N	每股收益(单季度)
-- q_netprofit_margin	float	N	销售净利率(单季度)
-- q_gsprofit_margin	float	N	销售毛利率(单季度)
-- q_exp_to_sales	float	N	销售期间费用率(单季度)
-- q_profit_to_gr	float	N	净利润／营业总收入(单季度)
-- q_saleexp_to_gr	float	Y	销售费用／营业总收入 (单季度)
-- q_adminexp_to_gr	float	N	管理费用／营业总收入 (单季度)
-- q_finaexp_to_gr	float	N	财务费用／营业总收入 (单季度)
-- q_impair_to_gr_ttm	float	N	资产减值损失／营业总收入(单季度)
-- q_gc_to_gr	float	Y	营业总成本／营业总收入 (单季度)
-- q_op_to_gr	float	N	营业利润／营业总收入(单季度)
-- q_roe	float	Y	净资产收益率(单季度)
-- q_dt_roe	float	Y	净资产单季度收益率(扣除非经常损益)
-- q_npta	float	Y	总资产净利润(单季度)
-- q_opincome_to_ebt	float	N	经营活动净收益／利润总额(单季度)
-- q_investincome_to_ebt	float	N	价值变动净收益／利润总额(单季度)
-- q_dtprofit_to_profit	float	N	扣除非经常损益后的净利润／净利润(单季度)
-- q_salescash_to_or	float	N	销售商品提供劳务收到的现金／营业收入(单季度)
-- q_ocf_to_sales	float	Y	经营活动产生的现金流量净额／营业收入(单季度)
-- q_ocf_to_or	float	N	经营活动产生的现金流量净额／经营活动净收益(单季度)
-- basic_eps_yoy	float	Y	基本每股收益同比增长率(%)
-- dt_eps_yoy	float	Y	稀释每股收益同比增长率(%)
-- cfps_yoy	float	Y	每股经营活动产生的现金流量净额同比增长率(%)
-- op_yoy	float	Y	营业利润同比增长率(%)
-- ebt_yoy	float	Y	利润总额同比增长率(%)
-- netprofit_yoy	float	Y	归属母公司股东的净利润同比增长率(%)
-- dt_netprofit_yoy	float	Y	归属母公司股东的净利润-扣除非经常损益同比增长率(%)
-- ocf_yoy	float	Y	经营活动产生的现金流量净额同比增长率(%)
-- roe_yoy	float	Y	净资产收益率(摊薄)同比增长率(%)
-- bps_yoy	float	Y	每股净资产相对年初增长率(%)
-- assets_yoy	float	Y	资产总计相对年初增长率(%)
-- eqt_yoy	float	Y	归属母公司的股东权益相对年初增长率(%)
-- tr_yoy	float	Y	营业总收入同比增长率(%)
-- or_yoy	float	Y	营业收入同比增长率(%)
-- q_gr_yoy	float	N	营业总收入同比增长率(%)(单季度)
-- q_gr_qoq	float	N	营业总收入环比增长率(%)(单季度)
-- q_sales_yoy	float	Y	营业收入同比增长率(%)(单季度)
-- q_sales_qoq	float	N	营业收入环比增长率(%)(单季度)
-- q_op_yoy	float	N	营业利润同比增长率(%)(单季度)
-- q_op_qoq	float	Y	营业利润环比增长率(%)(单季度)
-- q_profit_yoy	float	N	净利润同比增长率(%)(单季度)
-- q_profit_qoq	float	N	净利润环比增长率(%)(单季度)
-- q_netprofit_yoy	float	N	归属母公司股东的净利润同比增长率(%)(单季度)
-- q_netprofit_qoq	float	N	归属母公司股东的净利润环比增长率(%)(单季度)
-- equity_yoy	float	Y	净资产同比增长率
-- rd_exp	float	N	研发费用
-- update_flag	str	N	更新标识