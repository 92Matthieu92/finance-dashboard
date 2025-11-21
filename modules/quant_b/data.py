import pandas as pd
import yfinance as yf

def load_price_data(tickers, start=None, end=None):
    data = yf.download(tickers, start=start, end=end, auto_adjust=True)["Close"]
    if isinstance(data, pd.Series):
        data = data.to_frame()
    data = data.dropna(how="all")
    return data

if __name__ == '__main__':
    tickers = ["AAPL", "MSFT", "GOOGL"]
    df = load_price_data(tickers, start="2020-01-01", end="2024-01-01")
