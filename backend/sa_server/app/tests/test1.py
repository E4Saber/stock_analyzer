import yfinance as yf


def get_global_indices():
  index_data = yf.Ticker("^HSI")
  history_data = index_data.history(period="1mo")
  print(history_data.columns)

get_global_indices()