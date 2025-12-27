import numpy as np
import pandas as pd


def sharpe_ratio(returns, risk_free=0.0):
    excess = returns - risk_free / 252
    if returns.std() == 0:
        return 0
    return np.sqrt(252) * excess.mean() / excess.std()


def max_drawdown(series):
    roll_max = series.cummax()
    dd = (series - roll_max) / roll_max
    return dd.min()


def compute_all_metrics(df):
    """
    Retourne un dict avec toutes les métriques.
    """
    return {
        "sharpe_bh": sharpe_ratio(df['returns']),
        "sharpe_mom": sharpe_ratio(df['strategy_mom_ret']),
        "sharpe_rsi": sharpe_ratio(df['strategy_rsi_ret']),
        "maxdd_bh": max_drawdown(df['strategy_bh']),
        "maxdd_mom": max_drawdown(df['strategy_mom']),
        "maxdd_rsi": max_drawdown(df['strategy_rsi'])
    }
