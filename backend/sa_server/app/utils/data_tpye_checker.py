import pandas as pd

def data_check(data) -> None:

  # 检查类型
  print(f"Type of result: {type(data)}")

  # 如果是 Series，查看它的索引和值
  if isinstance(data, pd.Series):
      print("Series index:", data.index)
      print("First few values:", data.head())
      
      # 如果需要将 Series 转换为 DataFrame
      result_df = data.to_frame()
      print("Converted to DataFrame:", result_df.columns)

  # 如果是 DataFrame，查看它的列
  elif isinstance(data, pd.DataFrame):
      print("DataFrame columns:", data.columns)
      print("First few rows:", data.head())