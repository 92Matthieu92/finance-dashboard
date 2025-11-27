import numpy as np
import pandas as pd

class PortfolioOptimizer:
    def __init__(self, engine):
        """
        Args:
            engine (PortfolioEngine): Instance du moteur initialisée avec les données.
        """
        self.engine = engine

    def run_monte_carlo_simulation(self, num_simulations=5000):
        """
        Génère des milliers de portefeuilles aléatoires pour visualiser la 
        Frontière Efficiente.
        """
        results = np.zeros((3, num_simulations))
        weights_record = []
        
        print(f"🚀 Lancement de {num_simulations} simulations Monte Carlo...")

        for i in range(num_simulations):
            # 1. Générer des poids aléatoires
            weights = np.random.random(self.engine.num_assets)
            # 2. Normaliser pour que la somme = 1 (100%)
            weights /= np.sum(weights)
            weights_record.append(weights)
            
            # 3. Calculer Perf
            ret, vol = self.engine.calculate_portfolio_performance(weights)
            
            # 4. Stocker (Rendement, Volatilité, Sharpe)
            results[0,i] = ret
            results[1,i] = vol
            results[2,i] = self.engine.calculate_sharpe_ratio(ret, vol)

        # Trouver le portefeuille avec le meilleur Sharpe (Tangency Portfolio)
        max_sharpe_idx = np.argmax(results[2])
        best_weights = weights_record[max_sharpe_idx]
        best_metrics = results[:, max_sharpe_idx]
        
        # Trouver le portefeuille avec la volatilité min (Min Variance)
        min_vol_idx = np.argmin(results[1])
        min_vol_weights = weights_record[min_vol_idx]
        min_vol_metrics = results[:, min_vol_idx]

        return {
            "results_array": results, # Pour le plotting futur
            "max_sharpe": {"weights": best_weights, "metrics": best_metrics},
            "min_vol": {"weights": min_vol_weights, "metrics": min_vol_metrics}
        }