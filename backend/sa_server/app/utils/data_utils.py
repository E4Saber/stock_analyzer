from typing import Any, Dict, List
from app.data.modules.cn_index_data import CNIndexBaseData, CNIndexData

def match_index_data(base_data_list: List[CNIndexBaseData], index_data_list: List[CNIndexData]) -> List[Dict[str, Any]]:

  print(f"base_data_list: {base_data_list}")
  print(f"index_data_list: {index_data_list}")
  
  minimal_index_data = []
  # 创建字典以便快速查找
  index_data_dict = {data.ts_code: data for data in index_data_list}

  for base_data in base_data_list:
    ts_code = base_data.ts_code
    index_data = index_data_dict.get(ts_code)

    
    minimal_index_data.append({
        "ts_code": base_data.ts_code,
        "name": base_data.name,
        "current": index_data.close,
        "change": index_data.change,
        "change_pct": index_data.pct_chg,
    })

  return minimal_index_data