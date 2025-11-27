import yfinance as yf
import pandas as pd
import numpy as np

class AssetDataManager:
    def __init__(self, tickers: list, period: str = "2y"):
        self.tickers = tickers
        self.period = period
        self.data = pd.DataFrame()
        self.returns = pd.DataFrame()

    def fetch_data(self):
        """
        Télécharge les données ajustées de clôture pour tous les tickers.
        Gère l'alignement des dates (Inner Join) pour éviter les NaN.
        """
        print(f"Récupération des données pour {self.tickers}...")
        try:
            raw_data = yf.download(self.tickers, period=self.period, group_by='ticker', progress=False)
            
            df_close = pd.DataFrame()
            
            for t in self.tickers:
                if len(self.tickers) == 1:
                    df_close[t] = raw_data['Adj Close']
                else:
                    if 'Adj Close' in raw_data[t]:
                        df_close[t] = raw_data[t]['Adj Close']
                    elif 'Close' in raw_data[t]:
                        df_close[t] = raw_data[t]['Close']
            
            self.data = df_close.dropna()
            
            self.returns = self.data.pct_change().dropna()
            
            print(f"Données propres chargées : {self.returns.shape[0]} jours communs.")
            return self.data, self.returns
            
        except Exception as e:
            print(f"Erreur lors du téléchargement : {e}")
            return pd.DataFrame(), pd.DataFrame()

    def get_correlation_matrix(self):
        """Retourne la matrice de corrélation."""
        if self.returns.empty:
            return None
        return self.returns.corr()

    def get_covariance_matrix(self):
        """Retourne la matrice de covariance (annualisée)."""
        if self.returns.empty:
            return None
        return self.returns.cov() * 252