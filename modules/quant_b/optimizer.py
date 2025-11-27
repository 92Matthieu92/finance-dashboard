import numpy as np
import pandas as pd

class PortfolioOptimizer:
    def __init__(self, engine):
        """
        Args:
            engine (PortfolioEngine): Instance du moteur initialisée avec les données.
        """
        self.engine = engine

    def run_monte_carlo_simulation(self, num_simulations=5000, apply_constraints=False, max_weight=0.35):
        """
        Génère des portefeuilles aléatoires pour visualiser la Frontière Efficiente.
        Intègre une gestion des contraintes de pondération (Capping).

        Args:
            num_simulations (int): Nombre d'itérations.
            apply_constraints (bool): Si True, rejette les portefeuilles trop concentrés.
            max_weight (float): Poids maximum autorisé pour un seul actif (ex: 0.35 pour 35%).
        """
        min_feasible = 1.0 / self.engine.num_assets
        if apply_constraints and max_weight < min_feasible:
            print(f"ERREUR CONFIG: Impossible d'imposer Max {max_weight:.1%} avec {self.engine.num_assets} actifs.")
            print(f"Contrainte désactivée (Minimum requis: {min_feasible:.1%})")
            apply_constraints = False

        results = np.zeros((3, num_simulations))
        weights_record = []
        
        valid_count = 0     
        attempts = 0       
        max_attempts = num_simulations * 50
        
        print(f"Simulation Monte Carlo ({num_simulations} itérations)...")
        if apply_constraints:
            print(f"Contrainte Active : Aucun actif ne dépasse {max_weight:.1%}")

        while valid_count < num_simulations:
            attempts += 1
            
            if attempts > max_attempts:
                print(f"Arrêt prématuré : Trop de rejets. {valid_count} portefeuilles générés.")
                results = results[:, :valid_count]
                break

            weights = np.random.random(self.engine.num_assets)
            weights /= np.sum(weights)
            
            if apply_constraints:
                if np.any(weights > max_weight):
                    continue 

            weights_record.append(weights)
            
            ret, vol = self.engine.calculate_portfolio_performance(weights)
            
            results[0,valid_count] = ret
            results[1,valid_count] = vol
            results[2,valid_count] = self.engine.calculate_sharpe_ratio(ret, vol)
            
            valid_count += 1

        if valid_count == 0:
            return None

        
        max_sharpe_idx = np.argmax(results[2])
        best_weights = weights_record[max_sharpe_idx]
        best_metrics = results[:, max_sharpe_idx]
        
        min_vol_idx = np.argmin(results[1])
        min_vol_weights = weights_record[min_vol_idx]
        min_vol_metrics = results[:, min_vol_idx]

        return {
            "results_array": results, 
            "max_sharpe": {"weights": best_weights, "metrics": best_metrics},
            "min_vol": {"weights": min_vol_weights, "metrics": min_vol_metrics}
        }