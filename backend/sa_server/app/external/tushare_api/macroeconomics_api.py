import pandas as pd
from app.external.tushare_client import get_tushare_client


# 获取Tushare API实例
pro = get_tushare_client()


def get_shibor(date: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    shibor
        接口：shibor
        描述：shibor利率
        限量：单次最大2000，总量不限制，可通过设置开始和结束日期分段获取
        积分：用户积累120积分可以调取，具体请参阅积分获取办法

        Shibor利率介绍
            上海银行间同业拆放利率（Shanghai Interbank Offered Rate，简称Shibor），以位于上海的全国银行间同业拆借中心为技术平台计算、发布并命名，是由信用等级较高的银行组成报价团自主报出的人民币同业拆出利率计算确定的算术平均利率，是单利、无担保、批发性利率。目前，对社会公布的Shibor品种包括隔夜、1周、2周、1个月、3个月、6个月、9个月及1年。
            Shibor报价银行团现由18家商业银行组成。报价银行是公开市场一级交易商或外汇市场做市商，在中国货币市场上人民币交易相对活跃、信息披露比较充分的银行。中国人民银行成立Shibor工作小组，依据《上海银行间同业拆放利率（Shibor）实施准则》确定和调整报价银行团成员、监督和管理Shibor运行、规范报价行与指定发布人行为。
            全国银行间同业拆借中心受权Shibor的报价计算和信息发布。每个交易日根据各报价行的报价，剔除最高、最低各4家报价，对其余报价进行算术平均计算后，得出每一期限品种的Shibor，并于11:00对外发布。

    输入参数：
        名称	类型	必选	描述
        - date	str	N	日期 (日期输入格式：YYYYMMDD，下同)
        - start_date	str	N	开始日期
        - end_date	str	N	结束日期

    输出参数：
        pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - date	str	Y	日期
        - on	float	Y	隔夜
        - 1w	float	Y	1周
        - 2w	float	Y	2周
        - 1m	float	Y	1个月
        - 3m	float	Y	3个月
        - 6m	float	Y	6个月
        - 9m	float	Y	9个月
        - 1y	float	Y	1年
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取shibor利率
        shibor = pro.shibor(date=date, start_date=start_date, end_date=end_date)
        
        return shibor
    except Exception as e:
        print(f"获取shibor利率数据错误: {str(e)}")
        raise Exception(f"获取shibor利率数据错误: {str(e)}")


def get_shibor_quote(date: str = None, start_date: str = None, end_date: str = None, bank: str = None) -> pd.DataFrame:
    """
    shibor_quote
        接口：shibor_quote
        描述：Shibor报价数据
        限量：单次最大4000行数据，总量不限制，可通过设置开始和结束日期分段获取
        积分：用户积累120积分可以调取，具体请参阅积分获取办法

        输入参数：
            名称	类型	必选	描述
            - date	str	N	日期 (日期输入格式：YYYYMMDD，下同)
            - start_date	str	N	开始日期
            - end_date	str	N	结束日期
            - bank	str	N	银行名称 （中文名称，例如 农业银行）

        输出参数：
            pd.DataFrame: 包含以下列的 DataFrame:
            名称	类型	默认显示	描述
            - date	str	Y	日期
            - bank	str	Y	报价银行
            - on_b	float	Y	隔夜_Bid
            - on_a	float	Y	隔夜_Ask
            - 1w_b	float	Y	1周_Bid
            - 1w_a	float	Y	1周_Ask
            - 2w_b	float	Y	2周_Bid
            - 2w_a	float	Y	2周_Ask
            - 1m_b	float	Y	1月_Bid
            - 1m_a	float	Y	1月_Ask
            - 3m_b	float	Y	3月_Bid
            - 3m_a	float	Y	3月_Ask
            - 6m_b	float	Y	6月_Bid
            - 6m_a	float	Y	6月_Ask
            - 9m_b	float	Y	9月_Bid
            - 9m_a	float	Y	9月_Ask
            - 1y_b	float	Y	1年_Bid
            - 1y_a	float	Y	1年_Ask

    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取shibor报价数据
        shibor_quote = pro.shibor_quote(date=date, start_date=start_date, end_date=end_date, bank=bank)

        return shibor_quote
    except Exception as e:
        print(f"获取shibor报价数据错误: {str(e)}")
        raise Exception(f"获取shibor报价数据错误: {str(e)}")


def get_shibor_lpr(date: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    shibor_lpr
        接口：shibor_lpr
        描述：LPR贷款基础利率
        限量：单次最大4000(相当于单次可提取18年历史)，总量不限制，可通过设置开始和结束日期分段获取
        积分：用户积累120积分可以调取，具体请参阅积分获取办法

        贷款基础利率（Loan Prime Rate，简称LPR），是基于报价行自主报出的最优贷款利率计算并发布的贷款市场参考利率。目前，对社会公布1年期贷款基础利率。
        LPR报价银行团现由10家商业银行组成。报价银行应符合财务硬约束条件和宏观审慎政策框架要求，系统重要性程度高、市场影响力大、综合实力强，已建立内部收益率曲线和内部转移定价机制，具有较强的自主定价能力，已制定本行贷款基础利率管理办法，以及有利于开展报价工作的其他条件。市场利率定价自律机制依据《贷款基础利率集中报价和发布规则》确定和调整报价行成员，监督和管理贷款基础利率运行，规范报价行与指定发布人行为。
        全国银行间同业拆借中心受权贷款基础利率的报价计算和信息发布。每个交易日根据各报价行的报价，剔除最高、最低各1家报价，对其余报价进行加权平均计算后，得出贷款基础利率报价平均利率，并于11:30对外发布。

        输入参数：
            名称	类型	必选	描述
            - date	str	N	日期 (日期输入格式：YYYYMMDD，下同)
            - start_date	str	N	开始日期
            - end_date	str	N	结束日期

        输出参数：
            pd.DataFrame: 包含以下列的 DataFrame:
            名称	类型	默认显示	描述
            - date	str	Y	日期
            - 1y	float	Y	1年贷款利率
            - 5y	float	Y	5年贷款利率

    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取LPR报价数据
        shibor_lpr = pro.shibor_lpr(date=date, start_date=start_date, end_date=end_date)

        return shibor_lpr
    except Exception as e:
        print(f"获取LPR报价数据错误: {str(e)}")
        raise Exception(f"获取LPR报价数据错误: {str(e)}")


def get_libor(date: str = None, start_date: str = None, end_date: str = None, curr_type: str = None) -> pd.DataFrame:
    """
    libor
        接口：libor
        描述：Libor拆借利率
        限量：单次最大4000行数据，总量不限制，可通过设置开始和结束日期分段获取
        积分：用户积累120积分可以调取，具体请参阅积分获取办法

        Libor（London Interbank Offered Rate ），即伦敦同业拆借利率，是指伦敦的第一流银行之间短期资金借贷的利率，是国际金融市场中大多数浮动利率的基础利率。
        作为银行从市场上筹集资金进行转贷的融资成本，贷款协议中议定的LIBOR通常是由几家指定的参考银行，在规定的时间（一般是伦敦时间上午11：00）报价的平均利率。
        
        输入参数：
            名称	类型	必选	描述
            - date	str	N	日期 (日期输入格式：YYYYMMDD，下同)
            - start_date	str	N	开始日期
            - end_date	str	N	结束日期
            - curr_type	str	N	货币代码 (USD美元 EUR欧元 JPY日元 GBP英镑 CHF瑞郎，默认是USD)

        输出参数：
            pd.DataFrame: 包含以下列的 DataFrame:
            名称	类型	默认显示	描述
            - date	str	Y	日期
            - curr_type	str	Y	货币
            - on	float	Y	隔夜
            - 1w	float	Y	1周
            - 1m	float	Y	1个月
            - 2m	float	Y	2个月
            - 3m	float	Y	3个月
            - 6m	float	Y	6个月
            - 12m	float	Y	12个月

    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取Libor拆借利率数据
        libor = pro.libor(date=date, start_date=start_date, end_date=end_date, curr_type=curr_type)

        return libor
    except Exception as e:
        print(f"获取Libor拆借利率数据错误: {str(e)}")
        raise Exception(f"获取Libor拆借利率数据错误: {str(e)}")
    

def get_hibor(date: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    hibor
        接口：hibor
        描述：Hibor利率
        限量：单次最大4000行数据，总量不限制，可通过设置开始和结束日期分段获取
        积分：用户积累120积分可以调取，具体请参阅积分获取办法

        HIBOR (Hongkong InterBank Offered Rate)，是香港银行同行业拆借利率。指香港货币市场上，银行与银行之间的一年期以下的短期资金借贷利率，从伦敦同业拆借利率（LIBOR）变化出来的。

        输入参数：
            名称	类型	必选	描述
            - date	str	N	日期 (日期输入格式：YYYYMMDD，下同)
            - start_date	str	N	开始日期
            - end_date	str	N	结束日期

        输出参数：
            pd.DataFrame: 包含以下列的 DataFrame:
            名称	类型	默认显示	描述
            - date	str	Y	日期
            - on	float	Y	隔夜
            - 1w	float	Y	1周
            - 2w	float	Y	2周
            - 1m	float	Y	1个月
            - 2m	float	Y	2个月
            - 3m	float	Y	3个月
            - 6m	float	Y	6个月
            - 12m	float	Y	12个月

    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取Hibor香港同业拆借利率数据
        hibor = pro.hibor(date=date, start_date=start_date, end_date=end_date)

        return hibor
    except Exception as e:
        print(f"获取Hibor香港同业拆借利率数据错误: {str(e)}")
        raise Exception(f"获取Hibor香港同业拆借利率数据错误: {str(e)}")


def get_wz_index(date: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    wz_index
        接口：wz_index
        描述：温州民间借贷利率，即温州指数
        限量：不限量，一次可取全部指标全部历史数据
        积分：用户需要积攒2000积分可调取，具体请参阅积分获取办法
        数据来源：温州指数网

        温州指数 ，即温州民间融资综合利率指数，该指数及时反映民间金融交易活跃度和交易价格。该指数样板数据主要采集于四个方面：由温州市设立的几百家企业测报点，把各自借入的民间资本利率通过各地方金融办不记名申报收集起来；对各小额贷款公司借出的利率进行加权平均；融资性担保公司如典当行在融资过程中的利率，由温州经信委和商务局负责测报；民间借贷服务中心的实时利率。这些利率进行加权平均，就得出了“温州指数”。它是温州民间融资利率的风向标。2012年12月7日，温州指数正式对外发布。

        输入参数：
            名称	类型	必选	描述
            - date	str	N	日期 (日期输入格式：YYYYMMDD，下同)
            - start_date	str	N	开始日期
            - end_date	str	N	结束日期

        输出参数：
            pd.DataFrame: 包含以下列的 DataFrame:
            名称	类型	默认显示	描述
            - date	str	Y	日期
            - comp_rate	float	Y	温州民间融资综合利率指数 (%，下同)
            - center_rate	float	Y	民间借贷服务中心利率
            - micro_rate	float	Y	小额贷款公司放款利率
            - cm_rate	float	Y	民间资本管理公司融资价格
            - sdb_rate	float	Y	社会直接借贷利率
            - om_rate	float	Y	其他市场主体利率
            - aa_rate	float	Y	农村互助会互助金费率
            - m1_rate	float	Y	温州地区民间借贷分期限利率（一月期）
            - m3_rate	float	Y	温州地区民间借贷分期限利率（三月期）
            - m6_rate	float	Y	温州地区民间借贷分期限利率（六月期）
            - m12_rate	float	Y	温州地区民间借贷分期限利率（一年期）
            - long_rate	float	Y	温州地区民间借贷分期限利率（长期）

    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取温州民间借贷利率数据
        wz_index = pro.wz_index(date=date, start_date=start_date, end_date=end_date)

        return wz_index
    except Exception as e:
        print(f"获取温州民间借贷利率数据错误: {str(e)}")
        raise Exception(f"获取温州民间借贷利率数据错误: {str(e)}")

def get_gz_index(date: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    gz_index
        接口：gz_index
        描述：广州民间借贷利率
        限量：不限量，一次可取全部指标全部历史数据
        积分：用户需要积攒2000积分可调取，具体请参阅积分获取办法
        数据来源：广州民间金融街

        输入参数：
            名称	类型	必选	描述
            - date	str	N	日期 (日期输入格式：YYYYMMDD，下同)
            - start_date	str	N	开始日期
            - end_date	str	N	结束日期

        输出参数：
            pd.DataFrame: 包含以下列的 DataFrame:
            名称	类型	默认显示	描述
            - date	str	Y	日期
            - d10_rate	float	Y	小额贷市场平均利率（十天） （单位：%，下同）
            - m1_rate	float	Y	小额贷市场平均利率（一月期）
            - m3_rate	float	Y	小额贷市场平均利率（三月期）
            - m6_rate	float	Y	小额贷市场平均利率（六月期）
            - m12_rate	float	Y	小额贷市场平均利率（一年期）
            - long_rate	float	Y	小额贷市场平均利率（长期）
        """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取广州民间借贷利率数据
        gz_index = pro.gz_index(date=date, start_date=start_date, end_date=end_date)

        return gz_index
    except Exception as e:
        print(f"获取广州民间借贷利率数据错误: {str(e)}")
        raise Exception(f"获取广州民间借贷利率数据错误: {str(e)}")


def get_cn_gdp(q: str = None, start_q: str = None, end_q: str = None, fields: str = None) -> pd.DataFrame:
    """
    cn_gdp
        接口：cn_gdp
        描述：获取国民经济之GDP数据
        限量：单次最大10000，一次可以提取全部数据
        权限：用户积累600积分可以使用，具体请参阅积分获取办法

        输入参数：
            名称	类型	必选	描述
            - q	str	N	季度（2019Q1表示，2019年第一季度）
            - start_q	str	N	开始季度
            - end_q	str	N	结束季度
            - fields	str	N	指定输出字段（e.g. fields='quarter,gdp,gdp_yoy'）

        输出参数：
            pd.DataFrame: 包含以下列的 DataFrame:
            名称	类型	默认显示	描述
            - quarter	str	Y	季度
            - gdp	float	Y	GDP累计值（亿元）
            - gdp_yoy	float	Y	当季同比增速（%）
            - pi	float	Y	第一产业累计值（亿元）
            - pi_yoy	float	Y	第一产业同比增速（%）
            - si	float	Y	第二产业累计值（亿元）
            - si_yoy	float	Y	第二产业同比增速（%）
            - ti	float	Y	第三产业累计值（亿元）
            - ti_yoy	float	Y	第三产业同比增速（%）
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取中国GDP数据
        cn_gdp = pro.cn_gdp(q=q, start_q=start_q, end_q=end_q, fields=fields)
        
        return cn_gdp
    except Exception as e:
        print(f"获取中国GDP数据数据错误: {str(e)}")
        raise Exception(f"获取中国GDP数据数据错误: {str(e)}")
    
def get_cn_cpi(m: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    cn_cpi
        接口：cn_cpi
        描述：获取CPI居民消费价格数据，包括全国、城市和农村的数据
        限量：单次最大5000行，一次可以提取全部数据
        权限：用户积累600积分可以使用，具体请参阅积分获取办法

        输入参数：
            名称	类型	必选	描述
            - m	str	N	月份（YYYYMM，下同），支持多个月份同时输入，逗号分隔
            - start_m	str	N	开始月份
            - end_m	str	N	结束月份

        输出参数：
            pd.DataFrame: 包含以下列的 DataFrame:
            名称	类型	默认显示	描述
            - month	str	Y	月份YYYYMM
            - nt_val	float	Y	全国当月值
            - nt_yoy	float	Y	全国同比（%）
            - nt_mom	float	Y	全国环比（%）
            - nt_accu	float	Y	全国累计值
            - town_val	float	Y	城市当月值
            - town_yoy	float	Y	城市同比（%）
            - town_mom	float	Y	城市环比（%）
            - town_accu	float	Y	城市累计值
            - cnt_val	float	Y	农村当月值
            - cnt_yoy	float	Y	农村同比（%）
            - cnt_mom	float	Y	农村环比（%）
            - cnt_accu	float	Y	农村累计值
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取中国CPI数据
        cn_cpi = pro.cn_cpi(m=m, start_date=start_date, end_date=end_date)
        
        return cn_cpi
    except Exception as e:
        print(f"获取中国CPI数据数据错误: {str(e)}")
        raise Exception(f"获取中国CPI数据数据错误: {str(e)}")


def get_cn_ppi(m: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    cn_ppi
        接口：cn_ppi
        描述：获取PPI工业生产者出厂价格指数数据
        限量：单次最大5000，一次可以提取全部数据
        权限：用户600积分可以使用，具体请参阅积分获取办法

        输入参数：
            名称	类型	必选	描述
            - m	str	N	月份（YYYYMM，下同），支持多个月份同时输入，逗号分隔
            - start_m	str	N	开始月份
            - end_m	str	N	结束月份

        输出参数：
            pd.DataFrame: 包含以下列的 DataFrame:
        名称	类型	默认显示	描述
        - month	str	Y	月份YYYYMM
        - ppi_yoy	float	Y	PPI：全部工业品：当月同比
        - ppi_mp_yoy	float	Y	PPI：生产资料：当月同比
        - ppi_mp_qm_yoy	float	Y	PPI：生产资料：采掘业：当月同比
        - ppi_mp_rm_yoy	float	Y	PPI：生产资料：原料业：当月同比
        - ppi_mp_p_yoy	float	Y	PPI：生产资料：加工业：当月同比
        - ppi_cg_yoy	float	Y	PPI：生活资料：当月同比
        - ppi_cg_f_yoy	float	Y	PPI：生活资料：食品类：当月同比
        - ppi_cg_c_yoy	float	Y	PPI：生活资料：衣着类：当月同比
        - ppi_cg_adu_yoy	float	Y	PPI：生活资料：一般日用品类：当月同比
        - ppi_cg_dcg_yoy	float	Y	PPI：生活资料：耐用消费品类：当月同比
        - ppi_mom	float	Y	PPI：全部工业品：环比
        - ppi_mp_mom	float	Y	PPI：生产资料：环比
        - ppi_mp_qm_mom	float	Y	PPI：生产资料：采掘业：环比
        - ppi_mp_rm_mom	float	Y	PPI：生产资料：原料业：环比
        - ppi_mp_p_mom	float	Y	PPI：生产资料：加工业：环比
        - ppi_cg_mom	float	Y	PPI：生活资料：环比
        - ppi_cg_f_mom	float	Y	PPI：生活资料：食品类：环比
        - ppi_cg_c_mom	float	Y	PPI：生活资料：衣着类：环比
        - ppi_cg_adu_mom	float	Y	PPI：生活资料：一般日用品类：环比
        - ppi_cg_dcg_mom	float	Y	PPI：生活资料：耐用消费品类：环比
        - ppi_accu	float	Y	PPI：全部工业品：累计同比
        - ppi_mp_accu	float	Y	PPI：生产资料：累计同比
        - ppi_mp_qm_accu	float	Y	PPI：生产资料：采掘业：累计同比
        - ppi_mp_rm_accu	float	Y	PPI：生产资料：原料业：累计同比
        - ppi_mp_p_accu	float	Y	PPI：生产资料：加工业：累计同比
        - ppi_cg_accu	float	Y	PPI：生活资料：累计同比
        - ppi_cg_f_accu	float	Y	PPI：生活资料：食品类：累计同比
        - ppi_cg_c_accu	float	Y	PPI：生活资料：衣着类：累计同比
        - ppi_cg_adu_accu	float	Y	PPI：生活资料：一般日用品类：累计同比
        - ppi_cg_dcg_accu	float	Y	PPI：生活资料：耐用消费品类：累计同比
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取中国PPI数据
        cn_ppi = pro.cn_ppi(m=m, start_date=start_date, end_date=end_date)

        return cn_ppi
    except Exception as e:
        print(f"获取中国PPI数据数据错误: {str(e)}")
        raise Exception(f"获取中国PPI数据数据错误: {str(e)}")


def get_cn_m(m: str = None, start_date: str = None, end_date: str = None, fields : str = None) -> pd.DataFrame:
    """
    cn_m
        接口：cn_m
        描述：获取货币供应量之月度数据
        限量：单次最大5000，一次可以提取全部数据
        权限：用户积累600积分可以使用，具体请参阅积分获取办法

        输入参数：
            名称	类型	必选	描述
            - m	str	N	月度（202001表示，2020年1月）
            - start_m	str	N	开始月度
            - end_m	str	N	结束月度
            - fields	str	N	指定输出字段（e.g. fields='month,m0,m1,m2'）

        输出参数：
            pd.DataFrame: 包含以下列的 DataFrame:
            名称	类型	默认显示	描述
            - month	str	Y	月份YYYYMM
            - m0	float	Y	M0（亿元）
            - m0_yoy	float	Y	M0同比（%）
            - m0_mom	float	Y	M0环比（%）
            - m1	float	Y	M1（亿元）
            - m1_yoy	float	Y	M1同比（%）
            - m1_mom	float	Y	M1环比（%）
            - m2	float	Y	M2（亿元）
            - m2_yoy	float	Y	M2同比（%）
            - m2_mom	float	Y	M2环比（%）

    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取货币供应量数据
        cn_m = pro.cn_m(m=m, start_date=start_date, end_date=end_date, fields=fields)

        return cn_m
    except Exception as e:
        print(f"获取货币供应量数据错误: {str(e)}")
        raise Exception(f"获取货币供应量数据错误: {str(e)}")

def get_sf_month(m: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    sf_month
        接口：sf_month
        描述：获取社会融资规模数据
        限量：单次最大5000，一次可以提取全部数据
        权限：用户积累600积分可以使用，具体请参阅积分获取办法

        输入参数：
            名称	类型	必选	描述
            - m	str	N	月份（YYYYMM，下同），支持多个月份同时输入，逗号分隔
            - start_m	str	N	开始月份
            - end_m	str	N	结束月份

        输出参数：
            pd.DataFrame: 包含以下列的 DataFrame:
            名称	类型	默认显示	描述
            - month	str	Y	月度
            - inc_month	float	Y	社融增量当月值（亿元）
            - inc_cumval	float	Y	社融增量累计值（亿元）
            - stk_endval	float	Y	社融存量期末值（万亿元）
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取社会融资规模数据
        sf_month = pro.sf_month(m=m, start_date=start_date, end_date=end_date)

        return sf_month
    except Exception as e:
        print(f"获取社会融资规模数据错误: {str(e)}")
        raise Exception(f"获取社会融资规模数据错误: {str(e)}")
    

def get_cn_pmi(m: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    cn_pmi
        接口：cn_pmi
        描述：采购经理人指数
        限量：单次最大2000，一次可以提取全部数据
        权限：用户积累2000积分可以使用，具体请参阅积分获取办法

        输入参数：
            名称	类型	必选	描述
            - m	str	N	月度（202401表示，2024年1月）
            - start_m	str	N	开始月度
            - end_m	str	N	结束月度（e.g. fields='month,pmi010000,pmi010400'）

        输出参数：
            pd.DataFrame: 包含以下列的 DataFrame:
            名称	类型	默认显示	描述
            - month	str	N	月份YYYYMM
            - pmi010000	float	N	制造业PMI
            - pmi010100	float	N	制造业PMI:企业规模/大型企业
            - pmi010200	float	N	制造业PMI:企业规模/中型企业
            - pmi010300	float	N	制造业PMI:企业规模/小型企业
            - pmi010400	float	N	制造业PMI:构成指数/生产指数
            - pmi010401	float	N	制造业PMI:构成指数/生产指数:企业规模/大型企业
            - pmi010402	float	N	制造业PMI:构成指数/生产指数:企业规模/中型企业
            - pmi010403	float	N	制造业PMI:构成指数/生产指数:企业规模/小型企业
            - pmi010500	float	N	制造业PMI:构成指数/新订单指数
            - pmi010501	float	N	制造业PMI:构成指数/新订单指数:企业规模/大型企业
            - pmi010502	float	N	制造业PMI:构成指数/新订单指数:企业规模/中型企业
            - pmi010503	float	N	制造业PMI:构成指数/新订单指数:企业规模/小型企业
            - pmi010600	float	N	制造业PMI:构成指数/供应商配送时间指数
            - pmi010601	float	N	制造业PMI:构成指数/供应商配送时间指数:企业规模/大型企业
            - pmi010602	float	N	制造业PMI:构成指数/供应商配送时间指数:企业规模/中型企业
            - pmi010603	float	N	制造业PMI:构成指数/供应商配送时间指数:企业规模/小型企业
            - pmi010700	float	N	制造业PMI:构成指数/原材料库存指数
            - pmi010701	float	N	制造业PMI:构成指数/原材料库存指数:企业规模/大型企业
            - pmi010702	float	N	制造业PMI:构成指数/原材料库存指数:企业规模/中型企业
            - pmi010703	float	N	制造业PMI:构成指数/原材料库存指数:企业规模/小型企业
            - pmi010800	float	N	制造业PMI:构成指数/从业人员指数
            - pmi010801	float	N	制造业PMI:构成指数/从业人员指数:企业规模/大型企业
            - pmi010802	float	N	制造业PMI:构成指数/从业人员指数:企业规模/中型企业
            - pmi010803	float	N	制造业PMI:构成指数/从业人员指数:企业规模/小型企业
            - pmi010900	float	N	制造业PMI:其他/新出口订单
            - pmi011000	float	N	制造业PMI:其他/进口
            - pmi011100	float	N	制造业PMI:其他/采购量
            - pmi011200	float	N	制造业PMI:其他/主要原材料购进价格
            - pmi011300	float	N	制造业PMI:其他/出厂价格
            - pmi011400	float	N	制造业PMI:其他/产成品库存
            - pmi011500	float	N	制造业PMI:其他/在手订单
            - pmi011600	float	N	制造业PMI:其他/生产经营活动预期
            - pmi011700	float	N	制造业PMI:分行业/装备制造业
            - pmi011800	float	N	制造业PMI:分行业/高技术制造业
            - pmi011900	float	N	制造业PMI:分行业/基础原材料制造业
            - pmi012000	float	N	制造业PMI:分行业/消费品制造业
            - pmi020100	float	N	非制造业PMI:商务活动
            - pmi020101	float	N	非制造业PMI:商务活动:分行业/建筑业
            - pmi020102	float	N	非制造业PMI:商务活动:分行业/服务业业
            - pmi020200	float	N	非制造业PMI:新订单指数
            - pmi020201	float	N	非制造业PMI:新订单指数:分行业/建筑业
            - pmi020202	float	N	非制造业PMI:新订单指数:分行业/服务业
            - pmi020300	float	N	非制造业PMI:投入品价格指数
            - pmi020301	float	N	非制造业PMI:投入品价格指数:分行业/建筑业
            - pmi020302	float	N	非制造业PMI:投入品价格指数:分行业/服务业
            - pmi020400	float	N	非制造业PMI:销售价格指数
            - pmi020401	float	N	非制造业PMI:销售价格指数:分行业/建筑业
            - pmi020402	float	N	非制造业PMI:销售价格指数:分行业/服务业
            - pmi020500	float	N	非制造业PMI:从业人员指数
            - pmi020501	float	N	非制造业PMI:从业人员指数:分行业/建筑业
            - pmi020502	float	N	非制造业PMI:从业人员指数:分行业/服务业
            - pmi020600	float	N	非制造业PMI:业务活动预期指数
            - pmi020601	float	N	非制造业PMI:业务活动预期指数:分行业/建筑业
            - pmi020602	float	N	非制造业PMI:业务活动预期指数:分行业/服务业
            - pmi020700	float	N	非制造业PMI:新出口订单
            - pmi020800	float	N	非制造业PMI:在手订单
            - pmi020900	float	N	非制造业PMI:存货
            - pmi021000	float	N	非制造业PMI:供应商配送时间
            - pmi030000	float	N	中国综合PMI:产出指数
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取PMI数据
        cn_pmi = pro.cn_pmi(m=m, start_date=start_date, end_date=end_date)

        return cn_pmi
    except Exception as e:
        print(f"获取PMI数据错误: {str(e)}")
        raise Exception(f"获取PMI数据错误: {str(e)}")


# 国外宏观经济数据
def get_us_tycr(date: str = None, start_date: str = None, end_date: str = None, fields : str = None) -> pd.DataFrame:
    """
    us_tycr
        接口：us_tycr
        描述：获取美国每日国债收益率曲线利率
        限量：单次最大可获取2000条数据
        权限：用户积累120积分可以使用，积分越高频次越高。具体请参阅积分获取办法

        输入参数：
            名称	类型	必选	描述
            - date	str	N	日期 （YYYYMMDD格式，下同）
            - start_date	str	N	开始月份
            - end_date	str	N	结束月份
            - fields	str	N	指定输出字段（e.g. fields='m1,y1'）

        输出参数：
            pd.DataFrame: 包含以下列的 DataFrame:
            名称	类型	默认显示	描述
            - date	str	Y	日期
            - m1	float	Y	1月期
            - m2	float	Y	2月期
            - m3	float	Y	3月期
            - m4	float	Y	4月期（数据从20221019开始）
            - m6	float	Y	6月期
            - y1	float	Y	1年期
            - y2	float	Y	2年期
            - y3	float	Y	3年期
            - y5	float	Y	5年期
            - y7	float	Y	7年期
            - y10	float	Y	10年期
            - y20	float	Y	20年期
            - y30	float	Y	30年期

    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取国债收益率曲线利率（日频）数据
        us_tycr = pro.us_tycr(date=date, start_date=start_date, end_date=end_date, fields=fields)

        return us_tycr
    except Exception as e:
        print(f"获取美国国债收益率曲线数据错误: {str(e)}")
        raise Exception(f"获取美国国债收益率曲线数据错误: {str(e)}")
    
def get_us_trycr(date: str = None, start_date: str = None, end_date: str = None, fields : str = None) -> pd.DataFrame:
    """
    us_trycr
        接口：us_trycr
        描述：国债实际收益率曲线利率
        限量：单次最大可获取2000行数据，可循环获取
        权限：用户积累120积分可以使用，积分越高频次越高。具体请参阅积分获取办法

        输入参数：
            名称	类型	必选	描述
            - date	str	N	日期 （YYYYMMDD格式，下同）
            - start_date	str	N	开始月份
            - end_date	str	N	结束月份
            - fields	str	N	指定输出字段（e.g. fields='m1,y1'）

        输出参数：
            pd.DataFrame: 包含以下列的 DataFrame:
            名称	类型	默认显示	描述
            - date	str	Y	日期
            - y5	float	Y	5年期
            - y7	float	Y	7年期
            - y10	float	Y	10年期
            - y20	float	Y	20年期
            - y30	float	Y	30年期

    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取国债实际收益率曲线利率数据
        us_trycr = pro.us_trycr(date=date, start_date=start_date, end_date=end_date, fields=fields)

        return us_trycr
    except Exception as e:
        print(f"获取国债实际收益率曲线利率数据错误: {str(e)}")
        raise Exception(f"获取国债实际收益率曲线利率数据错误: {str(e)}")


def get_us_tbr(date: str = None, start_date: str = None, end_date: str = None, fields : str = None) -> pd.DataFrame:
    """
    us_tbr
        接口：us_tbr
        描述：获取美国短期国债利率数据
        限量：单次最大可获取2000行数据，可循环获取
        权限：用户积累120积分可以使用，积分越高频次越高。具体请参阅积分获取办法

        输入参数：
            名称	类型	必选	描述
            - date	str	N	日期 （YYYYMMDD格式，下同）
            - start_date	str	N	开始月份
            - end_date	str	N	结束月份
            - fields	str	N	指定输出字段(e.g. fields='w4_bd,w52_ce')

        输出参数：
            pd.DataFrame: 包含以下列的 DataFrame:
            名称	类型	默认显示	描述
            - date	str	Y	日期
            - w4_bd	float	Y	4周银行折现收益率
            - w4_ce	float	Y	4周票面利率
            - w8_bd	float	Y	8周银行折现收益率
            - w8_ce	float	Y	8周票面利率
            - w13_bd	float	Y	13周银行折现收益率
            - w13_ce	float	Y	13周票面利率
            - w17_bd	float	Y	17周银行折现收益率（数据从20221019开始）
            - w17_ce	float	Y	17周票面利率（数据从20221019开始）
            - w26_bd	float	Y	26周银行折现收益率
            - w26_ce	float	Y	26周票面利率
            - w52_bd	float	Y	52周银行折现收益率
            - w52_ce	float	Y	52周票面利率
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取短期国债利率数据
        us_tbr = pro.us_tbr(date=date, start_date=start_date, end_date=end_date, fields=fields)

        return us_tbr
    except Exception as e:
        print(f"获取短期国债利率数据错误: {str(e)}")
        raise Exception(f"获取短期国债利率数据错误: {str(e)}")


def get_us_tltr(date: str = None, start_date: str = None, end_date: str = None, fields : str = None) -> pd.DataFrame:
    """
    us_tltr
        接口：us_tltr
        描述：国债长期利率
        限量：单次最大可获取2000行数据，可循环获取
        权限：用户积累120积分可以使用，积分越高频次越高。具体请参阅积分获取办法

        输入参数：
            名称	类型	必选	描述
            - date	str	N	日期 （YYYYMMDD格式，下同）
            - start_date	str	N	开始月份
            - end_date	str	N	结束月份
            - fields	str	N	指定输出字段

        输出参数：
            pd.DataFrame: 包含以下列的 DataFrame:
            名称	类型	默认显示	描述
            - date	str	Y	日期
            - ltc	float	Y	收益率 LT COMPOSITE (>10 Yrs)
            - cmt	float	Y	20年期CMT利率(TREASURY 20-Yr CMT)
            - e_factor	float	Y	外推因子EXTRAPOLATION FACTOR
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取长期国债利率数据
        us_tltr = pro.us_tltr(date=date, start_date=start_date, end_date=end_date, fields=fields)

        return us_tltr
    except Exception as e:
        print(f"获取长期国债利率数据错误: {str(e)}")
        raise Exception(f"获取长期国债利率数据错误: {str(e)}")


def get_us_trltr(date: str = None, start_date: str = None, end_date: str = None, fields : str = None) -> pd.DataFrame:
    """
    us_trltr
        接口：us_trltr
        描述：国债实际长期利率平均值
        限量：单次最大可获取2000行数据，可循环获取
        权限：用户积累120积分可以使用，积分越高频次越高。具体请参阅积分获取办法

        输入参数：
            名称	类型	必选	描述
            - date	str	N	日期 （YYYYMMDD格式，下同）
            - start_date	str	N	开始月份
            - end_date	str	N	结束月份
            - fields	str	N	指定输出字段

        输出参数：
            pd.DataFrame: 包含以下列的 DataFrame:
            名称	类型	默认显示	描述
            - date	str	Y	日期
            - ltr_avg	float	Y	实际平均利率LT Real Average (10> Yrs)
    """
    if not pro:
        # API未初始化
        raise Exception("初始化TushareAPI失败")
    
    try:
        # 获取国债实际长期利率平均值数据
        us_trltr = pro.us_trltr(date=date, start_date=start_date, end_date=end_date, fields=fields)

        return us_trltr
    except Exception as e:
        print(f"获取国债实际长期利率平均值数据错误: {str(e)}")
        raise Exception(f"获取国债实际长期利率平均值数据错误: {str(e)}")