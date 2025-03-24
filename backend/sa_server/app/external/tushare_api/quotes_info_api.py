import pandas as pd
from app.external.tushare_client import get_tushare_client


# 获取Tushare API实例
pro = get_tushare_client()


def get_daily(ts_code: str = None, trade_date: str = None,
              start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    daily
        接口：daily，可以通过数据工具调试和查看数据
        数据说明：交易日每天15点～16点之间入库。本接口是未复权行情，停牌期间不提供数据
        调取说明：120积分每分钟内最多调取500次，每次6000条数据，相当于单次提取23年历史
        描述：获取股票行情数据，或通过通用行情接口获取数据，包含了前后复权数据

    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码（支持多个股票同时提取，逗号分隔）
        - trade_date	str	N	交易日期（YYYYMMDD）
        - start_date	str	N	开始日期(YYYYMMDD)
        - end_date	str	N	结束日期(YYYYMMDD)

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	描述
        - ts_code	str	股票代码
        - trade_date	str	交易日期
        - open	float	开盘价
        - high	float	最高价
        - low	float	最低价
        - close	float	收盘价
        - pre_close	float	昨收价【除权价，前复权】
        - change	float	涨跌额
        - pct_chg	float	涨跌幅 【基于除权后的昨收计算的涨跌幅：（今收-除权昨收）/除权昨收 】
        - vol	float	成交量 （手）
        - amount	float	成交额 （千元）
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取A股日线行情
        daily = pro.daily(ts_code=ts_code, trade_date=trade_date,
                                start_date=start_date, end_date=end_date)

        
        return daily
    except Exception as e:
        print(f"获取A股日线行情数据错误: {str(e)}")
        raise Exception(f"获取A股日线行情数据错误: {str(e)}")