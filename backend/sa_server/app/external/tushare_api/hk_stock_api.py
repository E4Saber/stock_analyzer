import pandas as pd
from app.external.tushare_client import get_tushare_client


# 获取Tushare API实例
pro = get_tushare_client()


def get_hk_basic(ts_code: str = None, list_status: str = None) -> pd.DataFrame:
    """
    hk_basic
        接口：hk_basic
        描述：获取港股列表信息
        数量：单次可提取全部在交易的港股列表数据
        积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	TS代码
        - list_status	str	N	上市状态 L上市 D退市 P暂停上市 ，默认L

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	
        - name	str	Y	股票简称
        - fullname	str	Y	公司全称
        - enname	str	Y	英文名称
        - cn_spell	str	Y	拼音
        - market	str	Y	市场类别
        - list_status	str	Y	上市状态
        - list_date	str	Y	上市日期
        - delist_date	str	Y	退市日期
        - trade_unit	float	Y	交易单位
        - isin	str	Y	ISIN代码
        - curr_type	str	Y	货币代码
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取港股列表信息
        hk_basic = pro.hk_basic(ts_code=ts_code, list_status=list_status)
        
        return hk_basic
    except Exception as e:
        print(f"获取港股列表信息数据错误: {str(e)}")
        raise Exception(f"获取港股列表信息数据错误: {str(e)}")


def get_hk_tradecal(start_date: str = None, end_date: str = None, is_open: str = None) -> pd.DataFrame:
    """
    get_hk_tradecal
        接口：hk_tradecal
        描述：获取交易日历
        限量：单次最大2000
        权限：用户积累2000积分才可调取
    
    输入参数：
        名称	类型	必选	描述
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期
        - is_open	str	N	是否交易 '0'休市 '1'交易

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - cal_date	str	Y	日历日期
        - is_open	int	Y	是否交易 '0'休市 '1'交易
        - pretrade_date	str	Y	上一个交易日
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取港股交易日历数据
        hk_tradecal = pro.hk_tradecal(start_date=start_date, end_date=end_date, is_open=is_open)
        
        return hk_tradecal
    except Exception as e:
        print(f"获取港股交易日历数据错误: {str(e)}")
        raise Exception(f"获取港股交易日历数据错误: {str(e)}")


def get_hk_daily(ts_code: str = None, trade_date: str = None,
                 start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    get_hk_daily
        接口：hk_daily，可以通过数据工具调试和查看数据。
        描述：获取港股每日增量和历史行情，每日18点左右更新当日数据
        限量：单次最大提取5000行记录，可多次提取，总量不限制
        积分：本接口单独开权限，具体请参阅积分获取办法
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码
        - trade_date	str	N	交易日期
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	股票代码
        - trade_date	str	Y	交易日期
        - open	float	Y	开盘价
        - high	float	Y	最高价
        - low	float	Y	最低价
        - close	float	Y	收盘价
        - pre_close	float	Y	昨收价
        - change	float	Y	涨跌额
        - pct_chg	float	Y	涨跌幅(%)
        - vol	float	Y	成交量(股)
        - amount	float	Y	成交额(元)
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取港股日线行情数据
        hk_daily = pro.hk_daily(ts_code=ts_code, trade_date=trade_date,
                                  start_date=start_date, end_date=end_date)
        
        return hk_daily
    except Exception as e:
        print(f"获取港股日线行情数据错误: {str(e)}")
        raise Exception(f"获取港股日线行情数据错误: {str(e)}")


def get_hk_daily_adj(ts_code: str = None, trade_date: str = None,
                      start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    get_hk_daily_adj
        接口：hk_daily_adj，可以通过数据工具调试和查看数据。
        描述：获取港股复权行情，提供股票股本、市值和成交及换手多个数据指标
        限量：单次最大可以提取6000条数据，可循环获取全部，支持分页提取
        要求：120积分可以试用查看数据，开通正式权限请参考权限说明文档
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码
        - trade_date	str	N	交易日期
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
        - vol	None	Y	成交量
        - amount	float	Y	成交额
        - vwap	float	Y	平均价
        - adj_factor	float	Y	复权因子
        - turnover_ratio	float	Y	换手率
        - free_share	None	Y	流通股本
        - total_share	None	Y	总股本
        - free_mv	float	Y	流通市值
        - total_mv	float	Y	总市值
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取港股日线行情数据（已复权）
        hk_daily_adj = pro.hk_daily_adj(ts_code=ts_code, trade_date=trade_date,
                                         start_date=start_date, end_date=end_date)
        
        return hk_daily_adj
    except Exception as e:
        print(f"获取港股日线行情（已复权）数据错误: {str(e)}")
        raise Exception(f"获取港股日线行情（已复权）数据错误: {str(e)}")


def get_hk_mins(ts_code: str = None, freq: str = None,
                 start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    hk_mins
        接口：hk_mins，可以通过数据工具调试和查看数据。
        描述：获取港股分钟线行情数据，包含了前后复权数据
        限量：单次最大提取5000条数据，可循环获取全部，支持分页提取
        要求：120积分可以试用查看数据，开通正式权限请参考权限说明文档
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	Y	股票代码，e.g.00001.HK
        - freq	str	Y	分钟频度（1min/5min/15min/30min/60min）
        - start_date	datetime	N	开始日期 格式：2023-03-13 09:00:00
        - end_date	datetime	N	结束时间 格式：2023-03-13 19:00:00

        freq参数说明
        - freq	说明
        - 1min	1分钟
        - 5min	5分钟
        - 15min	15分钟
        - 30min	30分钟
        - 60min	60分钟

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	股票代码
        - trade_time	str	Y	交易时间
        - open	float	Y	开盘价
        - close	float	Y	收盘价
        - high	float	Y	最高价
        - low	float	Y	最低价
        - vol	int	Y	成交量
        - amount	float	Y	成交金额
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    # 参数检查
    if not ts_code:
        raise ValueError("ts_code参数不能为空")
    if freq not in ['1min', '5min', '15min', '30min', '60min']:
        raise ValueError("频度参数freq必须是'1min', '5min', '15min', '30min'或'60min'中的一个")
    
    try:
        # 获取港股分钟行情
        hk_mins = pro.hk_mins(ts_code=ts_code, freq=freq,
                              start_date=start_date, end_date=end_date)
        
        return hk_mins
    except Exception as e:
        print(f"获取港股分钟行情数据错误: {str(e)}")
        raise Exception(f"获取港股分钟行情数据错误: {str(e)}")