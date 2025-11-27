import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


class DataLoader:

    def __init__(self, ticker="^FCHI", period="5y", interval="1d"):
        self.ticker = ticker
        self.period = period
        self.interval = interval

    def download(self):
        """
        Télécharge les données depuis Yahoo Finance.
        """
        df = yf.download(
            self.ticker,
            period=self.period,
            interval=self.interval,
            auto_adjust=True
        )

        if df.empty:
            raise ValueError("Erreur : aucune donnée téléchargée.")

        # Si MultiIndex → on aplati
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]
        df = df[['Close']].rename(columns={'Close': 'price'})
        df.dropna(inplace=True)
        return df
