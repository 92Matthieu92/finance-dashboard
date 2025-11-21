if __name__ == '__main__':
    from data import load_price_data
    from portfolio import run_strategy

    tickers = ["AAPL", "MSFT", "GOOGL"]
    prices = load_price_data(tickers, start="2023-01-01", end="2024-01-01")

    print("\n=== Test equal weight — daily rebal ===")
    eq_daily = run_strategy(prices,
                            strategy="equal_weight",
                            rebal_freq="D")
    print(eq_daily.tail())

    print("\n=== Test equal weight — weekly rebal ===")
    eq_weekly = run_strategy(prices,
                             strategy="equal_weight",
                             rebal_freq="W")
    print(eq_weekly.tail())

    print("\n=== Test custom weights — monthly rebal ===")
    custom_monthly = run_strategy(prices,
                                  strategy="custom",
                                  custom_weights=[0.5, 0.3, 0.2],
                                  rebal_freq="M")
    print(custom_monthly.tail())