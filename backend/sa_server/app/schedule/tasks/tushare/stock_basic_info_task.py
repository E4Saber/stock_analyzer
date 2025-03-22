from typing import List, Dict, Any
import tushare as ts


pro = ts.pro_api()


def get_stock_basic(ts_code: str = None, name: str = None, market: str = None, list_status: str = 'L',
                    exchange:str = '', is_hs: str = None) -> List[Dict[str, Any]]:
    """
    stock_basic
    获取基础信息数据，包括股票代码、名称、上市日期、退市日期等

    输入参数：
    名称	类型	必选	描述
    - ts_code	str	N	TS股票代码
    - name	str	N	名称
    - market	str	N	市场类别 （主板/创业板/科创板/CDR/北交所）
    - list_status	str	N	上市状态 L上市 D退市 P暂停上市，默认是L
    - exchange	str	N	交易所 SSE上交所 SZSE深交所 BSE北交所
    - is_hs	str	N	是否沪深港通标的，N否 H沪股通 S深股通

    返回参数：
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
        print(f"获取CN指数数据错误: {str(e)}")
        raise Exception(f"获取CN指数数据错误: {str(e)}")

if __name__ == "__main__":
    # print(get_stock_basic())
    print(get_stock_basic(ts_code='000001.SZ'))
    # print(get_stock_basic(name='平安银行'))
    # print(get_stock_basic(market='主板'))
    # print(get_stock_basic(list_status='D'))
    # print(get_stock_basic(exchange='SSE'))
    # print(get_stock_basic(is_hs='H'))