import pandas as pd
from app.external.tushare_client import get_tushare_client


# 获取Tushare API实例
pro = get_tushare_client()


def get_top10_holders(ts_code: str = None, period: str = None, ann_date: str = None,
                        start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    top10_holders
        接口：top10_holders
        描述：获取上市公司前十大股东数据，包括持有数量和比例等信息
        积分：需2000积分以上才可以调取本接口，5000积分以上频次会更高
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	Y	TS代码
        - period	str	N	报告期（YYYYMMDD格式，一般为每个季度最后一天）
        - ann_date	str	N	公告日期
        - start_date	str	N	报告期开始日期
        - end_date	str	N	报告期结束日期

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	描述
        - ts_code	str	TS股票代码
        - ann_date	str	公告日期
        - end_date	str	报告期
        - holder_name	str	股东名称
        - hold_amount	float	持有数量（股）
        - hold_ratio	float	占总股本比例(%)
        - hold_float_ratio	float	占流通股本比例(%)
        - hold_change	float	持股变动
        - holder_type	str	股东类型
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    # 参数检查
    if not ts_code:
        # 股票代码不能为空
        raise ValueError("股票代码不能为空")
    
    try:
        # 获取上市公司前十大股东数据
        top10_holders = pro.top10_holders(ts_code=ts_code, period=period, ann_date=ann_date,
                                            start_date=start_date, end_date=end_date)
        
        return top10_holders
    except Exception as e:
        print(f"获取上市公司前十大股东数据错误: {str(e)}")
        raise Exception(f"获取上市公司前十大股东数据错误: {str(e)}")


def get_top10_floatholders(ts_code: str = None, period: str = None, ann_date: str = None,
                            start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    top10_floatholders
        接口：top10_floatholders
        描述：获取上市公司前十大流通股东数据
        积分：需2000积分以上才可以调取本接口，5000积分以上频次会更高
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	Y	TS代码
        - period	str	N	报告期（YYYYMMDD格式，一般为每个季度最后一天）
        - ann_date	str	N	公告日期
        - start_date	str	N	报告期开始日期
        - end_date	str	N	报告期结束日期
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	描述
        - ts_code	str	TS股票代码
        - ann_date	str	公告日期
        - end_date	str	报告期
        - holder_name	str	股东名称
        - hold_amount	float	持有数量（股）
        - hold_ratio	float	占总股本比例(%)
        - hold_float_ratio	float	占流通股本比例(%)
        - hold_change	float	持股变动
        - holder_type	str	股东类型
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    # 参数检查
    if not ts_code:
        # 股票代码不能为空
        raise ValueError("股票代码不能为空")
    
    try:
        # 获取上市公司前十大流通股东数据
        top10_floatholders = pro.top10_floatholders(ts_code=ts_code, period=period, ann_date=ann_date,
                                                    start_date=start_date, end_date=end_date)
        
        return top10_floatholders
    except Exception as e:
        print(f"获取上市公司前十大流通股东数据错误: {str(e)}")
        raise Exception(f"获取上市公司前十大流通股东数据错误: {str(e)}")


def get_pledge_stat(ts_code: str = None, end_date: str = None) -> pd.DataFrame:
    """
    pledge_stat
        接口：pledge_stat
        描述：获取股票质押统计数据
        限量：单次最大1000
        积分：用户需要至少500积分才可以调取，具体请参阅积分获取办法
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	TS代码
        - end_date	str	N	报告期结束日期
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS代码
        - end_date	str	Y	截止日期
        - pledge_count	int	Y	质押次数
        - unrest_pledge	float	Y	无限售股质押数量（万）
        - rest_pledge	float	Y	限售股份质押数量（万）
        - total_share	float	Y	总股本
        - pledge_ratio	float	Y	质押比例
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取上市公司股东质押数据
        pledge_stat = pro.pledge_stat(ts_code=ts_code, end_date=end_date)
        
        return pledge_stat
    except Exception as e:
        print(f"获取上市公司股东质押数据错误: {str(e)}")
        raise Exception(f"获取上市公司股东质押数据错误: {str(e)}")


def get_pledge_detail(ts_code: str = None) -> pd.DataFrame:
    """
    pledge_detail
        接口：pledge_detail
        描述：获取股票质押明细数据
        限量：单次最大1000
        积分：用户需要至少500积分才可以调取，具体请参阅积分获取办法
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	Y	TS代码
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS股票代码
        - ann_date	str	Y	公告日期
        - holder_name	str	Y	股东名称
        - pledge_amount	float	Y	质押数量（万股）
        - start_date	str	Y	质押开始日期
        - end_date	str	Y	质押结束日期
        - is_release	str	Y	是否已解押
        - release_date	str	Y	解押日期
        - pledgor	str	Y	质押方
        - holding_amount	float	Y	持股总数（万股）
        - pledged_amount	float	Y	质押总数（万股）
        - p_total_ratio	float	Y	本次质押占总股本比例
        - h_total_ratio	float	Y	持股总数占总股本比例
        - is_buyback	str	Y	是否回购
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")

    # 参数检查
    if not ts_code:
        # 股票代码不能为空
        raise ValueError("股票代码不能为空")
    
    try:
        # 获取股权质押数据明细
        pledge_detail = pro.pledge_detail(ts_code=ts_code)
        
        return pledge_detail
    except Exception as e:
        print(f"获取股权质押明细数据错误: {str(e)}")
        raise Exception(f"获取股权质押明细数据错误: {str(e)}")


def get_repurchase(ann_date: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    repurchase
        接口：repurchase
        描述：获取上市公司回购股票数据
        积分：用户需要至少600积分才可以调取，具体请参阅积分获取办法
    
    输入参数：
        名称	类型	必选	描述
        - ann_date	str	N	公告日期（任意填参数，如果都不填，单次默认返回2000条）
        - start_date	str	N	开始日期（YYYYMMDD格式）
        - end_date	str	N	结束日期（YYYYMMDD格式）
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS代码
        - ann_date	str	Y	公告日期
        - end_date	str	Y	截止日期
        - proc	str	Y	进度
        - exp_date	str	Y	过期日期
        - vol	float	Y	回购数量
        - amount	float	Y	回购金额
        - high_limit	float	Y	回购最高价
        - low_limit	float	Y	回购最低价
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取股票回购数据
        repurchase = pro.repurchase(ann_date=ann_date, start_date=start_date, end_date=end_date)
        
        return repurchase
    except Exception as e:
        print(f"获取股票回购数据错误: {str(e)}")
        raise Exception(f"获取股票回购数据错误: {str(e)}")


def get_share_float(ts_code: str = None, ann_date: str = None, float_date: str = None,
                    start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    share_float
        接口：share_float
        描述：获取限售股解禁
        限量：单次最大6000条，总量不限制
        积分：120分可调取，每分钟内限制次数，超过5000积分频次相对较高，具体请参阅积分获取办法
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	TS股票代码
        - ann_date	str	N	公告日期（日期格式：YYYYMMDD，下同）
        - float_date	str	N	解禁日期
        - start_date	str	N	解禁开始日期
        - end_date	str	N	解禁结束日期
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS代码
        - ann_date	str	Y	公告日期
        - float_date	str	Y	解禁日期
        - float_share	float	Y	流通股份(股)
        - float_ratio	float	Y	流通股份占总股本比率
        - holder_name	str	Y	股东名称
        - share_type	str	Y	股份类型
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取限售股解禁
        share_float = pro.share_float(ts_code=ts_code, ann_date=ann_date,
                                      float_date=float_date, start_date=start_date,
                                      end_date=end_date)
        
        return share_float
    except Exception as e:
        print(f"获取限售股解禁数据错误: {str(e)}")
        raise Exception(f"获取限售股解禁数据错误: {str(e)}")


def get_block_trade(ts_code: str = None, trade_date: str = None,
                    start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    block_trade
        接口：block_trade
        描述：大宗交易
        限量：单次最大1000条，总量不限制
        积分：300积分可调取，每分钟内限制次数，超过5000积分频次相对较高，具体请参阅积分获取办法
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	TS代码（股票代码和日期至少输入一个参数）
        - trade_date	str	N	交易日期（格式：YYYYMMDD，下同）
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS代码
        - trade_date	str	Y	交易日历
        - price	float	Y	成交价
        - vol	float	Y	成交量（万股）
        - amount	float	Y	成交金额
        - buyer	str	Y	买方营业部
        - seller	str	Y	卖方营业部
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取大宗交易数据
        block_trade = pro.block_trade(ts_code=ts_code, trade_date=trade_date,
                                      start_date=start_date, end_date=end_date)
        
        return block_trade
    except Exception as e:
        print(f"获取大宗交易数据错误: {str(e)}")
        raise Exception(f"获取大宗交易数据错误: {str(e)}")


def get_stk_holdernumber(ts_code: str = None, ann_date: str = None, enddate: str = None,
                         start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    stk_holdernumber
        接口：stk_holdernumber
        描述：获取上市公司股东户数数据，数据不定期公布
        限量：单次最大3000,总量不限制
        积分：600积分可调取，基础积分每分钟调取100次，5000积分以上频次相对较高。具体请参阅积分获取办法
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	TS股票代码
        - ann_date	str	N	公告日期
        - enddate	str	N	截止日期
        - start_date	str	N	公告开始日期
        - end_date	str	N	公告结束日期
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS股票代码
        - ann_date	str	Y	公告日期
        - end_date	str	Y	截止日期
        - holder_num	int	Y	股东户数
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取股东户数数据
        stk_holdernumber = pro.stk_holdernumber(ts_code=ts_code, ann_date=ann_date,
                                                enddate=enddate, start_date=start_date,
                                                end_date=end_date)
        
        return stk_holdernumber
    except Exception as e:
        print(f"获取股东户数数据错误: {str(e)}")
        raise Exception(f"获取股东户数数据错误: {str(e)}")


def get_stk_holdertrade(ts_code: str = None, ann_date: str = None, start_date: str = None,
                        end_date: str = None, trade_type: str = None, holder_type: str = None) -> pd.DataFrame:
    """
    stk_holdertrade
        接口：stk_holdertrade
        描述：获取上市公司增减持数据，了解重要股东近期及历史上的股份增减变化
        限量：单次最大提取3000行记录，总量不限制
        积分：用户需要至少2000积分才可以调取。基础积分有流量控制，积分越多权限越大，5000积分以上无明显限制，请自行提高积分，具体请参阅积分获取办法
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	TS股票代码
        - ann_date	str	N	公告日期
        - start_date	str	N	公告开始日期
        - end_date	str	N	公告结束日期
        - trade_type	str	N	交易类型IN增持DE减持
        - holder_type	str	N	股东类型C公司P个人G高管
    
    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS代码
        - ann_date	str	Y	公告日期
        - holder_name	str	Y	股东名称
        - holder_type	str	Y	股东类型G高管P个人C公司
        - in_de	str	Y	类型IN增持DE减持
        - change_vol	float	Y	变动数量
        - change_ratio	float	Y	占流通比例（%）
        - after_share	float	Y	变动后持股
        - after_ratio	float	Y	变动后占流通比例（%）
        - avg_price	float	Y	平均价格
        - total_share	float	Y	持股总数
        - begin_date	str	N	增减持开始日期
        - close_date	str	N	增减持结束日期
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取股东增减持数据
        stk_holdertrade = pro.stk_holdertrade(ts_code=ts_code, ann_date=ann_date,
                                                start_date=start_date, end_date=end_date,
                                                trade_type=trade_type, holder_type=holder_type)
        
        return stk_holdertrade
    except Exception as e:
        print(f"获取股东增减持数据错误: {str(e)}")
        raise Exception(f"获取股东增减持数据错误: {str(e)}")