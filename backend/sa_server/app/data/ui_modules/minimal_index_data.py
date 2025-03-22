from pydantic import BaseModel

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