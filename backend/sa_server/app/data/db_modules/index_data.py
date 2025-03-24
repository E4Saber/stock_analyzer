from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class IndexBaseData(BaseModel):
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

class IndexData(BaseModel):
  """
  A股指数实时数据，日线/周线/月线
  """
  ts_code: Optional[str] = None     # TS指数代码
  name: str                         # 简称
  trade_date: Optional[str] = None  # 交易日
  open: float                       # 开盘价
  high: float                       # 最高价
  low: float                        # 最低价
  close: float                      # 收盘价
  pre_close: Optional[float] = None # 昨日收盘点
  change: Optional[float] = None    # 涨跌点
  pct_chg: Optional[float] = None   # 涨跌幅（%）
  vol: Optional[float] = None       # 成交量（手）
  volume: float                     # 成交量
  amount: Optional[float] = None    # 成交额（千元）
  dividends: float = 0.0            # 股息，默认为 0
  stock_splits: float = 1.0         # 股票拆分，默认为 1

  class Config:
    from_attributes = True

class MinimalIndexData(BaseModel):
  """
  指数简要信息
  """
  ts_code: str      # TS指数代码
  name: str         # 简称
  current: float    # 当前点位
  change: float     # 涨跌点
  change_pct: float # 涨跌幅
  
  class Config:
    from_attributes = True
