from pydantic import BaseModel
from typing import Optional


class GlobalIndexData(BaseModel):
  """
  全球指数数据
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