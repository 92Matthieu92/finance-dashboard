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
        """
        weights = np.array(weights)
        portfolio_return = np.sum(self.mean_returns * weights) * 252
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix * 252, weights)))
        
        return portfolio_return, portfolio_volatility

    def calculate_sharpe_ratio(self, ret, vol, risk_free_rate=0.02):
        """Calcule le ratio de Sharpe."""
        if vol == 0: return 0
        return (ret - risk_free_rate) / vol

    def calculate_var_cvar(self, weights: np.array, confidence_level=0.95):
        """
        Calcule la Value at Risk (VaR) et la Conditional VaR (CVaR).
        """
        portfolio_daily_returns = self.returns_df.dot(weights)
        
        sorted_returns = portfolio_daily_returns.sort_values(ascending=True)
        
        cutoff_index = int((1 - confidence_level) * len(sorted_returns))
        
        var = abs(sorted_returns.iloc[cutoff_index])
        
        cvar = abs(sorted_returns.iloc[:cutoff_index].mean())
        
        return var, cvar

    def get_drawdown_series(self, weights: np.array):
        """Calcule la série de Drawdown pour analyse graphique."""
        portfolio_daily_returns = self.returns_df.dot(weights)
        cumulative_returns = (1 + portfolio_daily_returns).cumprod() * 100
        
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max
        return drawdown, drawdown.min()


    def calculate_diversification_benefit(self, weights: np.array):
        """
        Quantifie l'effet de diversification.
        Différence entre la moyenne pondérée des volatilités et la volatilité réelle.
        """
        weights = np.array(weights)
        
        asset_vols = self.returns_df.std() * np.sqrt(252)
        
        weighted_avg_vol = np.sum(weights * asset_vols)
        
        _, portfolio_vol = self.calculate_portfolio_performance(weights)
        
        diversification_benefit = weighted_avg_vol - portfolio_vol
        
        return {
            "weighted_avg_vol": weighted_avg_vol,
            "portfolio_vol": portfolio_vol,
            "diversification_benefit": diversification_benefit
        }

    def get_normalized_prices(self, weights: np.array):
        """
        Génère un DataFrame base 100 pour tous les actifs ET le portefeuille.
        """
        normalized_assets = (1 + self.returns_df).cumprod() * 100
        
        portfolio_returns = self.returns_df.dot(weights)
        portfolio_curve = (1 + portfolio_returns).cumprod() * 100
        
        combined_df = normalized_assets.copy()
        combined_df['PORTFOLIO'] = portfolio_curve
        
        return combined_df