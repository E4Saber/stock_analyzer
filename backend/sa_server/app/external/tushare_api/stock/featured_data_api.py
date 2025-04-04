import pandas as pd
from app.external.tushare_client import get_tushare_client


# 获取Tushare API实例
pro = get_tushare_client()


def get_report_rc(ts_code: str = None, report_date: str = None,
                    start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    report_rc
        接口：report_rc
        描述：获取券商（卖方）每天研报的盈利预测数据，数据从2010年开始，每晚19~22点更新当日数据
        限量：单次最大3000条，可分页和循环提取所有数据
        权限：本接口120积分可以试用，每天10次请求，正式权限需8000积分，每天可请求100000次，10000积分以上无总量限制。
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码
        - report_date	str	N	报告日期（YYYYMMDD）
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	股票代码
        - name	str	Y	股票名称
        - report_date	str	Y	研报日期
        - report_title	str	Y	报告标题
        - report_type	str	Y	报告类型
        - classify	str	Y	报告分类
        - org_name	str	Y	机构名称
        - author_name	str	Y	作者
        - quarter	str	Y	预测报告期
        - op_rt	float	Y	预测营业收入（万元）
        - op_pr	float	Y	预测营业利润（万元）
        - tp	float	Y	预测利润总额（万元）
        - np	float	Y	预测净利润（万元）
        - eps	float	Y	预测每股收益（元）
        - pe	float	Y	预测市盈率
        - rd	float	Y	预测股息率
        - roe	float	Y	预测净资产收益率
        - ev_ebitda	float	Y	预测EV/EBITDA
        - rating	str	Y	卖方评级
        - max_price	float	Y	预测最高目标价
        - min_price	float	Y	预测最低目标价
        - imp_dg	str	N	机构关注度
        - create_time	datetime	N	TS数据更新时间
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取券商（卖方）每天研报的盈利预测数据
        report_rc = pro.report_rc(ts_code=ts_code, report_date=report_date,
                                   start_date=start_date, end_date=end_date)
        
        return report_rc
    except Exception as e:
        print(f"获取券商（卖方）每天研报的盈利预测数据错误: {str(e)}")
        raise Exception(f"获取券商（卖方）每天研报的盈利预测数据错误: {str(e)}")


def get_cyq_perf(ts_code: str = None, trade_date: str = None,
                    start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    cyq_perf
        接口：cyq_perf
        描述：获取A股每日筹码平均成本和胜率情况，每天17~18点左右更新，数据从2018年开始
        来源：Tushare社区
        限量：单次最大5000条，可以分页或者循环提取
        积分：120积分可以试用(查看数据)，5000积分每天20000次，10000积分每天200000次，15000积分每天不限总量
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码
        - trade_date	str	N	交易日期（YYYYMMDD）
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	股票代码
        - trade_date	str	Y	交易日期
        - his_low	float	Y	历史最低价
        - his_high	float	Y	历史最高价
        - cost_5pct	float	Y	5分位成本
        - cost_15pct	float	Y	15分位成本
        - cost_50pct	float	Y	50分位成本
        - cost_85pct	float	Y	85分位成本
        - cost_95pct	float	Y	95分位成本
        - weight_avg	float	Y	加权平均成本
        - winner_rate	float	Y	胜率
   """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取A股每日筹码平均成本和胜率情况
        cyq_perf = pro.cyq_perf(ts_code=ts_code, trade_date=trade_date,
                                 start_date=start_date, end_date=end_date)
        
        return cyq_perf
    except Exception as e:
        print(f"获取A股每日筹码平均成本和胜率数据错误: {str(e)}")
        raise Exception(f"获取A股每日筹码平均成本和胜率数据错误: {str(e)}")


def get_cyq_chips(ts_code: str = None, trade_date: str = None,
                    start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    cyq_chips
        接口：cyq_chips
        描述：获取A股每日的筹码分布情况，提供各价位占比，数据从2018年开始，每天17~18点之间更新当日数据
        来源：Tushare社区
        限量：单次最大2000条，可以按股票代码和日期循环提取
        积分：120积分可以试用查看数据，5000积分每天20000次，10000积分每天200000次，15000积分每天不限总量
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码
        - trade_date	str	N	交易日期（YYYYMMDD）
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	股票代码
        - trade_date	str	Y	交易日期
        - price	float	Y	成本价格
        - percent	float	Y	价格占比（%）
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取A股每日筹码分布数据
        cyq_chips = pro.cyq_chips(ts_code=ts_code, trade_date=trade_date,
                                   start_date=start_date, end_date=end_date)
        
        return cyq_chips
    except Exception as e:
        print(f"获取A股每日筹码分布数据错误: {str(e)}")
        raise Exception(f"获取A股每日筹码分布数据错误: {str(e)}")


def get_stk_factor(ts_code: str = None, trade_date: str = None,
                    start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    stk_factor
        接口：stk_factor
        描述：获取股票每日技术面因子数据，用于跟踪股票当前走势情况，数据由Tushare社区自产，覆盖全历史
        限量：单次最大10000条，可以循环或者分页提取
        积分：5000积分每分钟可以请求100次，8000积分以上每分钟500次，具体请参阅积分获取办法

        注：
        1、本接口的前复权行情是从最新一个交易日开始往前复权，跟行情软件一致。
        2、pro_bar接口的前复权是动态复权，即以end_date参数开始往前复权，与本接口会存在不一致的可能，属正常。
        3、本接口技术指标都是基于前复权价格计算。
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码
        - trade_date	str	N	交易日期（YYYYMMDD）
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	股票代码
        - trade_date	str	Y	交易日期
        - close	float	Y	收盘价
        - open	float	Y	开盘价
        - high	float	Y	最高价
        - low	float	Y	最低价
        - pre_close	float	Y	昨收价
        - change	float	Y	涨跌额
        - pct_change	float	Y	涨跌幅
        - vol	float	Y	成交量 （手）
        - amount	float	Y	成交额 （千元）
        - adj_factor	float	Y	复权因子
        - open_hfq	float	Y	开盘价后复权
        - open_qfq	float	Y	开盘价前复权
        - close_hfq	float	Y	收盘价后复权
        - close_qfq	float	Y	收盘价前复权
        - high_hfq	float	Y	最高价后复权
        - high_qfq	float	Y	最高价前复权
        - low_hfq	float	Y	最低价后复权
        - low_qfq	float	Y	最低价前复权
        - pre_close_hfq	float	Y	昨收价后复权
        - pre_close_qfq	float	Y	昨收价前复权
        - macd_dif	float	Y	MCAD_DIF (基于前复权价格计算，下同)
        - macd_dea	float	Y	MCAD_DEA
        - macd	float	Y	MCAD
        - kdj_k	float	Y	KDJ_K
        - kdj_d	float	Y	KDJ_D
        - kdj_j	float	Y	KDJ_J
        - rsi_6	float	Y	RSI_6
        - rsi_12	float	Y	RSI_12
        - rsi_24	float	Y	RSI_24
        - boll_upper	float	Y	BOLL_UPPER
        - boll_mid	float	Y	BOLL_MID
        - boll_lower	float	Y	BOLL_LOWER
        - cci	float	Y	CCI
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取A股每日个股技术面因子数据
        stk_factor = pro.stk_factor(ts_code=ts_code, trade_date=trade_date,
                                     start_date=start_date, end_date=end_date)
        
        return stk_factor
    except Exception as e:
        print(f"获取A股每日个股技术面因子数据错误: {str(e)}")
        raise Exception(f"获取A股每日个股技术面因子数据错误: {str(e)}")

def get_stk_factor_pro(ts_code: str = None, trade_date: str = None,
                    start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    stk_factor_pro
        接口：stk_factor_pro
        描述：获取股票每日技术面因子数据，用于跟踪股票当前走势情况，数据由Tushare社区自产，覆盖全历史；输出参数_bfq表示不复权，_qfq表示前复权 _hfq表示后复权，描述中说明了因子的默认传参，如需要特殊参数或者更多因子可以联系管理员评估
        限量：单次最大10000
        积分：5000积分每分钟可以请求30次，8000积分以上每分钟500次，具体请参阅积分获取办法
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码
        - trade_date	str	N	交易日期（YYYYMMDD）
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	股票代码
        - trade_date	str	Y	交易日期
        - open	float	Y	开盘价
        - open_hfq	float	Y	开盘价（后复权）
        - open_qfq	float	Y	开盘价（前复权）
        - high	float	Y	最高价
        - high_hfq	float	Y	最高价（后复权）
        - high_qfq	float	Y	最高价（前复权）
        - low	float	Y	最低价
        - low_hfq	float	Y	最低价（后复权）
        - low_qfq	float	Y	最低价（前复权）
        - close	float	Y	收盘价
        - close_hfq	float	Y	收盘价（后复权）
        - close_qfq	float	Y	收盘价（前复权）
        - pre_close	float	Y	昨收价(前复权)--为daily接口的pre_close,以当时复权因子计算值跟前一日close_qfq对不上，可不用
        - change	float	Y	涨跌额
        - pct_chg	float	Y	涨跌幅 （未复权，如果是复权请用 通用行情接口 ）
        - vol	float	Y	成交量 （手）
        - amount	float	Y	成交额 （千元）
        - turnover_rate	float	Y	换手率（%）
        - turnover_rate_f	float	Y	换手率（自由流通股）
        - volume_ratio	float	Y	量比
        - pe	float	Y	市盈率（总市值/净利润， 亏损的PE为空）
        - pe_ttm	float	Y	市盈率（TTM，亏损的PE为空）
        - pb	float	Y	市净率（总市值/净资产）
        - ps	float	Y	市销率
        - ps_ttm	float	Y	市销率（TTM）
        - dv_ratio	float	Y	股息率 （%）
        - dv_ttm	float	Y	股息率（TTM）（%）
        - total_share	float	Y	总股本 （万股）
        - float_share	float	Y	流通股本 （万股）
        - free_share	float	Y	自由流通股本 （万）
        - total_mv	float	Y	总市值 （万元）
        - circ_mv	float	Y	流通市值（万元）
        - adj_factor	float	Y	复权因子
        - asi_bfq	float	Y	振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10
        - asi_hfq	float	Y	振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10
        - asi_qfq	float	Y	振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10
        - asit_bfq	float	Y	振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10
        - asit_hfq	float	Y	振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10
        - asit_qfq	float	Y	振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10
        - atr_bfq	float	Y	真实波动N日平均值-CLOSE, HIGH, LOW, N=20
        - atr_hfq	float	Y	真实波动N日平均值-CLOSE, HIGH, LOW, N=20
        - atr_qfq	float	Y	真实波动N日平均值-CLOSE, HIGH, LOW, N=20
        - bbi_bfq	float	Y	BBI多空指标-CLOSE, M1=3, M2=6, M3=12, M4=20
        - bbi_hfq	float	Y	BBI多空指标-CLOSE, M1=3, M2=6, M3=12, M4=21
        - bbi_qfq	float	Y	BBI多空指标-CLOSE, M1=3, M2=6, M3=12, M4=22
        - bias1_bfq	float	Y	BIAS乖离率-CLOSE, L1=6, L2=12, L3=24
        - bias1_hfq	float	Y	BIAS乖离率-CLOSE, L1=6, L2=12, L3=24
        - bias1_qfq	float	Y	BIAS乖离率-CLOSE, L1=6, L2=12, L3=24
        - bias2_bfq	float	Y	BIAS乖离率-CLOSE, L1=6, L2=12, L3=24
        - bias2_hfq	float	Y	BIAS乖离率-CLOSE, L1=6, L2=12, L3=24
        - bias2_qfq	float	Y	BIAS乖离率-CLOSE, L1=6, L2=12, L3=24
        - bias3_bfq	float	Y	BIAS乖离率-CLOSE, L1=6, L2=12, L3=24
        - bias3_hfq	float	Y	BIAS乖离率-CLOSE, L1=6, L2=12, L3=24
        - bias3_qfq	float	Y	BIAS乖离率-CLOSE, L1=6, L2=12, L3=24
        - boll_lower_bfq	float	Y	BOLL指标，布林带-CLOSE, N=20, P=2
        - boll_lower_hfq	float	Y	BOLL指标，布林带-CLOSE, N=20, P=2
        - boll_lower_qfq	float	Y	BOLL指标，布林带-CLOSE, N=20, P=2
        - boll_mid_bfq	float	Y	BOLL指标，布林带-CLOSE, N=20, P=2
        - boll_mid_hfq	float	Y	BOLL指标，布林带-CLOSE, N=20, P=2
        - boll_mid_qfq	float	Y	BOLL指标，布林带-CLOSE, N=20, P=2
        - boll_upper_bfq	float	Y	BOLL指标，布林带-CLOSE, N=20, P=2
        - boll_upper_hfq	float	Y	BOLL指标，布林带-CLOSE, N=20, P=2
        - boll_upper_qfq	float	Y	BOLL指标，布林带-CLOSE, N=20, P=2
        - brar_ar_bfq	float	Y	BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26
        - brar_ar_hfq	float	Y	BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26
        - brar_ar_qfq	float	Y	BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26
        - brar_br_bfq	float	Y	BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26
        - brar_br_hfq	float	Y	BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26
        - brar_br_qfq	float	Y	BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26
        - cci_bfq	float	Y	顺势指标又叫CCI指标-CLOSE, HIGH, LOW, N=14
        - cci_hfq	float	Y	顺势指标又叫CCI指标-CLOSE, HIGH, LOW, N=14
        - cci_qfq	float	Y	顺势指标又叫CCI指标-CLOSE, HIGH, LOW, N=14
        - cr_bfq	float	Y	CR价格动量指标-CLOSE, HIGH, LOW, N=20
        - cr_hfq	float	Y	CR价格动量指标-CLOSE, HIGH, LOW, N=20
        - cr_qfq	float	Y	CR价格动量指标-CLOSE, HIGH, LOW, N=20
        - dfma_dif_bfq	float	Y	平行线差指标-CLOSE, N1=10, N2=50, M=10
        - dfma_dif_hfq	float	Y	平行线差指标-CLOSE, N1=10, N2=50, M=10
        - dfma_dif_qfq	float	Y	平行线差指标-CLOSE, N1=10, N2=50, M=10
        - dfma_difma_bfq	float	Y	平行线差指标-CLOSE, N1=10, N2=50, M=10
        - dfma_difma_hfq	float	Y	平行线差指标-CLOSE, N1=10, N2=50, M=10
        - dfma_difma_qfq	float	Y	平行线差指标-CLOSE, N1=10, N2=50, M=10
        - dmi_adx_bfq	float	Y	动向指标-CLOSE, HIGH, LOW, M1=14, M2=6
        - dmi_adx_hfq	float	Y	动向指标-CLOSE, HIGH, LOW, M1=14, M2=6
        - dmi_adx_qfq	float	Y	动向指标-CLOSE, HIGH, LOW, M1=14, M2=6
        - dmi_adxr_bfq	float	Y	动向指标-CLOSE, HIGH, LOW, M1=14, M2=6
        - dmi_adxr_hfq	float	Y	动向指标-CLOSE, HIGH, LOW, M1=14, M2=6
        - dmi_adxr_qfq	float	Y	动向指标-CLOSE, HIGH, LOW, M1=14, M2=6
        - dmi_mdi_bfq	float	Y	动向指标-CLOSE, HIGH, LOW, M1=14, M2=6
        - dmi_mdi_hfq	float	Y	动向指标-CLOSE, HIGH, LOW, M1=14, M2=6
        - dmi_mdi_qfq	float	Y	动向指标-CLOSE, HIGH, LOW, M1=14, M2=6
        - dmi_pdi_bfq	float	Y	动向指标-CLOSE, HIGH, LOW, M1=14, M2=6
        - dmi_pdi_hfq	float	Y	动向指标-CLOSE, HIGH, LOW, M1=14, M2=6
        - dmi_pdi_qfq	float	Y	动向指标-CLOSE, HIGH, LOW, M1=14, M2=6
        - downdays	float	Y	连跌天数
        - updays	float	Y	连涨天数
        - dpo_bfq	float	Y	区间震荡线-CLOSE, M1=20, M2=10, M3=6
        - dpo_hfq	float	Y	区间震荡线-CLOSE, M1=20, M2=10, M3=6
        - dpo_qfq	float	Y	区间震荡线-CLOSE, M1=20, M2=10, M3=6
        - madpo_bfq	float	Y	区间震荡线-CLOSE, M1=20, M2=10, M3=6
        - madpo_hfq	float	Y	区间震荡线-CLOSE, M1=20, M2=10, M3=6
        - madpo_qfq	float	Y	区间震荡线-CLOSE, M1=20, M2=10, M3=6
        - ema_bfq_10	float	Y	指数移动平均-N=10
        - ema_bfq_20	float	Y	指数移动平均-N=20
        - ema_bfq_250	float	Y	指数移动平均-N=250
        - ema_bfq_30	float	Y	指数移动平均-N=30
        - ema_bfq_5	float	Y	指数移动平均-N=5
        - ema_bfq_60	float	Y	指数移动平均-N=60
        - ema_bfq_90	float	Y	指数移动平均-N=90
        - ema_hfq_10	float	Y	指数移动平均-N=10
        - ema_hfq_20	float	Y	指数移动平均-N=20
        - ema_hfq_250	float	Y	指数移动平均-N=250
        - ema_hfq_30	float	Y	指数移动平均-N=30
        - ema_hfq_5	float	Y	指数移动平均-N=5
        - ema_hfq_60	float	Y	指数移动平均-N=60
        - ema_hfq_90	float	Y	指数移动平均-N=90
        - ema_qfq_10	float	Y	指数移动平均-N=10
        - ema_qfq_20	float	Y	指数移动平均-N=20
        - ema_qfq_250	float	Y	指数移动平均-N=250
        - ema_qfq_30	float	Y	指数移动平均-N=30
        - ema_qfq_5	float	Y	指数移动平均-N=5
        - ema_qfq_60	float	Y	指数移动平均-N=60
        - ema_qfq_90	float	Y	指数移动平均-N=90
        - emv_bfq	float	Y	简易波动指标-HIGH, LOW, VOL, N=14, M=9
        - emv_hfq	float	Y	简易波动指标-HIGH, LOW, VOL, N=14, M=9
        - emv_qfq	float	Y	简易波动指标-HIGH, LOW, VOL, N=14, M=9
        - maemv_bfq	float	Y	简易波动指标-HIGH, LOW, VOL, N=14, M=9
        - maemv_hfq	float	Y	简易波动指标-HIGH, LOW, VOL, N=14, M=9
        - maemv_qfq	float	Y	简易波动指标-HIGH, LOW, VOL, N=14, M=9
        - expma_12_bfq	float	Y	EMA指数平均数指标-CLOSE, N1=12, N2=50
        - expma_12_hfq	float	Y	EMA指数平均数指标-CLOSE, N1=12, N2=50
        - expma_12_qfq	float	Y	EMA指数平均数指标-CLOSE, N1=12, N2=50
        - expma_50_bfq	float	Y	EMA指数平均数指标-CLOSE, N1=12, N2=50
        - expma_50_hfq	float	Y	EMA指数平均数指标-CLOSE, N1=12, N2=50
        - expma_50_qfq	float	Y	EMA指数平均数指标-CLOSE, N1=12, N2=50
        - kdj_bfq	float	Y	KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3
        - kdj_hfq	float	Y	KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3
        - kdj_qfq	float	Y	KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3
        - kdj_d_bfq	float	Y	KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3
        - kdj_d_hfq	float	Y	KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3
        - kdj_d_qfq	float	Y	KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3
        - kdj_k_bfq	float	Y	KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3
        - kdj_k_hfq	float	Y	KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3
        - kdj_k_qfq	float	Y	KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3
        - ktn_down_bfq	float	Y	肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10
        - ktn_down_hfq	float	Y	肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10
        - ktn_down_qfq	float	Y	肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10
        - ktn_mid_bfq	float	Y	肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10
        - ktn_mid_hfq	float	Y	肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10
        - ktn_mid_qfq	float	Y	肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10
        - ktn_upper_bfq	float	Y	肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10
        - ktn_upper_hfq	float	Y	肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10
        - ktn_upper_qfq	float	Y	肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10
        - lowdays	float	Y	LOWRANGE(LOW)表示当前最低价是近多少周期内最低价的最小值
        - topdays	float	Y	TOPRANGE(HIGH)表示当前最高价是近多少周期内最高价的最大值
        - ma_bfq_10	float	Y	简单移动平均-N=10
        - ma_bfq_20	float	Y	简单移动平均-N=20
        - ma_bfq_250	float	Y	简单移动平均-N=250
        - ma_bfq_30	float	Y	简单移动平均-N=30
        - ma_bfq_5	float	Y	简单移动平均-N=5
        - ma_bfq_60	float	Y	简单移动平均-N=60
        - ma_bfq_90	float	Y	简单移动平均-N=90
        - ma_hfq_10	float	Y	简单移动平均-N=10
        - ma_hfq_20	float	Y	简单移动平均-N=20
        - ma_hfq_250	float	Y	简单移动平均-N=250
        - ma_hfq_30	float	Y	简单移动平均-N=30
        - ma_hfq_5	float	Y	简单移动平均-N=5
        - ma_hfq_60	float	Y	简单移动平均-N=60
        - ma_hfq_90	float	Y	简单移动平均-N=90
        - ma_qfq_10	float	Y	简单移动平均-N=10
        - ma_qfq_20	float	Y	简单移动平均-N=20
        - ma_qfq_250	float	Y	简单移动平均-N=250
        - ma_qfq_30	float	Y	简单移动平均-N=30
        - ma_qfq_5	float	Y	简单移动平均-N=5
        - ma_qfq_60	float	Y	简单移动平均-N=60
        - ma_qfq_90	float	Y	简单移动平均-N=90
        - macd_bfq	float	Y	MACD指标-CLOSE, SHORT=12, LONG=26, M=9
        - macd_hfq	float	Y	MACD指标-CLOSE, SHORT=12, LONG=26, M=9
        - macd_qfq	float	Y	MACD指标-CLOSE, SHORT=12, LONG=26, M=9
        - macd_dea_bfq	float	Y	MACD指标-CLOSE, SHORT=12, LONG=26, M=9
        - macd_dea_hfq	float	Y	MACD指标-CLOSE, SHORT=12, LONG=26, M=9
        - macd_dea_qfq	float	Y	MACD指标-CLOSE, SHORT=12, LONG=26, M=9
        - macd_dif_bfq	float	Y	MACD指标-CLOSE, SHORT=12, LONG=26, M=9
        - macd_dif_hfq	float	Y	MACD指标-CLOSE, SHORT=12, LONG=26, M=9
        - macd_dif_qfq	float	Y	MACD指标-CLOSE, SHORT=12, LONG=26, M=9
        - mass_bfq	float	Y	梅斯线-HIGH, LOW, N1=9, N2=25, M=6
        - mass_hfq	float	Y	梅斯线-HIGH, LOW, N1=9, N2=25, M=6
        - mass_qfq	float	Y	梅斯线-HIGH, LOW, N1=9, N2=25, M=6
        - ma_mass_bfq	float	Y	梅斯线-HIGH, LOW, N1=9, N2=25, M=6
        - ma_mass_hfq	float	Y	梅斯线-HIGH, LOW, N1=9, N2=25, M=6
        - ma_mass_qfq	float	Y	梅斯线-HIGH, LOW, N1=9, N2=25, M=6
        - mfi_bfq	float	Y	MFI指标是成交量的RSI指标-CLOSE, HIGH, LOW, VOL, N=14
        - mfi_hfq	float	Y	MFI指标是成交量的RSI指标-CLOSE, HIGH, LOW, VOL, N=14
        - mfi_qfq	float	Y	MFI指标是成交量的RSI指标-CLOSE, HIGH, LOW, VOL, N=14
        - mtm_bfq	float	Y	动量指标-CLOSE, N=12, M=6
        - mtm_hfq	float	Y	动量指标-CLOSE, N=12, M=6
        - mtm_qfq	float	Y	动量指标-CLOSE, N=12, M=6
        - mtmma_bfq	float	Y	动量指标-CLOSE, N=12, M=6
        - mtmma_hfq	float	Y	动量指标-CLOSE, N=12, M=6
        - mtmma_qfq	float	Y	动量指标-CLOSE, N=12, M=6
        - obv_bfq	float	Y	能量潮指标-CLOSE, VOL
        - obv_hfq	float	Y	能量潮指标-CLOSE, VOL
        - obv_qfq	float	Y	能量潮指标-CLOSE, VOL
        - psy_bfq	float	Y	投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6
        - psy_hfq	float	Y	投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6
        - psy_qfq	float	Y	投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6
        - psyma_bfq	float	Y	投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6
        - psyma_hfq	float	Y	投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6
        - psyma_qfq	float	Y	投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6
        - roc_bfq	float	Y	变动率指标-CLOSE, N=12, M=6
        - roc_hfq	float	Y	变动率指标-CLOSE, N=12, M=6
        - roc_qfq	float	Y	变动率指标-CLOSE, N=12, M=6
        - maroc_bfq	float	Y	变动率指标-CLOSE, N=12, M=6
        - maroc_hfq	float	Y	变动率指标-CLOSE, N=12, M=6
        - maroc_qfq	float	Y	变动率指标-CLOSE, N=12, M=6
        - rsi_bfq_12	float	Y	RSI指标-CLOSE, N=12
        - rsi_bfq_24	float	Y	RSI指标-CLOSE, N=24
        - rsi_bfq_6	float	Y	RSI指标-CLOSE, N=6
        - rsi_hfq_12	float	Y	RSI指标-CLOSE, N=12
        - rsi_hfq_24	float	Y	RSI指标-CLOSE, N=24
        - rsi_hfq_6	float	Y	RSI指标-CLOSE, N=6
        - rsi_qfq_12	float	Y	RSI指标-CLOSE, N=12
        - rsi_qfq_24	float	Y	RSI指标-CLOSE, N=24
        - rsi_qfq_6	float	Y	RSI指标-CLOSE, N=6
        - taq_down_bfq	float	Y	唐安奇通道(海龟)交易指标-HIGH, LOW, 20
        - taq_down_hfq	float	Y	唐安奇通道(海龟)交易指标-HIGH, LOW, 20
        - taq_down_qfq	float	Y	唐安奇通道(海龟)交易指标-HIGH, LOW, 20
        - taq_mid_bfq	float	Y	唐安奇通道(海龟)交易指标-HIGH, LOW, 20
        - taq_mid_hfq	float	Y	唐安奇通道(海龟)交易指标-HIGH, LOW, 20
        - taq_mid_qfq	float	Y	唐安奇通道(海龟)交易指标-HIGH, LOW, 20
        - taq_up_bfq	float	Y	唐安奇通道(海龟)交易指标-HIGH, LOW, 20
        - taq_up_hfq	float	Y	唐安奇通道(海龟)交易指标-HIGH, LOW, 20
        - taq_up_qfq	float	Y	唐安奇通道(海龟)交易指标-HIGH, LOW, 20
        - trix_bfq	float	Y	三重指数平滑平均线-CLOSE, M1=12, M2=20
        - trix_hfq	float	Y	三重指数平滑平均线-CLOSE, M1=12, M2=20
        - trix_qfq	float	Y	三重指数平滑平均线-CLOSE, M1=12, M2=20
        - trma_bfq	float	Y	三重指数平滑平均线-CLOSE, M1=12, M2=20
        - trma_hfq	float	Y	三重指数平滑平均线-CLOSE, M1=12, M2=20
        - trma_qfq	float	Y	三重指数平滑平均线-CLOSE, M1=12, M2=20
        - vr_bfq	float	Y	VR容量比率-CLOSE, VOL, M1=26
        - vr_hfq	float	Y	VR容量比率-CLOSE, VOL, M1=26
        - vr_qfq	float	Y	VR容量比率-CLOSE, VOL, M1=26
        - wr_bfq	float	Y	W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6
        - wr_hfq	float	Y	W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6
        - wr_qfq	float	Y	W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6
        - wr1_bfq	float	Y	W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6
        - wr1_hfq	float	Y	W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6
        - wr1_qfq	float	Y	W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6
        - xsii_td1_bfq	float	Y	薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7
        - xsii_td1_hfq	float	Y	薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7
        - xsii_td1_qfq	float	Y	薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7
        - xsii_td2_bfq	float	Y	薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7
        - xsii_td2_hfq	float	Y	薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7
        - xsii_td2_qfq	float	Y	薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7
        - xsii_td3_bfq	float	Y	薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7
        - xsii_td3_hfq	float	Y	薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7
        - xsii_td3_qfq	float	Y	薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7
        - xsii_td4_bfq	float	Y	薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7
        - xsii_td4_hfq	float	Y	薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7
        - xsii_td4_qfq	float	Y	薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取A股每日个股技术面因子数据
        stk_factor_pro = pro.stk_factor_pro(ts_code=ts_code, trade_date=trade_date,
                                            start_date=start_date, end_date=end_date)
        
        return stk_factor_pro
    except Exception as e:
        print(f"获取A股每日个股技术面因子数据错误: {str(e)}")
        raise Exception(f"获取A股每日个股技术面因子数据错误: {str(e)}")


def get_ccass_hold(ts_code: str = None, hk_code: str = None,
                   trade_date: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    ccass_hold
        接口：ccass_hold
        描述：获取中央结算系统持股汇总数据，覆盖全部历史数据，根据交易所披露时间，当日数据在下一交易日早上9点前完成入库
        限量：单次最大5000条数据，可循环或分页提供全部
        积分：用户120积分可以试用看数据，5000积分每分钟可以请求300次，8000积分以上可以请求500次每分钟，具体请参阅积分获取办法
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码 (e.g. 605009.SH)
        - hk_code	str	N	港交所代码 （e.g. 95009）
        - trade_date	str	N	交易日期(YYYYMMDD格式，下同)
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - trade_date	str	Y	交易日期
        - ts_code	str	Y	股票代号
        - name	str	Y	股票名称
        - shareholding	str	Y	于中央结算系统的持股量(股)
        - Shareholding in CCASS
        - hold_nums	str	Y	参与者数目（个）
        - hold_ratio	str	Y	占于上交所上市及交易的A股总数的百分比（%）
        - % of the total number of A shares listed and traded on the SSE
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取中央结算系统持股汇总
        ccass_hold = pro.ccass_hold(ts_code=ts_code, hk_code=hk_code,
                                            trade_date=trade_date, start_date=start_date, end_date=end_date)
        
        return ccass_hold
    except Exception as e:
        print(f"获取中央结算系统持股汇总数据错误: {str(e)}")
        raise Exception(f"获取中央结算系统持股汇总数据错误: {str(e)}")


def get_ccass_hold_detail(ts_code: str = None, hk_code: str = None,
                            trade_date: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    ccass_hold_detail
        接口：ccass_hold_detail
        描述：获取中央结算系统机构席位持股明细，数据覆盖全历史，根据交易所披露时间，当日数据在下一交易日早上9点前完成
        限量：单次最大返回6000条数据，可以循环或分页提取
        积分：用户积8000积分可调取，每分钟可以请求300次
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码 (e.g. 605009.SH)
        - hk_code	str	N	港交所代码 （e.g. 95009）
        - trade_date	str	N	交易日期(YYYYMMDD格式，下同)
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - trade_date	str	Y	交易日期
        - ts_code	str	Y	股票代号
        - name	str	Y	股票名称
        - col_participant_id	str	Y	参与者编号
        - col_participant_name	str	Y	机构名称
        - col_shareholding	str	Y	持股量(股)
        - col_shareholding_percent	str	Y	占已发行股份/权证/单位百分比(%)
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取中央结算系统机构席位持股明细
        ccass_hold_detail = pro.ccass_hold_detail(ts_code=ts_code, hk_code=hk_code,
                                                    trade_date=trade_date, start_date=start_date, end_date=end_date)
        
        return ccass_hold_detail
    except Exception as e:
        print(f"获取中央结算系统机构席位持股明细数据错误: {str(e)}")
        raise Exception(f"获取中央结算系统机构席位持股明细数据错误: {str(e)}")


def get_hk_hold(code: str = None, ts_code: str = None, trade_date: str = None,
                start_date: str = None, end_date: str = None, exchange: str = None) -> pd.DataFrame:
    """
    hk_hold
        接口：hk_hold，可以通过数据工具调试和查看数据。
        描述：获取沪深港股通持股明细，数据来源港交所。
        限量：单次最多提取3800条记录，可循环调取，总量不限制
        积分：用户积120积分可调取试用，2000积分可正常使用，单位分钟有流控，积分越高流量越大，请自行提高积分，具体请参阅积分获取办法

        说明：交易所于从2024年8月20开始停止发布北向资金数据

    输入参数：
        名称	类型	必选	描述
        - code	str	N	交易所代码
        - ts_code	str	N	TS股票代码
        - trade_date	str	N	交易日期
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期
        - exchange	str	N	类型：SH沪股通（北向）SZ深股通（北向）HK港股通（南向持股）

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - code	str	Y	原始代码
        - trade_date	str	Y	交易日期
        - ts_code	str	Y	TS代码
        - name	str	Y	股票名称
        - vol	int	Y	持股数量(股)
        - ratio	float	Y	持股占比（%），占已发行股份百分比
        - exchange	str	Y	类型：SH沪股通SZ深股通HK港股通
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取沪深港股通持股明细
        hk_hold = pro.hk_hold(code=code, ts_code=ts_code, trade_date=trade_date,
                                start_date=start_date, end_date=end_date, exchange=exchange)
        
        return hk_hold
    except Exception as e:
        print(f"获取沪深港股通持股明细数据错误: {str(e)}")
        raise Exception(f"获取沪深港股通持股明细数据错误: {str(e)}")


def get_stk_nineturn(ts_code: str = None, trade_date: str = None, freq: str = None,
                        start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    stk_nineturn
        接口：stk_nineturn，可以通过数据工具调试和查看数据。
        描述：获取个股九转数据，覆盖全历史数据，数据来源于交易所披露的公告
        限量：单次最多提取5000条记录，可循环调取，总量不限制
        积分：用户积120积分可调取试用，2000积分可正常使用，单位分钟有流控，积分越高流量越大，请自行提高积分，具体请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码
        - trade_date	str	N	交易日期 （格式：YYYY-MM-DD HH:MM:SS)
        - freq	str	N	频率(日daily,分钟60min)
        - start_date	str	N	开始时间
        - end_date	str	N	结束时间

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	股票代码
        - trade_date	datetime	Y	交易日期
        - freq	str	Y	频率(日daily,分钟60min)
        - open	float	Y	开盘价
        - high	float	Y	最高价
        - low	float	Y	最低价
        - close	float	Y	收盘价
        - vol	float	Y	成交量
        - amount	float	Y	成交额
        - up_count	float	Y	上九转计数
        - down_count	float	Y	下九转计数
        - nine_up_turn	str	Y	是否上九转)+9表示上九转
        - nine_down_turn	str	Y	是否下九转-9表示下九转
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取个股九转数据
        stk_nineturn = pro.stk_nineturn(ts_code=ts_code, trade_date=trade_date,
                                            start_date=start_date, end_date=end_date)
        
        return stk_nineturn
    except Exception as e:
        print(f"获取个股九转数据错误: {str(e)}")
        raise Exception(f"获取个股九转数据错误: {str(e)}")

def get_stk_surv(ts_code: str = None, trade_date: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    stk_surv
        接口：stk_surv
        描述：获取上市公司机构调研记录数据
        限量：单次最大获取100条数据，可循环或分页提取
        积分：用户积5000积分可使用

    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码
        - trade_date	str	N	调研日期
        - start_date	str	N	调研开始日期
        - end_date	str	N	调研结束日期

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	股票代码
        - name	str	Y	股票名称
        - surv_date	str	Y	调研日期
        - fund_visitors	str	Y	机构参与人员
        - rece_place	str	Y	接待地点
        - rece_mode	str	Y	接待方式
        - rece_org	str	Y	接待的公司
        - org_type	str	Y	接待公司类型
        - comp_rece	str	Y	上市公司接待人员
        - content	None	N	调研内容
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取上市公司机构调研记录数据
        stk_surv = pro.stk_surv(ts_code=ts_code, trade_date=trade_date,
                                    start_date=start_date, end_date=end_date)
        
        return stk_surv
    except Exception as e:
        print(f"获取上市公司机构调研记录数据错误: {str(e)}")
        raise Exception(f"获取上市公司机构调研记录数据错误: {str(e)}")


def get_broker_recommend(month: str = None) -> pd.DataFrame:
    """
    broker_recommend
        接口：broker_recommend
        描述：获取券商月度金股，一般1日~3日内更新当月数据
        限量：单次最大1000行数据，可循环提取
        积分：积分达到2000即可调用，具体请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - month	str	Y	月份(YYYYMM格式)

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - month	str	Y	月度
        - broker	str	Y	券商
        - ts_code	str	Y	股票代码
        - name	str	Y	股票简称
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    # month参数不能为空
    if month is None:
        raise ValueError("month参数不能为空")
    
    try:
        # 获取券商月度金股
        broker_recommend = pro.broker_recommend(month=month)
        
        return broker_recommend
    except Exception as e:
        print(f"获取券商月度金股数据错误: {str(e)}")
        raise Exception(f"获取券商月度金股数据错误: {str(e)}")

