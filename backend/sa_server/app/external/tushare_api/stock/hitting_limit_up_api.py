import pandas as pd
from app.external.tushare_client import get_tushare_client


# 获取Tushare API实例
pro = get_tushare_client()


def get_kpl_concept(trade_date: str = None, ts_code: str = None, name: str = None) -> pd.DataFrame:
    """
    kpl_concept
        接口：kpl_concept
        描述：获取开盘啦概念题材列表，每天盘后更新
        限量：单次最大5000条，可根据日期循环获取历史数据
        积分：5000积分可提取数据，具体请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - trade_date	str	N	交易日期（YYYYMMDD格式）
        - ts_code	str	N	题材代码（xxxxxx.KP格式）
        - name	str	N	题材名称（模糊匹配）
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - trade_date	str	Y	交易日期
        - ts_code	str	Y	题材代码
        - name	str	Y	题材名称
        - z_t_num	None	Y	涨停数量
        - up_num	str	Y	排名上升位数
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取开盘啦概念题材列表
        kpl_concept = pro.kpl_concept(trade_date=trade_date, ts_code=ts_code, name=name)
        
        return kpl_concept
    except Exception as e:
        print(f"获取开盘啦概念题材列表数据错误: {str(e)}")
        raise Exception(f"获取开盘啦概念题材列表数据错误: {str(e)}")


def get_kpl_concept_cons(trade_date: str = None, ts_code: str = None, con_code: str = None) -> pd.DataFrame:
    """
    kpl_concept_cons
        接口：kpl_concept_cons
        描述：获取开盘啦概念题材的成分股
        限量：单次最大3000条，可根据代码和日期循环获取全部数据
        积分：5000积分可提取数据，具体请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - trade_date	str	N	交易日期（YYYYMMDD格式）
        - ts_code	str	N	题材代码（xxxxxx.KP格式）
        - con_code	str	N	成分代码（xxxxxx.SH格式）
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	题材ID
        - name	str	Y	题材名称
        - con_name	str	Y	股票名称
        - con_code	str	Y	股票代码
        - trade_date	str	Y	交易日期
        - desc	str	Y	描述
        - hot_num	None	Y	人气值
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取开盘啦概念题材成分股列表
        kpl_concept_cons = pro.kpl_concept_cons(
            trade_date=trade_date,
            ts_code=ts_code,
            con_code=con_code
        )
        
        return kpl_concept_cons
    except Exception as e:
        print(f"获取开盘啦概念题材成分股列表数据错误: {str(e)}")
        raise Exception(f"获取开盘啦概念题材成分股列表数据错误: {str(e)}")


def get_kpl_list(ts_code: str = None, trade_date: str = None, tag: str = None,
                 start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    kpl_list
        接口：kpl_list
        描述：获取开盘啦涨停、跌停、炸板等榜单数据
        限量：单次最大8000条数据，可根据日期循环获取历史数据
        积分：5000积分每分钟可以请求200次每天总量1万次，8000积分以上每分钟500次每天总量不限制，具体请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码
        - trade_date	str	N	交易日期
        - tag	str	N	板单类型（涨停/炸板/跌停/自然涨停/竞价)
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	代码
        - name	str	Y	名称
        - trade_date	str	Y	交易时间
        - lu_time	str	Y	涨停时间
        - ld_time	str	Y	跌停时间
        - open_time	str	Y	开板时间
        - last_time	str	Y	最后涨停时间
        - lu_desc	str	Y	涨停原因
        - tag	str	Y	标签
        - theme	str	Y	板块
        - net_change	float	Y	主力净额(元)
        - bid_amount	float	Y	竞价成交额(元)
        - status	str	Y	状态（N连板）
        - bid_change	float	Y	竞价净额
        - bid_turnover	float	Y	竞价换手%
        - lu_bid_vol	float	Y	涨停委买额
        - pct_chg	float	Y	涨跌幅%
        - bid_pct_chg	float	Y	竞价涨幅%
        - rt_pct_chg	float	Y	实时涨幅%
        - limit_order	float	Y	封单
        - amount	float	Y	成交额
        - turnover_rate	float	Y	换手率%
        - free_float	float	Y	实际流通
        - lu_limit_order	float	Y	最大封单
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取开盘啦涨停、跌停、炸板等榜单数据
        kpl_list = pro.kpl_list(ts_code=ts_code, trade_date=trade_date,
                                tag=tag, start_date=start_date, end_date=end_date)
        
        return kpl_list
    except Exception as e:
        print(f"获取开盘啦涨停、跌停、炸板等榜单数据错误: {str(e)}")
        raise Exception(f"获取开盘啦涨停、跌停、炸板等榜单数据错误: {str(e)}")


def get_top_list(trade_date: str = None, ts_code: str = None) -> pd.DataFrame:
    """
    top_list
        接口：top_list
        描述：龙虎榜每日交易明细
        数据历史： 2005年至今
        限量：单次请求返回最大10000行数据，可通过参数循环获取全部历史
        积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - trade_date	str	N	交易日期（YYYYMMDD格式）
        - ts_code	str	N	股票代码（xxxxxx.SH格式）
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - trade_date	str	Y	交易日期
        - ts_code	str	Y	TS代码
        - name	str	Y	名称
        - close	float	Y	收盘价
        - pct_change	float	Y	涨跌幅
        - turnover_rate	float	Y	换手率
        - amount	float	Y	总成交额
        - l_sell	float	Y	龙虎榜卖出额
        - l_buy	float	Y	龙虎榜买入额
        - l_amount	float	Y	龙虎榜成交额
        - net_amount	float	Y	龙虎榜净买入额
        - net_rate	float	Y	龙虎榜净买额占比
        - amount_rate	float	Y	龙虎榜成交额占比
        - float_values	float	Y	当日流通市值
        - reason	str	Y	上榜理由
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取龙虎榜每日交易明细
        top_list = pro.top_list(trade_date=trade_date, ts_code=ts_code)
        
        return top_list
    except Exception as e:
        print(f"获取龙虎榜每日交易明细数据错误: {str(e)}")
        raise Exception(f"获取龙虎榜每日交易明细数据错误: {str(e)}")


def get_top_inst(trade_date: str = None, ts_code: str = None) -> pd.DataFrame:
    """
    top_inst
        接口：top_inst
        描述：龙虎榜机构成交明细
        限量：单次请求最大返回10000行数据，可根据参数循环获取全部历史
        积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - trade_date	str	Y	交易日期（YYYYMMDD格式）
        - ts_code	str	N	股票代码（xxxxxx.SH格式）
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - trade_date	str	Y	交易日期
        - ts_code	str	Y	TS代码
        - exalter	str	Y	营业部名称
        - side	str	Y	买卖类型0：买入金额最大的前5名， 1：卖出金额最大的前5名
        - buy	float	Y	买入额（元）
        - buy_rate	float	Y	买入占总成交比例
        - sell	float	Y	卖出额（元）
        - sell_rate	float	Y	卖出占总成交比例
        - net_buy	float	Y	净成交额（元）
        - reason	str	Y	上榜理由
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    # 股票代码不能为空
    if ts_code is None:
        raise ValueError("ts_code参数不能为空")
    
    try:
        # 获取龙虎榜机构成交明细
        top_inst = pro.top_inst(trade_date=trade_date, ts_code=ts_code)
        
        return top_inst
    except Exception as e:
        print(f"获取龙虎榜机构成交明细数据错误: {str(e)}")
        raise Exception(f"获取龙虎榜机构成交明细数据错误: {str(e)}")


def get_limit_list_ths(trade_date: str = None, ts_code: str = None, limit_type: str = None,
                       market: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    limit_list_ths
        接口：limit_list_ths
        描述：获取同花顺每日涨跌停榜单数据，历史数据从20231101开始提供，增量每天16点左右更新
        限量：单次最大4000条，可根据日期或股票代码循环提取
        积分：8000积分以上每分钟500次，每天总量不限制，具体请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - trade_date	str	N	交易日期
        - ts_code	str	N	股票代码
        - limit_type	str	N	涨停池、连扳池、冲刺涨停、炸板池、跌停池，默认：涨停池
        - market	str	N	HS-沪深主板 GEM-创业板 STAR-科创板
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - trade_date	str	Y	交易日期
        - ts_code	str	Y	股票代码
        - name	str	Y	股票名称
        - price	float	Y	收盘价(元)
        - pct_chg	float	Y	涨跌幅%
        - open_num	int	Y	打开次数
        - lu_desc	str	Y	涨停原因
        - limit_type	str	Y	板单类别
        - tag	str	Y	涨停标签
        - status	str	Y	涨停状态（N连板、一字板）
        - first_lu_time	str	N	首次涨停时间
        - last_lu_time	str	N	最后涨停时间
        - first_ld_time	str	N	首次跌停时间
        - last_ld_time	str	N	最后涨停时间
        - limit_order	float	Y	封单量(元
        - limit_amount	float	Y	封单额(元
        - turnover_rate	float	Y	换手率%
        - free_float	float	Y	实际流通(元
        - lu_limit_order	float	Y	最大封单(元
        - limit_up_suc_rate	float	Y	近一年涨停封板率
        - turnover	float	Y	成交额
        - rise_rate	float	N	涨速
        - sum_float	float	N	总市值（亿元）
        - market_type	str	Y	股票类型：HS沪深主板、GEM创业板、STAR科创板
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取同花顺涨停榜单数据
        limit_list_ths = pro.limit_list_ths(
            trade_date=trade_date,
            ts_code=ts_code,
            limit_type=limit_type,
            market=market,
            start_date=start_date,
            end_date=end_date
        )
        
        return limit_list_ths
    except Exception as e:
        print(f"获取同花顺涨停榜单数据错误: {str(e)}")
        raise Exception(f"获取同花顺涨停榜单数据错误: {str(e)}")


def get_limit_list_d(trade_date: str = None, ts_code: str = None, limit_type: str = None,
                     exchange: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    limit_list_d
        接口：limit_list_d
        描述：获取A股每日涨跌停、炸板数据情况，数据从2020年开始（不提供ST股票的统计）
        限量：单次最大可以获取2500条数据，可通过日期或者股票循环提取
        积分：5000积分每分钟可以请求200次每天总量1万次，8000积分以上每分钟500次每天总量不限制，具体请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - trade_date	str	N	交易日期
        - ts_code	str	N	股票代码
        - limit_type	str	N	涨跌停类型（U涨停D跌停Z炸板）
        - exchange	str	N	交易所（SH上交所SZ深交所BJ北交所）
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - trade_date	str	Y	交易日期
        - ts_code	str	Y	股票代码
        - industry	str	Y	所属行业
        - name	str	Y	股票名称
        - close	float	Y	收盘价
        - pct_chg	float	Y	涨跌幅
        - amount	float	Y	成交额
        - limit_amount	float	Y	板上成交金额(成交价格为该股票跌停价的所有成交额的总和，涨停无此数据)
        - float_mv	float	Y	流通市值
        - total_mv	float	Y	总市值
        - turnover_ratio	float	Y	换手率
        - fd_amount	float	Y	封单金额（以涨停价买入挂单的资金总量）
        - first_time	str	Y	首次封板时间（跌停无此数据）
        - last_time	str	Y	最后封板时间
        - open_times	int	Y	炸板次数(跌停为开板次数)
        - up_stat	str	Y	涨停统计（N/T T天有N次涨停）
        - limit_times	int	Y	连板数（个股连续封板数量）
        - limit	str	Y	D跌停U涨停Z炸板
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取A股每日涨跌停、炸板数据
        limit_list_ths = pro.limit_list_ths(
            trade_date=trade_date,
            ts_code=ts_code,
            limit_type=limit_type,
            exchange=exchange,
            start_date=start_date,
            end_date=end_date
        )
        
        return limit_list_ths
    except Exception as e:
        print(f"获取A股每日涨跌停、炸板数据错误: {str(e)}")
        raise Exception(f"获取A股每日涨跌停、炸板数据错误: {str(e)}")


def get_limit_step(trade_date: str = None, ts_code: str = None,
                   start_date: str = None, end_date: str = None, nums: str = None) -> pd.DataFrame:
    """
    limit_step
        接口：limit_step
        描述：获取每天连板个数晋级的股票，可以分析出每天连续涨停进阶个数，判断强势热度
        限量：单次最大2000行数据，可根据股票代码或者日期循环提取全部
        积分：8000积分以上每分钟500次，每天总量不限制，具体请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - trade_date	str	N	交易日期（格式：YYYYMMDD，下同）
        - ts_code	str	N	股票代码
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期
        - nums	str	N	连板次数，支持多个输入，例如nums='2,3'
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	代码
        - name	str	Y	名称
        - trade_date	str	Y	交易日期
        - nums	str	Y	连板次数
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取每天连板个数晋级的股票
        limit_step = pro.limit_step(
            trade_date=trade_date,
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date,
            nums=nums
        )
        
        return limit_step
    except Exception as e:
        print(f"获取每天连板个数晋级的股票数据错误: {str(e)}")
        raise Exception(f"获取每天连板个数晋级的股票数据错误: {str(e)}")


def get_limit_cpt_list(trade_date: str = None, ts_code: str = None,
                       start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    limit_cpt_list
        接口：limit_cpt_list
        描述：获取每天涨停股票最多最强的概念板块，可以分析强势板块的轮动，判断资金动向
        限量：单次最大2000行数据，可根据股票代码或者日期循环提取全部
        积分：8000积分以上每分钟500次，每天总量不限制，具体请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - trade_date	str	N	交易日期（格式：YYYYMMDD，下同）
        - ts_code	str	N	股票代码
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	板块代码
        - name	str	Y	板块名称
        - trade_date	str	Y	交易日期
        - days	int	Y	上榜天数
        - up_stat	str	Y	连板高度
        - cons_nums	int	Y	连板家数
        - up_nums	str	Y	涨停家数
        - pct_chg	float	Y	涨跌幅%
        - rank	str	Y	板块热点排名
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取每天涨停股票最多最强的概念板块
        limit_cpt_list = pro.limit_cpt_list(
            trade_date=trade_date,
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date
        )
        
        return limit_cpt_list
    except Exception as e:
        print(f"获取每天涨停股票最多最强的概念板块数据错误: {str(e)}")
        raise Exception(f"获取每天涨停股票最多最强的概念板块数据错误: {str(e)}")


def get_ths_index(trade_date: str = None, exchange: str = None, type: str = None) -> pd.DataFrame:
    """
    ths_index
        接口：ths_index
        描述：获取同花顺板块指数。注：数据版权归属同花顺，如做商业用途，请主动联系同花顺，如需帮助请联系微信：waditu_a
        限量：本接口需获得5000积分，单次最大5000，一次可提取全部数据，请勿循环提取。

    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	指数代码
        - exchange	str	N	市场类型A-a股 HK-港股 US-美股
        - type	str	N	指数类型 N-概念指数 I-行业指数 R-地域指数 S-同花顺特色指数 ST-同花顺风格指数 TH-同花顺主题指数 BB-同花顺宽基指数
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	代码
        - name	str	Y	名称
        - count	int	Y	成分个数
        - exchange	str	Y	交易所
        - list_date	str	Y	上市日期
        - type	str	Y	N概念指数S特色指数
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取同花顺板块指数
        ths_index = pro.ths_index(
            trade_date=trade_date,
            exchange=exchange,
            type=type
        )
        
        return ths_index
    except Exception as e:
        print(f"获取同花顺概念股指数列表数据错误: {str(e)}")
        raise Exception(f"获取同花顺概念股指数列表数据错误: {str(e)}")


def get_ths_daily(ts_code: str = None, trade_date: str = None,
                  start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    ths_daily
        接口：ths_daily
        描述：获取同花顺板块指数行情。注：数据版权归属同花顺，如做商业用途，请主动联系同花顺，如需帮助请联系微信：waditu_a
        限量：单次最大3000行数据（5000积分），可根据指数代码、日期参数循环提取。

    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	指数代码
        - trade_date	str	N	交易日期（YYYYMMDD格式，下同）
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS指数代码
        - trade_date	str	Y	交易日
        - close	float	Y	收盘点位
        - open	float	Y	开盘点位
        - high	float	Y	最高点位
        - low	float	Y	最低点位
        - pre_close	float	Y	昨日收盘点
        - avg_price	float	Y	平均价
        - change	float	Y	涨跌点位
        - pct_change	float	Y	涨跌幅
        - vol	float	Y	成交量
        - turnover_rate	float	Y	换手率
        - total_mv	float	N	总市值
        - float_mv	float	N	流通市值
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取同花顺板块指数行情
        ths_daily = pro.ths_daily(
            ts_code=ts_code,
            trade_date=trade_date,
            start_date=start_date,
            end_date=end_date
        )
        
        return ths_daily
    except Exception as e:
        print(f"获取同花顺板块指数行情数据错误: {str(e)}")
        raise Exception(f"获取同花顺板块指数行情数据错误: {str(e)}")


def get_ths_member(ts_code: str = None, con_code: str = None) -> pd.DataFrame:
    """
    ths_member
        接口：ths_member
        描述：获取同花顺概念板块成分列表 注：数据版权归属同花顺，如做商业用途，请主动联系同花顺。
        限量：用户积累5000积分可调取，每分钟可调取200次，可按概念板块代码循环提取所有成分

    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	板块指数代码
        - con_code	str	N	股票代码（xxxxxx.SH格式）
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	指数代码
        - con_code	str	Y	股票代码
        - con_name	str	Y	股票名称
        - weight	float	N	权重(暂无)
        - in_date	str	N	纳入日期(暂无)
        - out_date	str	N	剔除日期(暂无)
        - is_new	str	N	是否最新Y是N否
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取同花顺概念板块成分列表
        ths_member = pro.ths_member(
            ts_code=ts_code,
            con_code=con_code
        )
        
        return ths_member
    except Exception as e:
        print(f"获取同花顺概念板块成分列表数据错误: {str(e)}")
        raise Exception(f"获取同花顺概念板块成分列表数据错误: {str(e)}")


def get_dc_index(ts_code: str = None, name: str = None, trade_date: str = None,
                 start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    dc_index
        接口：dc_index
        描述：获取东方财富每个交易日的概念板块数据，支持按日期查询
        限量：单次最大可获取5000条数据，历史数据可根据日期循环获取
        权限：用户积累5000积分可调取，具体请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	指数代码（支持多个代码同时输入，用逗号分隔）
        - name	str	N	板块名称（例如：人形机器人）
        - trade_date	str	N	交易日期（YYYYMMDD格式，下同）
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期

    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	概念代码
        - trade_date	str	Y	交易日期
        - name	str	Y	概念名称
        - leading	str	Y	领涨股票名称
        - leading_code	str	Y	领涨股票代码
        - pct_change	float	Y	涨跌幅
        - leading_pct	float	Y	领涨股票涨跌幅
        - total_mv	float	Y	总市值（万元）
        - turnover_rate	float	Y	换手率
        - up_num	int	Y	上涨家数
        - down_num	int	Y	下降家数
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取东方财富每个交易日的概念板块
        dc_index = pro.dc_index(
            ts_code=ts_code,
            name=name,
            trade_date=trade_date,
            start_date=start_date,
            end_date=end_date
        )
        
        return dc_index
    except Exception as e:
        print(f"获取东方财富每个交易日的概念板块数据错误: {str(e)}")
        raise Exception(f"获取东方财富每个交易日的概念板块数据错误: {str(e)}")


def get_dc_member(ts_code: str = None, con_code: str = None, trade_date: str = None) -> pd.DataFrame:
    """
    dc_member
        接口：dc_member
        描述：获取东方财富板块每日成分数据，可以根据概念板块代码和交易日期，获取历史成分
        限量：单次最大获取5000条数据，可以通过日期和代码循环获取
        权限：用户积累5000积分可调取，具体请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	板块指数代码
        - con_code	str	N	成分股票代码
        - trade_date	str	N	交易日期（YYYYMMDD格式）
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - trade_date	str	Y	交易日期
        - ts_code	str	Y	概念代码
        - con_code	str	Y	成分代码
        - name	str	Y	成分股名称
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取东方财富板块每日成分数据
        dc_member = pro.dc_member(
            ts_code=ts_code,
            con_code=con_code,
            trade_date=trade_date
        )
        
        return dc_member
    except Exception as e:
        print(f"获取东方财富概念板块成分列表数据错误: {str(e)}")
        raise Exception(f"获取东方财富概念板块成分列表数据错误: {str(e)}")


def get_stk_auction(ts_code: str = None, trade_date: str = None,
                    start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    stk_auction
       接口：stk_auction
        描述：获取当日个股和ETF的集合竞价成交情况，每天9点25后可以获取当日的集合竞价成交数据
        限量：单次最大返回8000行数据，可根据日期或代码循环获取全部历史
        积分：本接口是单独开权限的数据，已经开通了股票分钟权限的用户可自动获得本接口权限，单独申请权限请参考权限列表。5000积分可以每分钟请求10次接口。

    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码
        - trade_date	str	N	交易日期（YYYYMMDD格式，下同)
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	股票代码
        - trade_date	str	Y	数据日期
        - vol	int	Y	成交量（股）
        - price	int	Y	成交均价（元）
        - amount	float	Y	成交金额（元）
        - pre_close	float	Y	昨收价（元）
        - turnover_rate	float	Y	换手率（%）
        - volume_ratio	float	Y	量比
        - float_share	float	Y	流通股本（万股）
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取集合竞价成交数据
        stk_auction = pro.stk_auction(
            ts_code=ts_code,
            trade_date=trade_date,
            start_date=start_date,
            end_date=end_date
        )
        
        return stk_auction
    except Exception as e:
        print(f"获取当日个股和ETF的集合竞价成交数据错误: {str(e)}")
        raise Exception(f"获取当日个股和ETF的集合竞价成交数据错误: {str(e)}")


def get_hm_list(name: str = None) -> pd.DataFrame:
    """
    hm_list
        接口：hm_list
        描述：获取游资分类名录信息
        限量：单次最大1000条数据，目前总量未超过500
        积分：5000积分可以调取，积分获取办法请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - name	str	N	游资名称
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - name	str	Y	游资名称
        - desc	str	Y	说明
        - orgs	None	Y	关联机构
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取游资分类名录信息
        hm_list = pro.hm_list(name=name)
        
        return hm_list
    except Exception as e:
        print(f"获取游资分类名录信息数据错误: {str(e)}")
        raise Exception(f"获取游资分类名录信息数据错误: {str(e)}")


def get_hm_detail(trade_date: str = None, ts_code: str = None, hm_name: str = None,
                  start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    hm_detail
        接口：hm_detail
        描述：获取每日游资交易明细，数据开始于2022年8。游资分类名录，请点击游资名录
        限量：单次最多提取2000条记录，可循环调取，总量不限制
        积分：用户积10000积分可调取使用，积分获取办法请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - trade_date	str	N	交易日期(YYYYMMDD)
        - ts_code	str	N	股票代码
        - hm_name	str	N	游资名称
        - start_date	str	N	开始日期(YYYYMMDD)
        - end_date	str	N	结束日期(YYYYMMDD)
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - trade_date	str	Y	交易日期
        - ts_code	str	Y	股票代码
        - ts_name	str	Y	股票名称
        - buy_amount	float	Y	买入金额（元）
        - sell_amount	float	Y	卖出金额（元）
        - net_amount	float	Y	净买卖（元）
        - hm_name	str	Y	游资名称
        - hm_orgs	str	Y	关联机构（一般为营业部或机构专用）
        - tag	str	N	标签
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取每日游资交易明细
        hm_detail = pro.hm_detail(
            trade_date=trade_date,
            ts_code=ts_code,
            hm_name=hm_name,
            start_date=start_date,
            end_date=end_date
        )
        
        return hm_detail
    except Exception as e:
        print(f"获取每日游资交易明细数据错误: {str(e)}")
        raise Exception(f"获取每日游资交易明细数据错误: {str(e)}")


def get_ths_hot(trade_date: str = None, ts_code: str = None,
                 market: str = None, is_new: str = None) -> pd.DataFrame:
    """
    ths_hot
        接口：ths_hot
        描述：获取同花顺App热榜数据，包括热股、概念板块、ETF、可转债、港美股等等，每日盘中提取4次，收盘后4次，最晚22点提取一次。
        限量：单次最大2000条，可根据日期等参数循环获取全部数据
        积分：用户积5000积分可调取使用，积分获取办法请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - trade_date	str	N	交易日期
        - ts_code	str	N	TS代码
        - market	str	N	热榜类型(热股、ETF、可转债、行业板块、概念板块、期货、港股、热基、美股)
        - is_new	str	N	是否最新（默认Y，如果为N则为盘中和盘后阶段采集，具体时间可参考rank_time字段，状态N每小时更新一次，状态Y更新时间为22：30）
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - trade_date	str	Y	交易日期
        - data_type	str	Y	数据类型
        - ts_code	str	Y	股票代码
        - ts_name	str	Y	股票名称
        - rank	int	Y	排行
        - pct_change	float	Y	涨跌幅%
        - current_price	float	Y	当前价格
        - concept	str	Y	标签
        - rank_reason	str	Y	上榜解读
        - hot	float	Y	热度值
        - rank_time	str	Y	排行榜获取时间
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取同花顺App热榜数据
        ths_hot = pro.ths_hot(
            trade_date=trade_date,
            ts_code=ts_code,
            market=market,
            is_new=is_new
        )
        
        return ths_hot
    except Exception as e:
        print(f"获取同花顺App热榜数据数据错误: {str(e)}")
        raise Exception(f"获取同花顺App热榜数据数据错误: {str(e)}")


def get_dc_hot(trade_date: str = None, ts_code: str = None,
                 market: str = None, hot_type: str = None, is_new: str = None) -> pd.DataFrame:
    """
    dc_hot
        接口：dc_hot
        描述：获取东方财富App热榜数据，包括A股市场、ETF基金、港股市场、美股市场等等，每日盘中提取4次，收盘后4次，最晚22点提取一次。
        限量：单次最大2000条，可根据日期等参数循环获取全部数据
        积分：用户积8000积分可调取使用，积分获取办法请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - trade_date	str	N	交易日期
        - ts_code	str	N	TS代码
        - market	str	N	类型(A股市场、ETF基金、港股市场、美股市场)
        - hot_type	str	N	热点类型(人气榜、飙升榜)
        - is_new	str	N	是否最新（默认Y，如果为N则为盘中和盘后阶段采集，具体时间可参考rank_time字段，状态N每小时更新一次，状态Y更新时间为22：30）   
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - trade_date	str	Y	交易日期
        - data_type	str	Y	数据类型
        - ts_code	str	Y	股票代码
        - ts_name	str	Y	股票名称
        - rank	int	Y	排行或者热度
        - pct_change	float	Y	涨跌幅%
        - current_price	float	Y	当前价
        - rank_time	str	Y	排行榜获取时间
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取东方财富App热榜数据
        dc_hot = pro.dc_hot(
            trade_date=trade_date,
            ts_code=ts_code,
            market=market,
            hot_type=hot_type,
            is_new=is_new
        )
        
        return dc_hot
    except Exception as e:
        print(f"东方财富App热榜数据数据错误: {str(e)}")
        raise Exception(f"东方财富App热榜数据数据错误: {str(e)}")


