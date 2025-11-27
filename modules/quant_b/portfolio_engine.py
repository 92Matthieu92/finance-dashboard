import numpy as np
import pandas as pd

class PortfolioEngine:
    def __init__(self, returns_df: pd.DataFrame):
        """
        Args:
            returns_df (pd.DataFrame): DataFrame des rendements journaliers des actifs.
        """
        self.returns_df = returns_df
        self.mean_returns = returns_df.mean()
        self.cov_matrix = returns_df.cov()
        self.num_assets = len(returns_df.columns)

    def calculate_portfolio_performance(self, weights: np.array):
        """
        Calcule le rendement et la volatilité attendus du portefeuille.
        
        Maths:
        - Rendement = Transposée(Poids) * Rendements Moyens
        - Volatilité = Racine( Transposée(Poids) * MatriceCov * Poids )
        """
        weights = np.array(weights)
        
        # Rendement annualisé
        portfolio_return = np.sum(self.mean_returns * weights) * 252
        
        # Volatilité annualisée
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix * 252, weights)))
        
        return portfolio_return, portfolio_volatility

    def calculate_sharpe_ratio(self, ret, vol, risk_free_rate=0.02):
        """Calcule le ratio de Sharpe."""
        if vol == 0: return 0
        return (ret - risk_free_rate) / vol

    def calculate_var_cvar(self, weights: np.array, confidence_level=0.95):
        """
        Calcule la Value at Risk (VaR) et la Conditional VaR (CVaR) historiques.
        C'est une métrique de risque essentielle pour les pros.
        """
        # Calcul des rendements journaliers historiques du portefeuille pondéré
        portfolio_daily_returns = self.returns_df.dot(weights)
        
        # Tri des rendements du pire au meilleur
        sorted_returns = portfolio_daily_returns.sort_values(ascending=True)
        
        # Index de la coupure (ex: 5% pires cas)
        cutoff_index = int((1 - confidence_level) * len(sorted_returns))
        
        # VaR = La valeur à cet index
        var = abs(sorted_returns.iloc[cutoff_index])
        
        # CVaR (Expected Shortfall) = Moyenne des pertes au-delà de la VaR
        cvar = abs(sorted_returns.iloc[:cutoff_index].mean())
        
        return var, cvar

    def get_drawdown_series(self, weights: np.array):
        """Calcule la série de Drawdown pour analyse graphique."""
        # Reconstruction de la courbe de prix (Base 100)
        portfolio_daily_returns = self.returns_df.dot(weights)
        cumulative_returns = (1 + portfolio_daily_returns).cumprod() * 100
        
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max
        return drawdown, drawdown.min()