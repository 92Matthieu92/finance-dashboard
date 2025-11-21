import numpy as np
import pandas as pd


def normalize_weights(weights):
    """
    Normalise un vecteur de poids pour que la somme = 1.
    """
    w = np.array(weights, dtype=float)
    total = w.sum()
    if total == 0:
        raise ValueError("La somme des poids ne peut pas être zéro.")
    return w / total


def compute_portfolio_returns(prices: pd.DataFrame, weights):
    """
    Calcule les rendements journaliers du portefeuille
    à partir des prix et des poids.
    """
    if len(weights) != len(prices.columns):
        raise ValueError("Nombre de poids différent du nombre d'actifs.")
    
    w = normalize_weights(weights)
    returns = prices.pct_change().dropna()
    port_returns = (returns * w).sum(axis=1)
    return port_returns


def compute_portfolio_value(port_returns: pd.Series, initial_value=1.0):
    """
    Calcule la valeur cumulée du portefeuille (courbe de perform.)
    """
    cum_value = initial_value * (1 + port_returns).cumprod()
    cum_value.name = "Portfolio"
    return cum_value


def simulate_portfolio(prices: pd.DataFrame, weights, initial_value=1.0):
    """
    Fonction high-level : renvoie directement la courbe du portefeuille.
    """
    port_returns = compute_portfolio_returns(prices, weights)
    return compute_portfolio_value(port_returns, initial_value)

def simulate_portfolio_rebalanced(prices: pd.DataFrame,
                                  weights,
                                  rebal_freq="D",
                                  initial_value=1.0):
    """
    Rebalance selon D (quotidien), W (hebdomadaire), M (mensuel).
    """
    weights = normalize_weights(weights)
    returns = prices.pct_change().dropna()

    if rebal_freq == "D":
        # simple : rééquilibrage quotidien = stable
        port_returns = (returns * weights).sum(axis=1)
        return compute_portfolio_value(port_returns, initial_value)

    # Regroupement selon fréquence demandée
    grouped = returns.groupby(pd.Grouper(freq=rebal_freq))

    value = initial_value
    portfolio_curve = []

    for _, group in grouped:
        if group.empty:
            continue

        # rendement cumulé par actif sur la période
        period_asset_returns = (1 + group).prod() - 1

        # rendement du portefeuille sur la période
        period_port_ret = (period_asset_returns * weights).sum()

        # on met à jour la valeur
        value *= (1 + period_port_ret)

        # pour remplir la courbe : valeur constante sur la période
        period_index = group.index
        period_values = pd.Series(value, index=period_index)
        portfolio_curve.append(period_values)

    out = pd.concat(portfolio_curve).sort_index()
    out.name = "Portfolio"
    return out

def run_strategy(prices: pd.DataFrame,
                 strategy="equal_weight",
                 custom_weights=None,
                 rebal_freq="D",
                 initial_value=1.0):

    n = prices.shape[1]

    if strategy == "equal_weight":
        weights = [1 / n] * n

    elif strategy == "custom":
        if custom_weights is None or len(custom_weights) != n:
            raise ValueError("Custom weights must match number of assets.")
        weights = custom_weights

    else:
        raise ValueError("Unknown strategy")

    return simulate_portfolio_rebalanced(
        prices,
        weights,
        rebal_freq=rebal_freq,
        initial_value=initial_value
    )