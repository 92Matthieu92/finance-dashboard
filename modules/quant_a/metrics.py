import pandas as pd
import numpy as np

def sharpe_ratio(df, risk_free_rate=0.0):
    """
    Calcule le Sharpe Ratio à partir du DataFrame contenant des prix.
    """
    if "Close" not in df.columns or df["Close"].empty:
        return 0

    # Rendements journaliers
    returns = df["Close"].pct_change().dropna()

    if returns.empty:
        return 0

    mean_ret = returns.mean()
    std_ret = returns.std()

    # 🛠 Correction principale : gérer le cas où std_ret est une série OU un scalaire
    if isinstance(std_ret, pd.Series):
        std_ret = std_ret.iloc[0]

    # 🛠 Eviter divisions par zéro / valeurs NaN
    if std_ret is None or std_ret == 0 or np.isnan(std_ret):
        return 0

    sharpe = (mean_ret - risk_free_rate) / std_ret
    return sharpe


def max_drawdown(df):
    """
    Calcule le Max Drawdown à partir des prix de clôture
    """
    prices = df["Close"]

    # Courbe des sommets historiques
    rolling_max = prices.cummax()

    # Drawdown courant
    drawdown = (prices - rolling_max) / rolling_max

    # Le minimum = le plus gros drawdown
    return drawdown.min()
