from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class CNIndexBaseData(BaseModel):
  """
  A股指数基本信息
  """
  ts_code: str                      # TS代码
  name: str                         # 简称
  fullname: Optional[str] = None    # 指数全称
  market: str                       # 市场
  publisher: str                    # 发布方
  index_type: Optional[str] = None  # 指数风格
  category: str                     # 指数类别
  base_date: str                    # 基期
  base_point: float                 # 基点
  list_date: str                    # 发布日期
  weight_rule: Optional[str] = None # 加权方式
  desc: Optional[str] = None        # 描述
  exp_date: Optional[str] = None    # 终止日期（可选字段）

  class Config:
    from_attributes = True

class CNIndexData(BaseModel):
  """
  A股指数实时数据，日线/周线/月线
  """
  ts_code: str                      # TS指数代码
  trade_date: str                   # 交易日
  open: float                       # 开盘点位
  high: float                       # 最高点位
  low: float                        # 最低点位
  close: float                      # 收盘点位
  pre_close: float                  # 昨日收盘点
  change: float                     # 涨跌点
  pct_chg: float                    # 涨跌幅（%）
  vol: float                        # 成交量（手）
  amount: float                     # 成交额（千元）

  class Config:
    from_attributes = True
