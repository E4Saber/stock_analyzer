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