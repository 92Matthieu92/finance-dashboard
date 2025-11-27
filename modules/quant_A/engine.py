import pandas as pd

from .data import DataLoader
from .strategies import apply_buy_hold, apply_momentum, apply_rsi_strategy
from .metrics import compute_all_metrics


class QuantAEngine:

    def __init__(self, ticker="^FCHI", period="5y", interval="1d"):
        self.loader = DataLoader(ticker=ticker, period=period, interval=interval)

    def load_data(self):
        df = self.loader.download()
        df['returns'] = df['price'].pct_change()
        df.dropna(inplace=True)
        return df

    def run(self, momentum_window=20, rsi_low=30, rsi_high=70):
        """
        Exécute le pipeline complet :
        1. Téléchargement
        2. Buy & Hold
        3. Momentum
        4. RSI
        5. Calcul métriques
        6. Retour DataFrame + métriques
        """
        df = self.load_data()

        # Stratégies
        df = apply_buy_hold(df)
        df = apply_momentum(df, window=momentum_window)
        df = apply_rsi_strategy(df, rsi_low=rsi_low, rsi_high=rsi_high)

        metrics = compute_all_metrics(df)

        return df, metrics

    def prepare_for_dashboard(self):
        """
        Fonction future pour Streamlit.
        Format : DataFrame + métriques.
        """
        return self.run()
