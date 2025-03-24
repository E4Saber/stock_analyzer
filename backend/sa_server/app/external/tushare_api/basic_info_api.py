import pandas as pd
from app.external.tushare_client import get_tushare_client


# 获取Tushare API实例
pro = get_tushare_client()


def get_stock_basic(ts_code: str = None, name: str = None, market: str = None, list_status: str = 'L',
                    exchange:str = '', is_hs: str = None) -> pd.DataFrame:
    """
    stock_basic
        接口：stock_basic，可以通过数据工具调试和查看数据
        描述：获取基础信息数据，包括股票代码、名称、上市日期、退市日期等
        权限：2000积分起。此接口是基础信息，调取一次就可以拉取完，建议保存倒本地存储后使用

    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	TS股票代码
        - name	str	N	名称
        - market	str	N	市场类别 （主板/创业板/科创板/CDR/北交所）
        - list_status	str	N	上市状态 L上市 D退市 P暂停上市，默认是L
        - exchange	str	N	交易所 SSE上交所 SZSE深交所 BSE北交所
        - is_hs	str	N	是否沪深港通标的，N否 H沪股通 S深股通

    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS代码
        - symbol	str	Y	股票代码
        - name	str	Y	股票名称
        - area	str	Y	地域
        - industry	str	Y	所属行业
        - fullname	str	N	股票全称
        - enname	str	N	英文全称
        - cnspell	str	Y	拼音缩写
        - market	str	Y	市场类型（主板/创业板/科创板/CDR）
        - exchange	str	N	交易所代码
        - curr_type	str	N	交易货币
        - list_status	str	N	上市状态 L上市 D退市 P暂停上市
        - list_date	str	Y	上市日期
        - delist_date	str	N	退市日期
        - is_hs	str	N	是否沪深港通标的，N否 H沪股通 S深股通
        - act_name	str	Y	实控人名称
        - act_ent_type	str	Y	实控人企业性质
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取指数基本信息
        stock_basic = pro.stock_basic(ts_code=ts_code, name=name, market=market, list_status=list_status,
                                      exchange=exchange, is_hs=is_hs)

        
        return stock_basic
    except Exception as e:
        print(f"获取基础信息数据错误: {str(e)}")
        raise Exception(f"获取基础信息数据错误: {str(e)}")


def stk_premarket(ts_code: str = None, trade_date: str = None,
                  start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    stk_premarket
        接口：stk_premarket
        描述：每日开盘前获取当日股票的股本情况，包括总股本和流通股本，涨跌停价格等。
        限量：单次最大8000条数据，可循环提取
        权限：与积分无关，需单独开权限
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	TS代码
        - trade_date	str	N	交易日期
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期
    
    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - trade_date	str	Y	交易日期
        - ts_code	str	Y	TS股票代码
        - total_share	float	Y	总股本（万股）
        - float_share	float	Y	流通股本（万股）
        - pre_close	float	Y	昨日收盘价
        - up_limit	float	Y	今日涨停价
        - down_limit	float	Y	今日跌停价
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取股本情况（盘前）
        stk_premarket = pro.stk_premarket(ts_code=ts_code, trade_date=trade_date,
                                        start_date=start_date, end_date=end_date)

        
        return stk_premarket
    except Exception as e:
        print(f"获取当日股票的股本数据错误: {str(e)}")
        raise Exception(f"获取当日股票的股本数据错误: {str(e)}")


def get_trade_cal(exchange: str = None, start_date: str = None,
                  end_date: str = None, is_open: str = None) -> pd.DataFrame:
    """
    trade_cal
        接口：trade_cal，可以通过数据工具调试和查看数据。
        描述：获取各大交易所交易日历数据,默认提取的是上交所
        积分：需2000积分
    
    输入参数：
        名称	类型	必选	描述
        - exchange	str	N	交易所 SSE上交所,SZSE深交所,CFFEX 中金所,SHFE 上期所,CZCE 郑商所,DCE 大商所,INE 上能源
        - start_date	str	N	开始日期 （格式：YYYYMMDD 下同）
        - end_date	str	N	结束日期
        - is_open	str	N	是否交易 0休市 1交易
    
    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - exchange	str	Y	交易所 SSE上交所 SZSE深交所
        - cal_date	str	Y	日历日期
        - is_open	int	Y	是否交易 0休市 1交易
        - pretrade_date	str	Y	上一个交易日
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取各大交易所交易日历数据,默认提取的是上交所
        trade_cal = pro.trade_cal(exchange=exchange, start_date=start_date,
                                        end_date=end_date, is_open=is_open)

        
        return trade_cal
    except Exception as e:
        print(f"获取交易日历数据错误: {str(e)}")
        raise Exception(f"获取交易日历数据错误: {str(e)}")


def get_namechange(ts_code: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    namechange
        接口：namechange
        描述：历史名称变更记录
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	TS股票代码
        - start_date	str	N	公告开始日期
        - end_date	str	N	公告结束日期
    
    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS代码
        - name	str	Y	证券名称
        - start_date	str	Y	开始日期
        - end_date	str	Y	结束日期
        - ann_date	str	Y	公告日期
        - change_reason	str	Y	变更原因
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取历史名称变更记录
        namechange = pro.namechange(ts_code=ts_code, start_date=start_date, end_date=end_date)

        
        return namechange
    except Exception as e:
        print(f"获取历史名称变更记录数据错误: {str(e)}")
        raise Exception(f"获取历史名称变更记录数据错误: {str(e)}")


def get_hs_const(hs_type: str = None, is_new: str = None) -> pd.DataFrame:
    """
    hs_const
        接口：hs_const
        描述：获取沪股通、深股通成分数据
    
    输入参数：
        名称	类型	必选	描述
        - hs_type	str	N	类型SH沪股通SZ深股通
        - is_new	str	N	是否最新 1是 0否
    
    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS代码
        - hs_type	str	Y	沪深港通类型SH沪SZ深
        - in_date	str	Y	纳入日期
        - out_date	str	Y	剔除日期
        - is_new	str	Y	是否最新 1是 0否
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取沪股通、深股通成分数据
        hs_const = pro.hs_const(hs_type=hs_type, is_new=is_new)

        
        return hs_const
    except Exception as e:
        print(f"获取沪股通、深股通成分数据错误: {str(e)}")
        raise Exception(f"获取沪股通、深股通成分数据错误: {str(e)}")


def get_stock_company(ts_code: str = None, exchange: str = None) -> pd.DataFrame:
    """
    stock_company
        接口：stock_company，可以通过数据工具调试和查看数据。
        描述：获取上市公司基础信息，单次提取4500条，可以根据交易所分批提取
        积分：用户需要至少120积分才可以调取，具体请参阅积分获取办法
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	股票代码
        - exchange	str	N	交易所代码
    
    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	股票代码
        - com_name	str	Y	公司全称
        - com_id	str	Y	统一社会信用代码
        - exchange	str	Y	交易所代码
        - chairman	str	Y	法人代表
        - manager	str	Y	总经理
        - secretary	str	Y	董秘
        - reg_capital	float	Y	注册资本(万元)
        - setup_date	str	Y	注册日期
        - province	str	Y	所在省份
        - city	str	Y	所在城市
        - introduction	str	N	公司介绍
        - website	str	Y	公司主页
        - email	str	Y	电子邮件
        - office	str	N	办公室
        - employees	int	Y	员工人数
        - main_business	str	N	主要业务及产品
        - business_scope	str	N	经营范围
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取上市公司基础信息
        stock_company = pro.stock_company(ts_code=ts_code, exchange=exchange)

        
        return stock_company
    except Exception as e:
        print(f"获取上市公司基础信息数据错误: {str(e)}")
        raise Exception(f"获取上市公司基础信息数据错误: {str(e)}")


def get_stk_managers(ts_code: str = None, ann_date: str = None,
                     start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    stk_managers
        接口：stk_managers
        描述：获取上市公司管理层
        积分：用户需要2000积分才可以调取，5000积分以上频次相对较高，具体请参阅积分获取办法
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	N	TS股票代码
        - ann_date	str	N	公告日期
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期

    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS股票代码
        - ann_date	str	Y	公告日期
        - name	str	Y	姓名
        - gender	str	Y	性别
        - lev	str	Y	岗位类别
        - title	str	Y	岗位
        - edu	str	Y	学历
        - national	str	Y	国籍
        - birthday	str	Y	出生年月
        - begin_date	str	Y	上任日期
        - end_date	str	Y	离任日期
        - resume	str	N	个人简历
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取上市公司管理层
        stk_managers = pro.stk_managers(ts_code=ts_code, ann_date=ann_date,
                                        start_date=start_date, end_date=end_date)

        
        return stk_managers
    except Exception as e:
        print(f"获取上市公司管理层数据错误: {str(e)}")
        raise Exception(f"获取上市公司管理层数据错误: {str(e)}")


def get_stk_rewards(ts_code: str, end_date: str = None) -> pd.DataFrame:
    """
    stk_rewards
        接口：stk_rewards
        描述：获取上市公司管理层薪酬和持股
        积分：用户需要2000积分才可以调取，5000积分以上频次相对较高，具体请参阅积分获取办法
    
    输入参数：
        名称	类型	必选	描述
        - ts_code	str	Y	TS股票代码
        - end_date	str	N	公告日期
    
    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS股票代码
        - ann_date	str	Y	公告日期
        - end_date	str	Y	截止日期
        - name	str	Y	姓名
        - title	str	Y	职务
        - reward	float	Y	报酬
        - hold_vol	float	Y	持股数
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取上市公司管理层薪酬和持股
        stk_rewards = pro.stk_rewards(ts_code=ts_code, end_date=end_date)

        return stk_rewards
    except Exception as e:
        print(f"获取上市公司管理层薪酬和持股数据错误: {str(e)}")
        raise Exception(f"获取上市公司管理层薪酬和持股数据错误: {str(e)}")


def get_new_share(start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    new_share
        接口：new_share
        描述：获取新股上市列表数据
        限量：单次最大2000条，总量不限制
        积分：用户需要至少120积分才可以调取，具体请参阅积分获取办法
    
    输入参数：
        名称	类型	必选	描述
        - start_date	str	N	上网发行开始日期
        - end_date	str	N	上网发行结束日期

    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - ts_code	str	Y	TS股票代码
        - sub_code	str	Y	申购代码
        - name	str	Y	名称
        - ipo_date	str	Y	上网发行日期
        - issue_date	str	Y	上市日期
        - amount	float	Y	发行总量（万股）
        - market_amount	float	Y	上网发行总量（万股）
        - price	float	Y	发行价格
        - pe	float	Y	市盈率
        - limit_amount	float	Y	个人申购上限（万股）
        - funds	float	Y	募集资金（亿元）
        - ballot	float	Y	中签率
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取新股上市列表
        new_share = pro.new_share(start_date=start_date, end_date=end_date)

        return new_share
    except Exception as e:
        print(f"获取新股上市列表数据错误: {str(e)}")
        raise Exception(f"获取新股上市列表数据错误: {str(e)}")


def get_bak_basic(trade_date: str = None, ts_code: str = None) -> pd.DataFrame:
    """
    bak_basic
        接口：bak_basic
        描述：获取备用基础列表，数据从2016年开始
        限量：单次最大7000条，可以根据日期参数循环获取历史，正式权限需要5000积分。

    输入参数：
        名称	类型	必选	描述
        - trade_date	str	N	交易日期
        - ts_code	str	N	TS代码
    
    返回参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - trade_date	str	Y	交易日期
        - ts_code	str	Y	TS股票代码
        - name	str	Y	股票名称
        - industry	str	Y	行业
        - area	str	Y	地域
        - pe	float	Y	市盈率（动）
        - float_share	float	Y	流通股本（亿）
        - total_share	float	Y	总股本（亿）
        - total_assets	float	Y	总资产（亿）
        - liquid_assets	float	Y	流动资产（亿）
        - fixed_assets	float	Y	固定资产（亿）
        - reserved	float	Y	公积金
        - reserved_pershare	float	Y	每股公积金
        - eps	float	Y	每股收益
        - bvps	float	Y	每股净资产
        - pb	float	Y	市净率
        - list_date	str	Y	上市日期
        - undp	float	Y	未分配利润
        - per_undp	float	Y	每股未分配利润
        - rev_yoy	float	Y	收入同比（%）
        - profit_yoy	float	Y	利润同比（%）
        - gpr	float	Y	毛利率（%）
        - npr	float	Y	净利润率（%）
        - holder_num	int	Y	股东人数
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取备用基础列表
        bak_basic = pro.bak_basic(trade_date=trade_date, ts_code=ts_code)

        return bak_basic
    except Exception as e:
        print(f"获取备用基础列表数据错误: {str(e)}")
        raise Exception(f"获取备用基础列表数据错误: {str(e)}")


if __name__ == "__main__":
    # print(get_stock_basic())
    print(get_stock_basic(ts_code='000001.SZ'))
    # print(get_stock_basic(name='平安银行'))
    # print(get_stock_basic(market='主板'))
    # print(get_stock_basic(list_status='D'))
    # print(get_stock_basic(exchange='SSE'))
    # print(get_stock_basic(is_hs='H'))