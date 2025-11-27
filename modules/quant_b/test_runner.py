# Ce fichier sert à tester ton module Quant B sans lancer Streamlit
# C'est ici que tu travailles pour vérifier tes algos.

import sys
import os

# Ajout du path pour importer les modules proprement si exécuté depuis ce dossier
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from data_manager import AssetDataManager
from portfolio_engine import PortfolioEngine
from optimizer import PortfolioOptimizer

def main():
    print("=== TEST MODULE QUANT B (BACKEND ONLY) ===\n")

    # 1. Définition des actifs
    tickers = ["AAPL", "MSFT", "GOOGL", "GLD", "BTC-USD"]
    print(f"Actifs sélectionnés : {tickers}")

    # 2. Chargement Data
    dm = AssetDataManager(tickers, period="2y")
    data, returns = dm.fetch_data()

    if data.empty:
        print("Erreur de données. Arrêt.")
        return

    # 3. Initialisation Moteur
    engine = PortfolioEngine(returns)

    # 4. Test d'un portefeuille Équilibré (Equal Weight)
    print("\n--- Analyse Portefeuille Équilibré ---")
    num_assets = len(tickers)
    equal_weights = [1/num_assets] * num_assets
    
    ret, vol = engine.calculate_portfolio_performance(equal_weights)
    sharpe = engine.calculate_sharpe_ratio(ret, vol)
    var_95, cvar_95 = engine.calculate_var_cvar(equal_weights)
    _, max_dd = engine.get_drawdown_series(equal_weights)

    print(f"Poids : {[round(w, 2) for w in equal_weights]}")
    print(f"Rendement Annuel Espéré : {ret:.2%}")
    print(f"Volatilité Annuelle     : {vol:.2%}")
    print(f"Ratio de Sharpe         : {sharpe:.2f}")
    print(f"VaR (95% Daily)         : {var_95:.2%}")
    print(f"Max Drawdown            : {max_dd:.2%}")

    # 5. Optimisation (Monte Carlo)
    print("\n--- Optimisation Monte Carlo ---")
    optimizer = PortfolioOptimizer(engine)
    sim_results = optimizer.run_monte_carlo_simulation(num_simulations=5000)
    
    best_sharpe = sim_results['max_sharpe']
    
    print("\n🏆 Meilleur Portefeuille (Max Sharpe) :")
    print(f"Rendement : {best_sharpe['metrics'][0]:.2%}")
    print(f"Volatilité: {best_sharpe['metrics'][1]:.2%}")
    print(f"Sharpe    : {best_sharpe['metrics'][2]:.2f}")
    
    print("Allocation Optimale :")
    for tick, w in zip(tickers, best_sharpe['weights']):
        print(f"  - {tick}: {w:.1%}")

if __name__ == "__main__":
    main()