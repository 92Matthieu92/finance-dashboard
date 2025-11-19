import numpy as np

def sharpe_ratio(df):
    returns = df["Close"].pct_change().dropna()
    if returns.std() == 0:
        return 0
    return np.sqrt(252) * returns.mean() / returns.std()


def max_drawdown(df):
    cum_max = df["Close"].cummax()
    dd = df["Close"] / cum_max - 1
    return dd.min()
