import pandas as pd
from app.external.tushare_client import get_tushare_client


# 获取Tushare API实例
pro = get_tushare_client()


def get_income(ts_code: str = None, ann_date: str = None, f_ann_date: str = None,
               start_date: str = None, end_date: str = None, period: str = None,
               report_type: str = None, comp_type: str = None) -> pd.DataFrame:
    """
    income
        接口：income，可以通过数据工具调试和查看数据。
        描述：获取上市公司财务利润表数据
        积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

        提示：当前接口只能按单只股票获取其历史数据，如果需要获取某一季度全部上市公司数据，请使用income_vip接口（参数一致），需积攒5000积分。

    输入参数：
        名称	类型	必选	描述
        - ts_code	str	Y	股票代码
        - ann_date	str	N	公告日期（YYYYMMDD格式，下同）
        - f_ann_date	str	N	实际公告日期
        - start_date	str	N	公告开始日期
        - end_date	str	N	公告结束日期
        - period	str	N	报告期(每个季度最后一天的日期，比如20171231表示年报，20170630半年报，20170930三季报)
        - report_type	str	N	报告类型，参考文档最下方说明
        - comp_type	str	N	公司类型（1一般工商业2银行3保险4证券）

    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS代码
        - ann_date	str	Y	公告日期
        - f_ann_date	str	Y	实际公告日期
        - end_date	str	Y	报告期
        - report_type	str	Y	报告类型 见底部表
        - comp_type	str	Y	公司类型(1一般工商业2银行3保险4证券)
        - end_type	str	Y	报告期类型
        - basic_eps	float	Y	基本每股收益
        - diluted_eps	float	Y	稀释每股收益
        - total_revenue	float	Y	营业总收入
        - revenue	float	Y	营业收入
        - int_income	float	Y	利息收入
        - prem_earned	float	Y	已赚保费
        - comm_income	float	Y	手续费及佣金收入
        - n_commis_income	float	Y	手续费及佣金净收入
        - n_oth_income	float	Y	其他经营净收益
        - n_oth_b_income	float	Y	加:其他业务净收益
        - prem_income	float	Y	保险业务收入
        - out_prem	float	Y	减:分出保费
        - une_prem_reser	float	Y	提取未到期责任准备金
        - reins_income	float	Y	其中:分保费收入
        - n_sec_tb_income	float	Y	代理买卖证券业务净收入
        - n_sec_uw_income	float	Y	证券承销业务净收入
        - n_asset_mg_income	float	Y	受托客户资产管理业务净收入
        - oth_b_income	float	Y	其他业务收入
        - fv_value_chg_gain	float	Y	加:公允价值变动净收益
        - invest_income	float	Y	加:投资净收益
        - ass_invest_income	float	Y	其中:对联营企业和合营企业的投资收益
        - forex_gain	float	Y	加:汇兑净收益
        - total_cogs	float	Y	营业总成本
        - oper_cost	float	Y	减:营业成本
        - int_exp	float	Y	减:利息支出
        - comm_exp	float	Y	减:手续费及佣金支出
        - biz_tax_surchg	float	Y	减:营业税金及附加
        - sell_exp	float	Y	减:销售费用
        - admin_exp	float	Y	减:管理费用
        - fin_exp	float	Y	减:财务费用
        - assets_impair_loss	float	Y	减:资产减值损失
        - prem_refund	float	Y	退保金
        - compens_payout	float	Y	赔付总支出
        - reser_insur_liab	float	Y	提取保险责任准备金
        - div_payt	float	Y	保户红利支出
        - reins_exp	float	Y	分保费用
        - oper_exp	float	Y	营业支出
        - compens_payout_refu	float	Y	减:摊回赔付支出
        - insur_reser_refu	float	Y	减:摊回保险责任准备金
        - reins_cost_refund	float	Y	减:摊回分保费用
        - other_bus_cost	float	Y	其他业务成本
        - operate_profit	float	Y	营业利润
        - non_oper_income	float	Y	加:营业外收入
        - non_oper_exp	float	Y	减:营业外支出
        - nca_disploss	float	Y	其中:减:非流动资产处置净损失
        - total_profit	float	Y	利润总额
        - income_tax	float	Y	所得税费用
        - n_income	float	Y	净利润(含少数股东损益)
        - n_income_attr_p	float	Y	净利润(不含少数股东损益)
        - minority_gain	float	Y	少数股东损益
        - oth_compr_income	float	Y	其他综合收益
        - t_compr_income	float	Y	综合收益总额
        - compr_inc_attr_p	float	Y	归属于母公司(或股东)的综合收益总额
        - compr_inc_attr_m_s	float	Y	归属于少数股东的综合收益总额
        - ebit	float	Y	息税前利润
        - ebitda	float	Y	息税折旧摊销前利润
        - insurance_exp	float	Y	保险业务支出
        - undist_profit	float	Y	年初未分配利润
        - distable_profit	float	Y	可分配利润
        - rd_exp	float	Y	研发费用
        - fin_exp_int_exp	float	Y	财务费用:利息费用
        - fin_exp_int_inc	float	Y	财务费用:利息收入
        - transfer_surplus_rese	float	Y	盈余公积转入
        - transfer_housing_imprest	float	Y	住房周转金转入
        - transfer_oth	float	Y	其他转入
        - adj_lossgain	float	Y	调整以前年度损益
        - withdra_legal_surplus	float	Y	提取法定盈余公积
        - withdra_legal_pubfund	float	Y	提取法定公益金
        - withdra_biz_devfund	float	Y	提取企业发展基金
        - withdra_rese_fund	float	Y	提取储备基金
        - withdra_oth_ersu	float	Y	提取任意盈余公积金
        - workers_welfare	float	Y	职工奖金福利
        - distr_profit_shrhder	float	Y	可供股东分配的利润
        - prfshare_payable_dvd	float	Y	应付优先股股利
        - comshare_payable_dvd	float	Y	应付普通股股利
        - capit_comstock_div	float	Y	转作股本的普通股股利
        - net_after_nr_lp_correct	float	N	扣除非经常性损益后的净利润（更正前）
        - credit_impa_loss	float	N	信用减值损失
        - net_expo_hedging_benefits	float	N	净敞口套期收益
        - oth_impair_loss_assets	float	N	其他资产减值损失
        - total_opcost	float	N	营业总成本（二）
        - amodcost_fin_assets	float	N	以摊余成本计量的金融资产终止确认收益
        - oth_income	float	N	其他收益
        - asset_disp_income	float	N	资产处置收益
        - continued_net_profit	float	N	持续经营净利润
        - end_net_profit	float	N	终止经营净利润
        - update_flag	str	Y	更新标识
    
        主要报表类型说明
            代码	类型	说明
            1	合并报表	上市公司最新报表（默认）
            2	单季合并	单一季度的合并报表
            3	调整单季合并表	调整后的单季合并报表（如果有）
            4	调整合并报表	本年度公布上年同期的财务报表数据，报告期为上年度
            5	调整前合并报表	数据发生变更，将原数据进行保留，即调整前的原数据
            6	母公司报表	该公司母公司的财务报表数据
            7	母公司单季表	母公司的单季度表
            8	母公司调整单季表	母公司调整后的单季表
            9	母公司调整表	该公司母公司的本年度公布上年同期的财务报表数据
            10	母公司调整前报表	母公司调整之前的原始财务报表数据
            11	母公司调整前合并报表	母公司调整之前合并报表原数据
            12	母公司调整前报表	母公司报表发生变更前保留的原数据
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    # 参数检查
    if not ts_code:
        # 股票代码不能为空
        raise ValueError("股票代码不能为空")
    
    try:
        # 获取利润表信息
        income = pro.income(ts_code=ts_code, ann_date=ann_date, f_ann_date=f_ann_date,
                                start_date=start_date, end_date=end_date, period=period,
                                report_type=report_type, comp_type=comp_type)
        
        return income
    except Exception as e:
        print(f"获取利润表数据错误: {str(e)}")
        raise Exception(f"获取利润表数据错误: {str(e)}")


def get_balancesheet(ts_code: str = None, ann_date: str = None,
                        start_date: str = None, end_date: str = None, period: str = None,
                        report_type: str = None, comp_type: str = None) -> pd.DataFrame:
    """
    balancesheet"
        接口：balancesheet，可以通过数据工具调试和查看数据。
        描述：获取上市公司资产负债表
        积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

        提示：当前接口只能按单只股票获取其历史数据，如果需要获取某一季度全部上市公司数据，请使用balancesheet_vip接口（参数一致），需积攒5000积分。
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	Y	股票代码
        - ann_date	str	N	公告日期(YYYYMMDD格式，下同)
        - start_date	str	N	公告开始日期
        - end_date	str	N	公告结束日期
        - period	str	N	报告期(每个季度最后一天的日期，比如20171231表示年报，20170630半年报，20170930三季报)
        - report_type	str	N	报告类型：见下方详细说明
        - comp_type	str	N	公司类型：1一般工商业 2银行 3保险 4证券
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS股票代码
        - ann_date	str	Y	公告日期
        - f_ann_date	str	Y	实际公告日期
        - end_date	str	Y	报告期
        - report_type	str	Y	报表类型
        - comp_type	str	Y	公司类型(1一般工商业2银行3保险4证券)
        - end_type	str	Y	报告期类型
        - total_share	float	Y	期末总股本
        - cap_rese	float	Y	资本公积金
        - undistr_porfit	float	Y	未分配利润
        - surplus_rese	float	Y	盈余公积金
        - special_rese	float	Y	专项储备
        - money_cap	float	Y	货币资金
        - trad_asset	float	Y	交易性金融资产
        - notes_receiv	float	Y	应收票据
        - accounts_receiv	float	Y	应收账款
        - oth_receiv	float	Y	其他应收款
        - prepayment	float	Y	预付款项
        - div_receiv	float	Y	应收股利
        - int_receiv	float	Y	应收利息
        - inventories	float	Y	存货
        - amor_exp	float	Y	待摊费用
        - nca_within_1y	float	Y	一年内到期的非流动资产
        - sett_rsrv	float	Y	结算备付金
        - loanto_oth_bank_fi	float	Y	拆出资金
        - premium_receiv	float	Y	应收保费
        - reinsur_receiv	float	Y	应收分保账款
        - reinsur_res_receiv	float	Y	应收分保合同准备金
        - pur_resale_fa	float	Y	买入返售金融资产
        - oth_cur_assets	float	Y	其他流动资产
        - total_cur_assets	float	Y	流动资产合计
        - fa_avail_for_sale	float	Y	可供出售金融资产
        - htm_invest	float	Y	持有至到期投资
        - lt_eqt_invest	float	Y	长期股权投资
        - invest_real_estate	float	Y	投资性房地产
        - time_deposits	float	Y	定期存款
        - oth_assets	float	Y	其他资产
        - lt_rec	float	Y	长期应收款
        - fix_assets	float	Y	固定资产
        - cip	float	Y	在建工程
        - const_materials	float	Y	工程物资
        - fixed_assets_disp	float	Y	固定资产清理
        - produc_bio_assets	float	Y	生产性生物资产
        - oil_and_gas_assets	float	Y	油气资产
        - intan_assets	float	Y	无形资产
        - r_and_d	float	Y	研发支出
        - goodwill	float	Y	商誉
        - lt_amor_exp	float	Y	长期待摊费用
        - defer_tax_assets	float	Y	递延所得税资产
        - decr_in_disbur	float	Y	发放贷款及垫款
        - oth_nca	float	Y	其他非流动资产
        - total_nca	float	Y	非流动资产合计
        - cash_reser_cb	float	Y	现金及存放中央银行款项
        - depos_in_oth_bfi	float	Y	存放同业和其它金融机构款项
        - prec_metals	float	Y	贵金属
        - deriv_assets	float	Y	衍生金融资产
        - rr_reins_une_prem	float	Y	应收分保未到期责任准备金
        - rr_reins_outstd_cla	float	Y	应收分保未决赔款准备金
        - rr_reins_lins_liab	float	Y	应收分保寿险责任准备金
        - rr_reins_lthins_liab	float	Y	应收分保长期健康险责任准备金
        - refund_depos	float	Y	存出保证金
        - ph_pledge_loans	float	Y	保户质押贷款
        - refund_cap_depos	float	Y	存出资本保证金
        - indep_acct_assets	float	Y	独立账户资产
        - client_depos	float	Y	其中：客户资金存款
        - client_prov	float	Y	其中：客户备付金
        - transac_seat_fee	float	Y	其中:交易席位费
        - invest_as_receiv	float	Y	应收款项类投资
        - total_assets	float	Y	资产总计
        - lt_borr	float	Y	长期借款
        - st_borr	float	Y	短期借款
        - cb_borr	float	Y	向中央银行借款
        - depos_ib_deposits	float	Y	吸收存款及同业存放
        - loan_oth_bank	float	Y	拆入资金
        - trading_fl	float	Y	交易性金融负债
        - notes_payable	float	Y	应付票据
        - acct_payable	float	Y	应付账款
        - adv_receipts	float	Y	预收款项
        - sold_for_repur_fa	float	Y	卖出回购金融资产款
        - comm_payable	float	Y	应付手续费及佣金
        - payroll_payable	float	Y	应付职工薪酬
        - taxes_payable	float	Y	应交税费
        - int_payable	float	Y	应付利息
        - div_payable	float	Y	应付股利
        - oth_payable	float	Y	其他应付款
        - acc_exp	float	Y	预提费用
        - deferred_inc	float	Y	递延收益
        - st_bonds_payable	float	Y	应付短期债券
        - payable_to_reinsurer	float	Y	应付分保账款
        - rsrv_insur_cont	float	Y	保险合同准备金
        - acting_trading_sec	float	Y	代理买卖证券款
        - acting_uw_sec	float	Y	代理承销证券款
        - non_cur_liab_due_1y	float	Y	一年内到期的非流动负债
        - oth_cur_liab	float	Y	其他流动负债
        - total_cur_liab	float	Y	流动负债合计
        - bond_payable	float	Y	应付债券
        - lt_payable	float	Y	长期应付款
        - specific_payables	float	Y	专项应付款
        - estimated_liab	float	Y	预计负债
        - defer_tax_liab	float	Y	递延所得税负债
        - defer_inc_non_cur_liab	float	Y	递延收益-非流动负债
        - oth_ncl	float	Y	其他非流动负债
        - total_ncl	float	Y	非流动负债合计
        - depos_oth_bfi	float	Y	同业和其它金融机构存放款项
        - deriv_liab	float	Y	衍生金融负债
        - depos	float	Y	吸收存款
        - agency_bus_liab	float	Y	代理业务负债
        - oth_liab	float	Y	其他负债
        - prem_receiv_adva	float	Y	预收保费
        - depos_received	float	Y	存入保证金
        - ph_invest	float	Y	保户储金及投资款
        - reser_une_prem	float	Y	未到期责任准备金
        - reser_outstd_claims	float	Y	未决赔款准备金
        - reser_lins_liab	float	Y	寿险责任准备金
        - reser_lthins_liab	float	Y	长期健康险责任准备金
        - indept_acc_liab	float	Y	独立账户负债
        - pledge_borr	float	Y	其中:质押借款
        - indem_payable	float	Y	应付赔付款
        - policy_div_payable	float	Y	应付保单红利
        - total_liab	float	Y	负债合计
        - treasury_share	float	Y	减:库存股
        - ordin_risk_reser	float	Y	一般风险准备
        - forex_differ	float	Y	外币报表折算差额
        - invest_loss_unconf	float	Y	未确认的投资损失
        - minority_int	float	Y	少数股东权益
        - total_hldr_eqy_exc_min_int	float	Y	股东权益合计(不含少数股东权益)
        - total_hldr_eqy_inc_min_int	float	Y	股东权益合计(含少数股东权益)
        - total_liab_hldr_eqy	float	Y	负债及股东权益总计
        - lt_payroll_payable	float	Y	长期应付职工薪酬
        - oth_comp_income	float	Y	其他综合收益
        - oth_eqt_tools	float	Y	其他权益工具
        - oth_eqt_tools_p_shr	float	Y	其他权益工具(优先股)
        - lending_funds	float	Y	融出资金
        - acc_receivable	float	Y	应收款项
        - st_fin_payable	float	Y	应付短期融资款
        - payables	float	Y	应付款项
        - hfs_assets	float	Y	持有待售的资产
        - hfs_sales	float	Y	持有待售的负债
        - cost_fin_assets	float	Y	以摊余成本计量的金融资产
        - fair_value_fin_assets	float	Y	以公允价值计量且其变动计入其他综合收益的金融资产
        - cip_total	float	Y	在建工程(合计)(元)
        - oth_pay_total	float	Y	其他应付款(合计)(元)
        - long_pay_total	float	Y	长期应付款(合计)(元)
        - debt_invest	float	Y	债权投资(元)
        - oth_debt_invest	float	Y	其他债权投资(元)
        - oth_eq_invest	float	N	其他权益工具投资(元)
        - oth_illiq_fin_assets	float	N	其他非流动金融资产(元)
        - oth_eq_ppbond	float	N	其他权益工具:永续债(元)
        - receiv_financing	float	N	应收款项融资
        - use_right_assets	float	N	使用权资产
        - lease_liab	float	N	租赁负债
        - contract_assets	float	Y	合同资产
        - contract_liab	float	Y	合同负债
        - accounts_receiv_bill	float	Y	应收票据及应收账款
        - accounts_pay	float	Y	应付票据及应付账款
        - oth_rcv_total	float	Y	其他应收款(合计)（元）
        - fix_assets_total	float	Y	固定资产(合计)(元)
        - update_flag	str	Y	更新标识
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    # 参数检查
    if not ts_code:
        # 股票代码不能为空
        raise ValueError("股票代码不能为空")
    
    try:
        # 获取资产负债表信息
        balancesheet = pro.balancesheet(ts_code=ts_code, ann_date=ann_date,
                                        start_date=start_date, end_date=end_date, period=period,
                                        report_type=report_type, comp_type=comp_type)
        
        return balancesheet
    except Exception as e:
        print(f"获取资产负债表数据错误: {str(e)}")
        raise Exception(f"获取资产负债表数据错误: {str(e)}")


def get_cashflow(ts_code: str = None, ann_date: str = None, f_ann_date: str = None,
                 start_date: str = None, end_date: str = None, period: str = None,
                 report_type: str = None, comp_type: str = None, is_calc: int = None) -> pd.DataFrame:
    """
    cashflow
        接口：cashflow，可以通过数据工具调试和查看数据。
        描述：获取上市公司现金流量表
        积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

        提示：当前接口只能按单只股票获取其历史数据，如果需要获取某一季度全部上市公司数据，请使用cashflow_vip接口（参数一致），需积攒5000积分。   
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	Y	股票代码
        - ann_date	str	N	公告日期（YYYYMMDD格式，下同）
        - f_ann_date	str	N	实际公告日期
        - start_date	str	N	公告开始日期
        - end_date	str	N	公告结束日期
        - period	str	N	报告期(每个季度最后一天的日期，比如20171231表示年报，20170630半年报，20170930三季报)
        - report_type	str	N	报告类型：见下方详细说明
        - comp_type	str	N	公司类型：1一般工商业 2银行 3保险 4证券
        - is_calc	int	N	是否计算报表
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS股票代码
        - ann_date	str	Y	公告日期
        - f_ann_date	str	Y	实际公告日期
        - end_date	str	Y	报告期
        - comp_type	str	Y	公司类型(1一般工商业2银行3保险4证券)
        - report_type	str	Y	报表类型
        - end_type	str	Y	报告期类型
        - net_profit	float	Y	净利润
        - finan_exp	float	Y	财务费用
        - c_fr_sale_sg	float	Y	销售商品、提供劳务收到的现金
        - recp_tax_rends	float	Y	收到的税费返还
        - n_depos_incr_fi	float	Y	客户存款和同业存放款项净增加额
        - n_incr_loans_cb	float	Y	向中央银行借款净增加额
        - n_inc_borr_oth_fi	float	Y	向其他金融机构拆入资金净增加额
        - prem_fr_orig_contr	float	Y	收到原保险合同保费取得的现金
        - n_incr_insured_dep	float	Y	保户储金净增加额
        - n_reinsur_prem	float	Y	收到再保业务现金净额
        - n_incr_disp_tfa	float	Y	处置交易性金融资产净增加额
        - ifc_cash_incr	float	Y	收取利息和手续费净增加额
        - n_incr_disp_faas	float	Y	处置可供出售金融资产净增加额
        - n_incr_loans_oth_bank	float	Y	拆入资金净增加额
        - n_cap_incr_repur	float	Y	回购业务资金净增加额
        - c_fr_oth_operate_a	float	Y	收到其他与经营活动有关的现金
        - c_inf_fr_operate_a	float	Y	经营活动现金流入小计
        - c_paid_goods_s	float	Y	购买商品、接受劳务支付的现金
        - c_paid_to_for_empl	float	Y	支付给职工以及为职工支付的现金
        - c_paid_for_taxes	float	Y	支付的各项税费
        - n_incr_clt_loan_adv	float	Y	客户贷款及垫款净增加额
        - n_incr_dep_cbob	float	Y	存放央行和同业款项净增加额
        - c_pay_claims_orig_inco	float	Y	支付原保险合同赔付款项的现金
        - pay_handling_chrg	float	Y	支付手续费的现金
        - pay_comm_insur_plcy	float	Y	支付保单红利的现金
        - oth_cash_pay_oper_act	float	Y	支付其他与经营活动有关的现金
        - st_cash_out_act	float	Y	经营活动现金流出小计
        - n_cashflow_act	float	Y	经营活动产生的现金流量净额
        - oth_recp_ral_inv_act	float	Y	收到其他与投资活动有关的现金
        - c_disp_withdrwl_invest	float	Y	收回投资收到的现金
        - c_recp_return_invest	float	Y	取得投资收益收到的现金
        - n_recp_disp_fiolta	float	Y	处置固定资产、无形资产和其他长期资产收回的现金净额
        - n_recp_disp_sobu	float	Y	处置子公司及其他营业单位收到的现金净额
        - stot_inflows_inv_act	float	Y	投资活动现金流入小计
        - c_pay_acq_const_fiolta	float	Y	购建固定资产、无形资产和其他长期资产支付的现金
        - c_paid_invest	float	Y	投资支付的现金
        - n_disp_subs_oth_biz	float	Y	取得子公司及其他营业单位支付的现金净额
        - oth_pay_ral_inv_act	float	Y	支付其他与投资活动有关的现金
        - n_incr_pledge_loan	float	Y	质押贷款净增加额
        - stot_out_inv_act	float	Y	投资活动现金流出小计
        - n_cashflow_inv_act	float	Y	投资活动产生的现金流量净额
        - c_recp_borrow	float	Y	取得借款收到的现金
        - proc_issue_bonds	float	Y	发行债券收到的现金
        - oth_cash_recp_ral_fnc_act	float	Y	收到其他与筹资活动有关的现金
        - stot_cash_in_fnc_act	float	Y	筹资活动现金流入小计
        - free_cashflow	float	Y	企业自由现金流量
        - c_prepay_amt_borr	float	Y	偿还债务支付的现金
        - c_pay_dist_dpcp_int_exp	float	Y	分配股利、利润或偿付利息支付的现金
        - incl_dvd_profit_paid_sc_ms	float	Y	其中:子公司支付给少数股东的股利、利润
        - oth_cashpay_ral_fnc_act	float	Y	支付其他与筹资活动有关的现金
        - stot_cashout_fnc_act	float	Y	筹资活动现金流出小计
        - n_cash_flows_fnc_act	float	Y	筹资活动产生的现金流量净额
        - eff_fx_flu_cash	float	Y	汇率变动对现金的影响
        - n_incr_cash_cash_equ	float	Y	现金及现金等价物净增加额
        - c_cash_equ_beg_period	float	Y	期初现金及现金等价物余额
        - c_cash_equ_end_period	float	Y	期末现金及现金等价物余额
        - c_recp_cap_contrib	float	Y	吸收投资收到的现金
        - incl_cash_rec_saims	float	Y	其中:子公司吸收少数股东投资收到的现金
        - uncon_invest_loss	float	Y	未确认投资损失
        - prov_depr_assets	float	Y	加:资产减值准备
        - depr_fa_coga_dpba	float	Y	固定资产折旧、油气资产折耗、生产性生物资产折旧
        - amort_intang_assets	float	Y	无形资产摊销
        - lt_amort_deferred_exp	float	Y	长期待摊费用摊销
        - decr_deferred_exp	float	Y	待摊费用减少
        - incr_acc_exp	float	Y	预提费用增加
        - loss_disp_fiolta	float	Y	处置固定、无形资产和其他长期资产的损失
        - loss_scr_fa	float	Y	固定资产报废损失
        - loss_fv_chg	float	Y	公允价值变动损失
        - invest_loss	float	Y	投资损失
        - decr_def_inc_tax_assets	float	Y	递延所得税资产减少
        - incr_def_inc_tax_liab	float	Y	递延所得税负债增加
        - decr_inventories	float	Y	存货的减少
        - decr_oper_payable	float	Y	经营性应收项目的减少
        - incr_oper_payable	float	Y	经营性应付项目的增加
        - others	float	Y	其他
        - im_net_cashflow_oper_act	float	Y	经营活动产生的现金流量净额(间接法)
        - conv_debt_into_cap	float	Y	债务转为资本
        - conv_copbonds_due_within_1y	float	Y	一年内到期的可转换公司债券
        - fa_fnc_leases	float	Y	融资租入固定资产
        - im_n_incr_cash_equ	float	Y	现金及现金等价物净增加额(间接法)
        - net_dism_capital_add	float	Y	拆出资金净增加额
        - net_cash_rece_sec	float	Y	代理买卖证券收到的现金净额(元)
        - credit_impa_loss	float	Y	信用减值损失
        - use_right_asset_dep	float	Y	使用权资产折旧
        - oth_loss_asset	float	Y	其他资产减值损失
        - end_bal_cash	float	Y	现金的期末余额
        - beg_bal_cash	float	Y	减:现金的期初余额
        - end_bal_cash_equ	float	Y	加:现金等价物的期末余额
        - beg_bal_cash_equ	float	Y	减:现金等价物的期初余额
        - update_flag	str	Y	更新标志(1最新）
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")

    # 参数检查
    if not ts_code:
        # 股票代码不能为空
        raise ValueError("股票代码不能为空")
    
    try:
        # 获取现金流量表信息
        cashflow = pro.cashflow(ts_code=ts_code, ann_date=ann_date, f_ann_date=f_ann_date,
                                start_date=start_date, end_date=end_date, period=period,
                                report_type=report_type, comp_type=comp_type, is_calc=is_calc)
        
        return cashflow
    except Exception as e:
        print(f"获取现金流量表数据错误: {str(e)}")
        raise Exception(f"获取现金流量表数据错误: {str(e)}")


def get_forecast(ts_code: str = None, ann_date: str = None,
                 start_date: str = None, end_date: str = None,
                 period: str = None, type: str = None) -> pd.DataFrame:
    """
    forecast
        接口：forecast，可以通过数据工具调试和查看数据。
        描述：获取业绩预告数据
        权限：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

        提示：当前接口只能按单只股票获取其历史数据，如果需要获取某一季度全部上市公司数据，请使用forecast_vip接口（参数一致），需积攒5000积分。
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码(二选一)
        - ann_date	str	N	公告日期 (二选一)
        - start_date	str	N	公告开始日期
        - end_date	str	N	公告结束日期
        - period	str	N	报告期(每个季度最后一天的日期，比如20171231表示年报，20170630半年报，20170930三季报)
        - type	str	N	预告类型(预增/预减/扭亏/首亏/续亏/续盈/略增/略减)
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	描述
        - ts_code	str	TS股票代码
        - ann_date	str	公告日期
        - end_date	str	报告期
        - type	str	业绩预告类型(预增/预减/扭亏/首亏/续亏/续盈/略增/略减)
        - p_change_min	float	预告净利润变动幅度下限（%）
        - p_change_max	float	预告净利润变动幅度上限（%）
        - net_profit_min	float	预告净利润下限（万元）
        - net_profit_max	float	预告净利润上限（万元）
        - last_parent_net	float	上年同期归属母公司净利润
        - first_ann_date	str	首次公告日
        - summary	str	业绩预告摘要
        - change_reason	str	业绩变动原因
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")

    # 参数检查
    if not ts_code and not ann_date:
        # 股票代码和公告日期不能同时为空
        raise ValueError("股票代码和公告日期不能同时为空")
    
    try:
        # 获取业绩预告
        forecast = pro.forecast(ts_code=ts_code, ann_date=ann_date,
                                start_date=start_date, end_date=end_date, period=period,
                                type=type)
        
        return forecast
    except Exception as e:
        print(f"获取业绩预告数据错误: {str(e)}")
        raise Exception(f"获取业绩预告数据错误: {str(e)}")


def get_express(ts_code: str = None, ann_date: str = None,
                start_date: str = None, end_date: str = None,
                period: str = None) -> pd.DataFrame:
    """
    express
        接口：express
        描述：获取上市公司业绩快报
        权限：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

        提示：当前接口只能按单只股票获取其历史数据，如果需要获取某一季度全部上市公司数据，请使用express_vip接口（参数一致），需积攒5000积分。
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	Y	股票代码
        - ann_date	str	N	公告日期
        - start_date	str	N	公告开始日期
        - end_date	str	N	公告结束日期
        - period	str	N	报告期(每个季度最后一天的日期,比如20171231表示年报，20170630半年报，20170930三季报)

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	描述
        - ts_code	str	TS股票代码
        - ann_date	str	公告日期
        - end_date	str	报告期
        - revenue	float	营业收入(元)
        - operate_profit	float	营业利润(元)
        - total_profit	float	利润总额(元)
        - n_income	float	净利润(元)
        - total_assets	float	总资产(元)
        - total_hldr_eqy_exc_min_int	float	股东权益合计(不含少数股东权益)(元)
        - diluted_eps	float	每股收益(摊薄)(元)
        - diluted_roe	float	净资产收益率(摊薄)(%)
        - yoy_net_profit	float	去年同期修正后净利润
        - bps	float	每股净资产
        - yoy_sales	float	同比增长率:营业收入
        - yoy_op	float	同比增长率:营业利润
        - yoy_tp	float	同比增长率:利润总额
        - yoy_dedu_np	float	同比增长率:归属母公司股东的净利润
        - yoy_eps	float	同比增长率:基本每股收益
        - yoy_roe	float	同比增减:加权平均净资产收益率
        - growth_assets	float	比年初增长率:总资产
        - yoy_equity	float	比年初增长率:归属母公司的股东权益
        - growth_bps	float	比年初增长率:归属于母公司股东的每股净资产
        - or_last_year	float	去年同期营业收入
        - op_last_year	float	去年同期营业利润
        - tp_last_year	float	去年同期利润总额
        - np_last_year	float	去年同期净利润
        - eps_last_year	float	去年同期每股收益
        - open_net_assets	float	期初净资产
        - open_bps	float	期初每股净资产
        - perf_summary	str	业绩简要说明
        - is_audit	int	是否审计： 1是 0否
        - remark	str	备注
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")

    # 参数检查
    if not ts_code:
        # 股票代码不能为空
        raise ValueError("股票代码不能为空")
    
    try:
        # 获取业绩快报
        express = pro.express(ts_code=ts_code, ann_date=ann_date,
                              start_date=start_date, end_date=end_date, period=period)
        
        return express
    except Exception as e:
        print(f"获取业绩快报数据错误: {str(e)}")
        raise Exception(f"获取业绩快报数据错误: {str(e)}")


def get_dividend(ts_code: str = None, ann_date: str = None,
                 record_date: str = None, ex_date: str = None,
                 imp_ann_date: str = None) -> pd.DataFrame:
    """
    dividend
        接口：dividend
        描述：分红送股数据
        权限：用户需要至少2000积分才可以调取，具体请参阅积分获取办法
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	TS代码
        - ann_date	str	N	公告日
        - record_date	str	N	股权登记日期
        - ex_date	str	N	除权除息日
        - imp_ann_date	str	N	实施公告日

        以上参数至少有一个不能为空

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS代码
        - end_date	str	Y	分红年度
        - ann_date	str	Y	预案公告日
        - div_proc	str	Y	实施进度
        - stk_div	float	Y	每股送转
        - stk_bo_rate	float	Y	每股送股比例
        - stk_co_rate	float	Y	每股转增比例
        - cash_div	float	Y	每股分红（税后）
        - cash_div_tax	float	Y	每股分红（税前）
        - record_date	str	Y	股权登记日
        - ex_date	str	Y	除权除息日
        - pay_date	str	Y	派息日
        - div_listdate	str	Y	红股上市日
        - imp_ann_date	str	Y	实施公告日
        - base_date	str	N	基准日
        - base_share	float	N	基准股本（万）
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")

    # 参数检查
    if not ts_code and not ann_date and not record_date and not ex_date and not imp_ann_date:
        # 至少有一个参数不能为空
        raise ValueError("至少有一个参数不能为空（ts_code, ann_date, record_date, ex_date, imp_ann_date）")
    
    try:
        # 获取分红送股
        dividend = pro.dividend(ts_code=ts_code, ann_date=ann_date,
                                record_date=record_date, ex_date=ex_date,
                                imp_ann_date=imp_ann_date)
        
        return dividend
    except Exception as e:
        print(f"获取分红送股数据错误: {str(e)}")
        raise Exception(f"获取分红送股数据错误: {str(e)}")


def get_fina_indicator(ts_code: str = None, ann_date: str = None,
                        start_date: str = None, end_date: str = None,
                        period: str = None) -> pd.DataFrame:
    """
    fina_indicator
        接口：fina_indicator，可以通过数据工具调试和查看数据。
        描述：获取上市公司财务指标数据，为避免服务器压力，现阶段每次请求最多返回60条记录，可通过设置日期多次请求获取更多数据。
        权限：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

        提示：当前接口只能按单只股票获取其历史数据，如果需要获取某一季度全部上市公司数据，请使用fina_indicator_vip接口（参数一致），需积攒5000积分。
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	Y	TS股票代码,e.g. 600001.SH/000001.SZ
        - ann_date	str	N	公告日期
        - start_date	str	N	报告期开始日期
        - end_date	str	N	报告期结束日期
        - period	str	N	报告期(每个季度最后一天的日期,比如20171231表示年报)

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS代码
        - ann_date	str	Y	公告日期
        - end_date	str	Y	报告期
        - eps	float	Y	基本每股收益
        - dt_eps	float	Y	稀释每股收益
        - total_revenue_ps	float	Y	每股营业总收入
        - revenue_ps	float	Y	每股营业收入
        - capital_rese_ps	float	Y	每股资本公积
        - surplus_rese_ps	float	Y	每股盈余公积
        - undist_profit_ps	float	Y	每股未分配利润
        - extra_item	float	Y	非经常性损益
        - profit_dedt	float	Y	扣除非经常性损益后的净利润（扣非净利润）
        - gross_margin	float	Y	毛利
        - current_ratio	float	Y	流动比率
        - quick_ratio	float	Y	速动比率
        - cash_ratio	float	Y	保守速动比率
        - invturn_days	float	N	存货周转天数
        - arturn_days	float	N	应收账款周转天数
        - inv_turn	float	N	存货周转率
        - ar_turn	float	Y	应收账款周转率
        - ca_turn	float	Y	流动资产周转率
        - fa_turn	float	Y	固定资产周转率
        - assets_turn	float	Y	总资产周转率
        - op_income	float	Y	经营活动净收益
        - valuechange_income	float	N	价值变动净收益
        - interst_income	float	N	利息费用
        - daa	float	N	折旧与摊销
        - ebit	float	Y	息税前利润
        - ebitda	float	Y	息税折旧摊销前利润
        - fcff	float	Y	企业自由现金流量
        - fcfe	float	Y	股权自由现金流量
        - current_exint	float	Y	无息流动负债
        - noncurrent_exint	float	Y	无息非流动负债
        - interestdebt	float	Y	带息债务
        - netdebt	float	Y	净债务
        - tangible_asset	float	Y	有形资产
        - working_capital	float	Y	营运资金
        - networking_capital	float	Y	营运流动资本
        - invest_capital	float	Y	全部投入资本
        - retained_earnings	float	Y	留存收益
        - diluted2_eps	float	Y	期末摊薄每股收益
        - bps	float	Y	每股净资产
        - ocfps	float	Y	每股经营活动产生的现金流量净额
        - retainedps	float	Y	每股留存收益
        - cfps	float	Y	每股现金流量净额
        - ebit_ps	float	Y	每股息税前利润
        - fcff_ps	float	Y	每股企业自由现金流量
        - fcfe_ps	float	Y	每股股东自由现金流量
        - netprofit_margin	float	Y	销售净利率
        - grossprofit_margin	float	Y	销售毛利率
        - cogs_of_sales	float	Y	销售成本率
        - expense_of_sales	float	Y	销售期间费用率
        - profit_to_gr	float	Y	净利润/营业总收入
        - saleexp_to_gr	float	Y	销售费用/营业总收入
        - adminexp_of_gr	float	Y	管理费用/营业总收入
        - finaexp_of_gr	float	Y	财务费用/营业总收入
        - impai_ttm	float	Y	资产减值损失/营业总收入
        - gc_of_gr	float	Y	营业总成本/营业总收入
        - op_of_gr	float	Y	营业利润/营业总收入
        - ebit_of_gr	float	Y	息税前利润/营业总收入
        - roe	float	Y	净资产收益率
        - roe_waa	float	Y	加权平均净资产收益率
        - roe_dt	float	Y	净资产收益率(扣除非经常损益)
        - roa	float	Y	总资产报酬率
        - npta	float	Y	总资产净利润
        - roic	float	Y	投入资本回报率
        - roe_yearly	float	Y	年化净资产收益率
        - roa2_yearly	float	Y	年化总资产报酬率
        - roe_avg	float	N	平均净资产收益率(增发条件)
        - opincome_of_ebt	float	N	经营活动净收益/利润总额
        - investincome_of_ebt	float	N	价值变动净收益/利润总额
        - n_op_profit_of_ebt	float	N	营业外收支净额/利润总额
        - tax_to_ebt	float	N	所得税/利润总额
        - dtprofit_to_profit	float	N	扣除非经常损益后的净利润/净利润
        - salescash_to_or	float	N	销售商品提供劳务收到的现金/营业收入
        - ocf_to_or	float	N	经营活动产生的现金流量净额/营业收入
        - ocf_to_opincome	float	N	经营活动产生的现金流量净额/经营活动净收益
        - capitalized_to_da	float	N	资本支出/折旧和摊销
        - debt_to_assets	float	Y	资产负债率
        - assets_to_eqt	float	Y	权益乘数
        - dp_assets_to_eqt	float	Y	权益乘数(杜邦分析)
        - ca_to_assets	float	Y	流动资产/总资产
        - nca_to_assets	float	Y	非流动资产/总资产
        - tbassets_to_totalassets	float	Y	有形资产/总资产
        - int_to_talcap	float	Y	带息债务/全部投入资本
        - eqt_to_talcapital	float	Y	归属于母公司的股东权益/全部投入资本
        - currentdebt_to_debt	float	Y	流动负债/负债合计
        - longdeb_to_debt	float	Y	非流动负债/负债合计
        - ocf_to_shortdebt	float	Y	经营活动产生的现金流量净额/流动负债
        - debt_to_eqt	float	Y	产权比率
        - eqt_to_debt	float	Y	归属于母公司的股东权益/负债合计
        - eqt_to_interestdebt	float	Y	归属于母公司的股东权益/带息债务
        - tangibleasset_to_debt	float	Y	有形资产/负债合计
        - tangasset_to_intdebt	float	Y	有形资产/带息债务
        - tangibleasset_to_netdebt	float	Y	有形资产/净债务
        - ocf_to_debt	float	Y	经营活动产生的现金流量净额/负债合计
        - ocf_to_interestdebt	float	N	经营活动产生的现金流量净额/带息债务
        - ocf_to_netdebt	float	N	经营活动产生的现金流量净额/净债务
        - ebit_to_interest	float	N	已获利息倍数(EBIT/利息费用)
        - longdebt_to_workingcapital	float	N	长期债务与营运资金比率
        - ebitda_to_debt	float	N	息税折旧摊销前利润/负债合计
        - turn_days	float	Y	营业周期
        - roa_yearly	float	Y	年化总资产净利率
        - roa_dp	float	Y	总资产净利率(杜邦分析)
        - fixed_assets	float	Y	固定资产合计
        - profit_prefin_exp	float	N	扣除财务费用前营业利润
        - non_op_profit	float	N	非营业利润
        - op_to_ebt	float	N	营业利润／利润总额
        - nop_to_ebt	float	N	非营业利润／利润总额
        - ocf_to_profit	float	N	经营活动产生的现金流量净额／营业利润
        - cash_to_liqdebt	float	N	货币资金／流动负债
        - cash_to_liqdebt_withinterest	float	N	货币资金／带息流动负债
        - op_to_liqdebt	float	N	营业利润／流动负债
        - op_to_debt	float	N	营业利润／负债合计
        - roic_yearly	float	N	年化投入资本回报率
        - total_fa_trun	float	N	固定资产合计周转率
        - profit_to_op	float	Y	利润总额／营业收入
        - q_opincome	float	N	经营活动单季度净收益
        - q_investincome	float	N	价值变动单季度净收益
        - q_dtprofit	float	N	扣除非经常损益后的单季度净利润
        - q_eps	float	N	每股收益(单季度)
        - q_netprofit_margin	float	N	销售净利率(单季度)
        - q_gsprofit_margin	float	N	销售毛利率(单季度)
        - q_exp_to_sales	float	N	销售期间费用率(单季度)
        - q_profit_to_gr	float	N	净利润／营业总收入(单季度)
        - q_saleexp_to_gr	float	Y	销售费用／营业总收入 (单季度)
        - q_adminexp_to_gr	float	N	管理费用／营业总收入 (单季度)
        - q_finaexp_to_gr	float	N	财务费用／营业总收入 (单季度)
        - q_impair_to_gr_ttm	float	N	资产减值损失／营业总收入(单季度)
        - q_gc_to_gr	float	Y	营业总成本／营业总收入 (单季度)
        - q_op_to_gr	float	N	营业利润／营业总收入(单季度)
        - q_roe	float	Y	净资产收益率(单季度)
        - q_dt_roe	float	Y	净资产单季度收益率(扣除非经常损益)
        - q_npta	float	Y	总资产净利润(单季度)
        - q_opincome_to_ebt	float	N	经营活动净收益／利润总额(单季度)
        - q_investincome_to_ebt	float	N	价值变动净收益／利润总额(单季度)
        - q_dtprofit_to_profit	float	N	扣除非经常损益后的净利润／净利润(单季度)
        - q_salescash_to_or	float	N	销售商品提供劳务收到的现金／营业收入(单季度)
        - q_ocf_to_sales	float	Y	经营活动产生的现金流量净额／营业收入(单季度)
        - q_ocf_to_or	float	N	经营活动产生的现金流量净额／经营活动净收益(单季度)
        - basic_eps_yoy	float	Y	基本每股收益同比增长率(%)
        - dt_eps_yoy	float	Y	稀释每股收益同比增长率(%)
        - cfps_yoy	float	Y	每股经营活动产生的现金流量净额同比增长率(%)
        - op_yoy	float	Y	营业利润同比增长率(%)
        - ebt_yoy	float	Y	利润总额同比增长率(%)
        - netprofit_yoy	float	Y	归属母公司股东的净利润同比增长率(%)
        - dt_netprofit_yoy	float	Y	归属母公司股东的净利润-扣除非经常损益同比增长率(%)
        - ocf_yoy	float	Y	经营活动产生的现金流量净额同比增长率(%)
        - roe_yoy	float	Y	净资产收益率(摊薄)同比增长率(%)
        - bps_yoy	float	Y	每股净资产相对年初增长率(%)
        - assets_yoy	float	Y	资产总计相对年初增长率(%)
        - eqt_yoy	float	Y	归属母公司的股东权益相对年初增长率(%)
        - tr_yoy	float	Y	营业总收入同比增长率(%)
        - or_yoy	float	Y	营业收入同比增长率(%)
        - q_gr_yoy	float	N	营业总收入同比增长率(%)(单季度)
        - q_gr_qoq	float	N	营业总收入环比增长率(%)(单季度)
        - q_sales_yoy	float	Y	营业收入同比增长率(%)(单季度)
        - q_sales_qoq	float	N	营业收入环比增长率(%)(单季度)
        - q_op_yoy	float	N	营业利润同比增长率(%)(单季度)
        - q_op_qoq	float	Y	营业利润环比增长率(%)(单季度)
        - q_profit_yoy	float	N	净利润同比增长率(%)(单季度)
        - q_profit_qoq	float	N	净利润环比增长率(%)(单季度)
        - q_netprofit_yoy	float	N	归属母公司股东的净利润同比增长率(%)(单季度)
        - q_netprofit_qoq	float	N	归属母公司股东的净利润环比增长率(%)(单季度)
        - equity_yoy	float	Y	净资产同比增长率
        - rd_exp	float	N	研发费用
        - update_flag	str	N	更新标识
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")

    # 参数检查
    if not ts_code:
        # 股票代码不能为空
        raise ValueError("股票代码不能为空")
    
    try:
        # 获取财务指标数据
        fina_indicator = pro.fina_indicator(ts_code=ts_code, ann_date=ann_date,
                                            start_date=start_date, end_date=end_date, period=period)
        
        return fina_indicator
    except Exception as e:
        print(f"获取财务指标数据错误: {str(e)}")
        raise Exception(f"获取财务指标数据错误: {str(e)}")


def get_fina_audit(ts_code: str = None, ann_date: str = None,
                    start_date: str = None, end_date: str = None,
                    period: str = None) -> pd.DataFrame:
    """
    fina_audit
        接口：fina_audit
        描述：获取上市公司定期财务审计意见数据
        权限：用户需要至少500积分才可以调取，具体请参阅积分获取办法
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	Y	股票代码
        - ann_date	str	N	公告日期
        - start_date	str	N	公告开始日期
        - end_date	str	N	公告结束日期
        - period	str	N	报告期(每个季度最后一天的日期,比如20171231表示年报)

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	描述
        - ts_code	str	TS股票代码
        - ann_date	str	公告日期
        - end_date	str	报告期
        - audit_result	str	审计结果
        - audit_fees	float	审计总费用（元）
        - audit_agency	str	会计事务所
        - audit_sign	str	签字会计师
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")

    # 参数检查
    if not ts_code:
        # 股票代码不能为空
        raise ValueError("股票代码不能为空")
    
    try:
        # 获取定期财务审计意见
        fina_audit = pro.fina_audit(ts_code=ts_code, ann_date=ann_date,
                                    start_date=start_date, end_date=end_date, period=period)
        
        return fina_audit
    except Exception as e:
        print(f"获取定期财务审计意见数据错误: {str(e)}")
        raise Exception(f"获取定期财务审计意见数据错误: {str(e)}")


def get_fina_mainbz(ts_code: str = None,
                    period: str = None, type: str = None,
                    start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    fina_mainbz
        接口：fina_mainbz
        描述：获得上市公司主营业务构成，分地区和产品两种方式
        权限：用户需要至少2000积分才可以调取，具体请参阅积分获取办法 ，单次最大提取100行，总量不限制，可循环获取。

        提示：当前接口只能按单只股票获取其历史数据，如果需要获取某一季度全部上市公司数据，请使用fina_mainbz_vip接口（参数一致），需积攒5000积分。
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	Y	股票代码
        - period	str	N	报告期(每个季度最后一天的日期,比如20171231表示年报)
        - type	str	N	类型：P按产品 D按地区 I按行业（请输入大写字母P或者D）
        - start_date	str	N	报告期开始日期
        - end_date	str	N	报告期结束日期

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	描述
        - ts_code	str	TS股票代码
        - ann_date	str	公告日期
        - end_date	str	报告期
        - mainbz_income	float	主营业务收入(元)
        - mainbz_cost	float	主营业务成本(元)
        - mainbz_profit	float	主营业务利润(元)
        - mainbz_tax	float	主营业务税金及附加(元)
        - mainbz_profit_margin	float	主营业务利润率(%)
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")

    # 参数检查
    if not ts_code:
        # 股票代码不能为空
        raise ValueError("股票代码不能为空")

    try:
        # 获取上市公司主营业务构成数据
        fina_mainbz = pro.fina_mainbz(ts_code=ts_code, period=period,
                                     type=type, start_date=start_date, end_date=end_date)
        
        return fina_mainbz
    except Exception as e:
        print(f"获取上市公司主营业务构成数据错误: {str(e)}")
        raise Exception(f"获取上市公司主营业务构成数据错误: {str(e)}")


def get_disclosure_date(ts_code: str = None, end_date: str = None,
                        pre_date: str = None, actual_adte: str = None) -> pd.DataFrame:
    """
    disclosure_date
        接口：disclosure_date
        描述：获取财报披露计划日期
        限量：单次最大3000，总量不限制
        积分：用户需要至少500积分才可以调取，积分越多权限越大，具体请参阅积分获取办法
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	TS股票代码
        - end_date	str	N	财报周期（每个季度最后一天的日期，比如20181231表示2018年年报，20180630表示中报)
        - pre_date	str	N	计划披露日期
        - actual_date	str	N	实际披露日期

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS代码
        - ann_date	str	Y	最新披露公告日
        - end_date	str	Y	报告期
        - pre_date	str	Y	预计披露日期
        - actual_date	str	Y	实际披露日期
        - modify_date	str	N	披露日期修正记录
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")

    try:
        # 获取财报披露计划日期
        disclosure_date = pro.disclosure_date(ts_code=ts_code,
                                                end_date=end_date, pre_date=pre_date,
                                                actual_date=actual_adte)
        
        return disclosure_date
    except Exception as e:
        print(f"获取财报披露计划日期数据错误: {str(e)}")
        raise Exception(f"获取财报披露计划日期数据错误: {str(e)}")