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
        print(f"📥 Récupération des données pour {self.tickers}...")
        try:
            # Téléchargement groupé
            raw_data = yf.download(self.tickers, period=self.period, group_by='ticker', progress=False)
            
            df_close = pd.DataFrame()
            
            for t in self.tickers:
                # Gestion du cas où yfinance renvoie un multi-index ou non selon le nombre d'actifs
                if len(self.tickers) == 1:
                    df_close[t] = raw_data['Adj Close']
                else:
                    if 'Adj Close' in raw_data[t]:
                        df_close[t] = raw_data[t]['Adj Close']
                    elif 'Close' in raw_data[t]:
                        df_close[t] = raw_data[t]['Close']
            
            # Nettoyage crucial pour le calcul matriciel
            # On supprime les lignes où il manque une donnée (jours fériés différents selon pays)
            self.data = df_close.dropna()
            
            # Calcul des rendements logarithmiques (plus précis pour les maths financières)
            # ou arithmétiques. Ici on reste sur arithmétique simple pour la lisibilité.
            self.returns = self.data.pct_change().dropna()
            
            print(f"✅ Données propres chargées : {self.returns.shape[0]} jours communs.")
            return self.data, self.returns
            
        except Exception as e:
            print(f"❌ Erreur lors du téléchargement : {e}")
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
        # Covariance journalière * 252 jours de trading
        return self.returns.cov() * 252