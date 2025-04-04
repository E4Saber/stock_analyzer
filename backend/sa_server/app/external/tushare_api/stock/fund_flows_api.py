import pandas as pd
from app.external.tushare_client import get_tushare_client


# 获取Tushare API实例
pro = get_tushare_client()


def get_moneyflow(ts_code: str = None, trade_date: str = None,
                    start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    moneyflow
        接口：moneyflow，可以通过数据工具调试和查看数据。
        描述：获取沪深A股票资金流向数据，分析大单小单成交情况，用于判别资金动向，数据开始于2010年。
        限量：单次最大提取6000行记录，总量不限制
        积分：用户需要至少2000积分才可以调取，基础积分有流量控制，积分越多权限越大，请自行提高积分，具体请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码 （股票和时间参数至少输入一个）
        - trade_date	str	N	交易日期
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期

    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS代码
        - trade_date	str	Y	交易日期
        - buy_sm_vol	int	Y	小单买入量（手）
        - buy_sm_amount	float	Y	小单买入金额（万元）
        - sell_sm_vol	int	Y	小单卖出量（手）
        - sell_sm_amount	float	Y	小单卖出金额（万元）
        - buy_md_vol	int	Y	中单买入量（手）
        - buy_md_amount	float	Y	中单买入金额（万元）
        - sell_md_vol	int	Y	中单卖出量（手）
        - sell_md_amount	float	Y	中单卖出金额（万元）
        - buy_lg_vol	int	Y	大单买入量（手）
        - buy_lg_amount	float	Y	大单买入金额（万元）
        - sell_lg_vol	int	Y	大单卖出量（手）
        - sell_lg_amount	float	Y	大单卖出金额（万元）
        - buy_elg_vol	int	Y	特大单买入量（手）
        - buy_elg_amount	float	Y	特大单买入金额（万元）
        - sell_elg_vol	int	Y	特大单卖出量（手）
        - sell_elg_amount	float	Y	特大单卖出金额（万元）
        - net_mf_vol	int	Y	净流入量（手）
        - net_mf_amount	float	Y	净流入额（万元）

        各类别统计规则如下：
        小单：5万以下 中单：5万～20万 大单：20万～100万 特大单：成交额>=100万 ，数据基于主动买卖单统计
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取沪深A股票资金流向
        moneyflow = pro.moneyflow(ts_code=ts_code, trade_date=trade_date,
                                    start_date=start_date, end_date=end_date)

        return moneyflow
    except Exception as e:
        print(f"获取沪深A股票资金流向数据错误: {str(e)}")
        raise Exception(f"获取沪深A股票资金流向数据错误: {str(e)}")


def get_moneyflow_ths(ts_code: str = None, trade_date: str = None,
                        start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    moneyflow_ths
        接口：moneyflow_ths
        描述：获取同花顺个股资金流向数据，每日盘后更新
        限量：单次最大6000，可根据日期或股票代码循环提取数据
        积分：用户需要至少5000积分才可以调取，具体请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码 （股票和时间参数至少输入一个）
        - trade_date	str	N	交易日期
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期

    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - trade_date	str	Y	交易日期
        - ts_code	str	Y	股票代码
        - name	str	Y	股票名称
        - pct_change	float	Y	涨跌幅
        - latest	float	Y	最新价
        - net_amount	float	Y	资金净流入(万元)
        - net_d5_amount	float	Y	5日主力净额(万元)
        - buy_lg_amount	float	Y	今日大单净流入额(万元)
        - buy_lg_amount_rate	float	Y	今日大单净流入占比(%)
        - buy_md_amount	float	Y	今日中单净流入额(万元)
        - buy_md_amount_rate	float	Y	今日中单净流入占比(%)
        - buy_sm_amount	float	Y	今日小单净流入额(万元)
        - buy_sm_amount_rate	float	Y	今日小单净流入占比(%)
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取同花顺个股资金流向
        moneyflow_ths = pro.moneyflow_ths(ts_code=ts_code, trade_date=trade_date,
                                            start_date=start_date, end_date=end_date)

        return moneyflow_ths
    except Exception as e:
        print(f"获取同花顺个股资金流向数据错误: {str(e)}")
        raise Exception(f"获取同花顺个股资金流向数据错误: {str(e)}")
    

def get_moneyflow_dc(ts_code: str = None, trade_date: str = None,
                        start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    moneyflow_dc
        接口：moneyflow_dc
        描述：获取东方财富个股资金流向数据，每日盘后更新，数据开始于20230911
        限量：单次最大获取6000条数据，可根据日期或股票代码循环提取数据
        积分：用户需要至少5000积分才可以调取，具体请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码 （股票和时间参数至少输入一个）
        - trade_date	str	N	交易日期
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期
    
    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - trade_date	str	Y	交易日期
        - ts_code	str	Y	股票代码
        - name	str	Y	股票名称
        - pct_change	float	Y	涨跌幅
        - close	float	Y	最新价
        - net_amount	float	Y	今日主力净流入额（万元）
        - net_amount_rate	float	Y	今日主力净流入净占比（%）
        - buy_elg_amount	float	Y	今日超大单净流入额（万元）
        - buy_elg_amount_rate	float	Y	今日超大单净流入占比（%）
        - buy_lg_amount	float	Y	今日大单净流入额（万元）
        - buy_lg_amount_rate	float	Y	今日大单净流入占比（%）
        - buy_md_amount	float	Y	今日中单净流入额（万元）
        - buy_md_amount_rate	float	Y	今日中单净流入占比（%）
        - buy_sm_amount	float	Y	今日小单净流入额（万元）
        - buy_sm_amount_rate	float	Y	今日小单净流入占比（%）
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取东方财富个股资金流向
        moneyflow_dc = pro.moneyflow_dc(ts_code=ts_code, trade_date=trade_date,
                                            start_date=start_date, end_date=end_date)

        return moneyflow_dc
    except Exception as e:
        print(f"获取东方财富个股资金流向数据错误: {str(e)}")
        raise Exception(f"获取东方财富个股资金流向数据错误: {str(e)}")


def get_moneyflow_cnt_ths(ts_code: str = None, trade_date: str = None,
                            start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    moneyflow_cnt_ths
        接口：moneyflow_cnt_ths
        描述：获取同花顺概念板块每日资金流向
        限量：单次最大可调取5000条数据，可以根据日期和代码循环提取全部数据
        积分：5000积分可以调取，具体请参阅积分获取办法
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码 （股票和时间参数至少输入一个）
        - trade_date	str	N	交易日期
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期
    
    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - trade_date	str	Y	交易日期
        - ts_code	str	Y	板块代码
        - name	str	Y	板块名称
        - lead_stock	str	Y	领涨股票名称
        - close_price	float	Y	最新价
        - pct_change	float	Y	行业涨跌幅
        - index_close	float	Y	板块指数
        - company_num	int	Y	公司数量
        - pct_change_stock	float	Y	领涨股涨跌幅
        - net_buy_amount	float	Y	流入资金(元)
        - net_sell_amount	float	Y	流出资金(元)
        - net_amount	float	Y	净额(元)
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取同花顺概念板块每日资金流向
        moneyflow_cnt_ths = pro.moneyflow_cnt_ths(ts_code=ts_code, trade_date=trade_date,
                                                    start_date=start_date, end_date=end_date)

        return moneyflow_cnt_ths
    except Exception as e:
        print(f"获取同花顺概念板块每日资金流向数据错误: {str(e)}")
        raise Exception(f"获取同花顺概念板块每日资金流向数据错误: {str(e)}")
    

def get_moneyflow_ind_ths(ts_code: str = None, trade_date: str = None,
                            start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    moneyflow_ind_ths
        接口：moneyflow_ind_ths
        描述：获取同花顺行业资金流向，每日盘后更新
        限量：单次最大可调取5000条数据，可以根据日期和代码循环提取全部数据
        积分：5000积分可以调取，具体请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码 （股票和时间参数至少输入一个）
        - trade_date	str	N	交易日期
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期
    
    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - trade_date	str	Y	交易日期
        - ts_code	str	Y	板块代码
        - industry	str	Y	板块名称
        - lead_stock	str	Y	领涨股票名称
        - close	float	Y	收盘指数
        - pct_change	float	Y	指数涨跌幅
        - company_num	int	Y	公司数量
        - pct_change_stock	float	Y	领涨股涨跌幅
        - close_price	float	Y	领涨股最新价
        - net_buy_amount	float	Y	流入资金(亿元)
        - net_sell_amount	float	Y	流出资金(亿元)
        - net_amount	float	Y	净额(元)
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取同花顺行业资金流向
        moneyflow_ind_ths = pro.moneyflow_ind_ths(ts_code=ts_code, trade_date=trade_date,
                                                    start_date=start_date, end_date=end_date)

        return moneyflow_ind_ths
    except Exception as e:
        print(f"获取同花顺行业资金流向数据错误: {str(e)}")
        raise Exception(f"获取同花顺行业资金流向数据错误: {str(e)}")


def get_moneyflow_ind_dc(ts_code: str = None, trade_date: str = None,
                            start_date: str = None, end_date: str = None, content_type: str = None) -> pd.DataFrame:
    """
    moneyflow_ind_dc
        接口：moneyflow_ind_dc
        描述：获取东方财富板块资金流向，每天盘后更新
        限量：单次最大可调取5000条数据，可以根据日期和代码循环提取全部数据
        积分：5000积分可以调取，具体请参阅积分获取办法
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	代码
        - trade_date	str	N	交易日期（YYYYMMDD格式，下同）
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期
        - content_type	str	N	资金类型(行业、概念、地域)
    
    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - trade_date	str	Y	交易日期
        - content_type	str	Y	数据类型
        - ts_code	str	Y	DC板块代码（行业、概念、地域）
        - name	str	Y	板块名称
        - pct_change	float	Y	板块涨跌幅（%）
        - close	float	Y	板块最新指数
        - net_amount	float	Y	今日主力净流入 净额（元）
        - net_amount_rate	float	Y	今日主力净流入净占比%
        - buy_elg_amount	float	Y	今日超大单净流入 净额（元）
        - buy_elg_amount_rate	float	Y	今日超大单净流入 净占比%
        - buy_lg_amount	float	Y	今日大单净流入 净额（元）
        - buy_lg_amount_rate	float	Y	今日大单净流入 净占比%
        - buy_md_amount	float	Y	今日中单净流入 净额（元）
        - buy_md_amount_rate	float	Y	今日中单净流入 净占比%
        - buy_sm_amount	float	Y	今日小单净流入 净额（元）
        - buy_sm_amount_rate	float	Y	今日小单净流入 净占比%
        - buy_sm_amount_stock	str	Y	今日主力净流入最大股
        - rank	int	Y	序号
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取东方财富板块资金流向
        moneyflow_ind_dc = pro.moneyflow_ind_dc(ts_code=ts_code, trade_date=trade_date,
                                                    start_date=start_date, end_date=end_date, content_type=content_type)

        return moneyflow_ind_dc
    except Exception as e:
        print(f"获取东方财富板块资金流向数据错误: {str(e)}")
        raise Exception(f"获取东方财富板块资金流向数据错误: {str(e)}")


def get_moneyflow_mkt_dc(trade_date: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    moneyflow_mkt_dc
        接口：moneyflow_mkt_dc
        描述：获取东方财富大盘资金流向数据，每日盘后更新
        限量：单次最大3000条，可根据日期或日期区间循环获取
        积分：120积分可试用，5000积分可正式调取，具体请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - trade_date	str	N	交易日期(YYYYMMDD格式，下同）
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期
    
    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - trade_date	str	Y	交易日期
        - close_sh	float	Y	上证收盘价（点）
        - pct_change_sh	float	Y	上证涨跌幅(%)
        - close_sz	float	Y	深证收盘价（点）
        - pct_change_sz	float	Y	深证涨跌幅(%)
        - net_amount	float	Y	今日主力净流入 净额（元）
        - net_amount_rate	float	Y	今日主力净流入净占比%
        - buy_elg_amount	float	Y	今日超大单净流入 净额（元）
        - buy_elg_amount_rate	float	Y	今日超大单净流入 净占比%
        - buy_lg_amount	float	Y	今日大单净流入 净额（元）
        - buy_lg_amount_rate	float	Y	今日大单净流入 净占比%
        - buy_md_amount	float	Y	今日中单净流入 净额（元）
        - buy_md_amount_rate	float	Y	今日中单净流入 净占比%
        - buy_sm_amount	float	Y	今日小单净流入 净额（元）
        - buy_sm_amount_rate	float	Y	今日小单净流入 净占比%
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取东方财富大盘资金流向
        moneyflow_mkt_dc = pro.moneyflow_mkt_dc(trade_date=trade_date, start_date=start_date, end_date=end_date)
        
        return moneyflow_mkt_dc
    except Exception as e:
        print(f"获取东方财富大盘资金流向数据错误: {str(e)}")
        raise Exception(f"获取东方财富大盘资金流向数据错误: {str(e)}")


def get_moneyflow_hsgt(trade_date: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    moneyflow_hsgt
        接口：moneyflow_hsgt，可以通过数据工具调试和查看数据。
        描述：获取沪股通、深股通、港股通每日资金流向数据，每次最多返回300条记录，总量不限制。每天18~20点之间完成当日更新
        积分要求：2000积分起，5000积分每分钟可提取500次

    输入参数：
        名称	类型	必选	描述
        - trade_date	str	N	交易日期 (二选一)
        - start_date	str	N	开始日期 (二选一)
        - end_date	str	N	结束日期
    
    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	描述
        - trade_date	str	交易日期
        - ggt_ss	float	港股通（上海）
        - ggt_sz	float	港股通（深圳）
        - hgt	float	沪股通（百万元）
        - sgt	float	深股通（百万元）
        - north_money	float	北向资金（百万元）
        - south_money	float	南向资金（百万元）
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取获取沪股通、深股通、港股通每日资金流向
        moneyflow_hsgt = pro.moneyflow_hsgt(trade_date=trade_date, start_date=start_date, end_date=end_date)

        return moneyflow_hsgt
    except Exception as e:
        print(f"获取获取沪股通、深股通、港股通每日资金流向数据错误: {str(e)}")
        raise Exception(f"获取获取沪股通、深股通、港股通每日资金流向数据错误: {str(e)}")