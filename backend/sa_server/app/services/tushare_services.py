from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.external.tushare_client import get_cn_indices
from app.config.indices_config import CN_INDICES

today = datetime.now()
today_str = today.strftime('%Y%m%d')
yesterday = today - timedelta(days=1)
yesterday_str = yesterday.strftime('%Y%m%d')
bf_yesterday = today - timedelta(days=2)
bf_yesterday_str = bf_yesterday.strftime('%Y%m%d')
def get_cn_indices_onday(index_codes: List, date: str = yesterday) -> dict:
    indices = get_cn_indices(index_codes=index_codes, trade_date=date)
    return indices

# 极简版全球指数数据，由于没有前日的收盘价，所以需要获取昨日的数据
def get_minimal_cn_indices_yday(index_codes: List) -> List[Dict[str, Any]]:
    indices = get_cn_indices(index_codes=index_codes, trade_date=yesterday_str)
    return indices

def get_minimal_cn_indices_tday(index_codes: List) -> List[Dict[str, Any]]:
    indices = get_cn_indices(index_codes=index_codes, trade_date=today_str)
    return indices

if __name__ == "__main__":
    indices = get_minimal_cn_indices_tday(CN_INDICES)
    print(f"CN tday Indices: {indices[0].get('cn_index_data').close}")
