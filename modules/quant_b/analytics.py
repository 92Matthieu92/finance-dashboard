import numpy as np
import pandas as pd

TRADING_DAYS = 252


def compute_returns(prices: pd.DataFrame):
    """
    Rendements journaliers (% change) pour chaque actif.
    """
    return prices.pct_change().dropna()


def correlation_matrix(returns: pd.DataFrame):
    """
    Matrice de corrélation entre actifs.
    """
    return returns.corr()


def asset_metrics(returns: pd.DataFrame):
    """
    Rendement annualisé + volatilité annualisée pour chaque actif.
    """
    mean_daily = returns.mean()
    std_daily = returns.std()

    ann_return = (1 + mean_daily) ** TRADING_DAYS - 1
    ann_vol = std_daily * np.sqrt(TRADING_DAYS)

    return pd.DataFrame({
        "Annual Return": ann_return,
        "Annual Volatility": ann_vol
    })


def portfolio_metrics(returns: pd.DataFrame, weights):
    """
    Métriques du portefeuille : vol, return, diversification ratio.
    """
    w = np.array(weights, dtype=float)
    w = w / w.sum()

    # daily
    portfolio_daily_returns = (returns * w).sum(axis=1)
    mean_daily = portfolio_daily_returns.mean()
    std_daily = portfolio_daily_returns.std()

    # annualized
    ann_return = (1 + mean_daily) ** TRADING_DAYS - 1
    ann_vol = std_daily * np.sqrt(TRADING_DAYS)

    # diversification ratio
    cov = returns.cov()
    asset_vols = np.sqrt(np.diag(cov)) * np.sqrt(TRADING_DAYS)
    numerator = (w * asset_vols).sum()
    diversification_ratio = numerator / ann_vol if ann_vol != 0 else np.nan

    return {
        "ann_return": ann_return,
        "ann_vol": ann_vol,
        "diversification_ratio": diversification_ratio,
        "daily_returns": portfolio_daily_returns
    }