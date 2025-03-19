from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.external.yfinance_client import get_global_indices
from app.config.indices_config import GLOBAL_INDICES

today = datetime.now()
yesterday = today - timedelta(days=1)
bf_yesterday = today - timedelta(days=2)
def get_global_indices_onday(index_codes: List, date: str = yesterday) -> dict:
    indices = get_global_indices(index_codes=index_codes, start=date, end=date)
    return indices

# 极简版全球指数数据，由于没有前日的收盘价，所以需要获取昨日的数据
def get_minimal_global_indices_yday(index_codes: List) -> List[Dict[str, Any]]:
    indices = get_global_indices(index_codes=index_codes, start=bf_yesterday, end=yesterday)
    return indices

def get_minimal_global_indices_tday(index_codes: List) -> List[Dict[str, Any]]:
    indices = get_global_indices(index_codes=index_codes, start=yesterday, end=today)
    return indices

if __name__ == "__main__":
    indices = get_minimal_global_indices_tday(GLOBAL_INDICES)
    print(indices)