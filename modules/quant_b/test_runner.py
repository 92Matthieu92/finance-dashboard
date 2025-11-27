import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from modules.quant_b.data_manager import AssetDataManager
from modules.quant_b.portfolio_engine import PortfolioEngine
from modules.quant_b.optimizer import PortfolioOptimizer

def print_allocation(tickers, weights, title="Allocation"):
    """Helper pour afficher proprement les poids."""
    print(f"\n📊 {title} :")
    print("-" * 30)
    for ticker, w in zip(tickers, weights):
        bar_len = int(w * 20)  
        bar = "█" * bar_len
        print(f"{ticker:<10} | {w:>6.1%} {bar}")
    print("-" * 30)

def main():
    print("=====================================================")
    print("      🧪 TEST RUNNER - MODULE QUANT B (COMPLET)      ")
    print("=====================================================\n")

    tickers = ["AAPL", "MSFT", "GOOGL", "GLD", "BTC-USD"]
    constraint_limit = 0.30 
    
    print(f"1. Chargement des données pour : {tickers}")
    dm = AssetDataManager(tickers, period="2y")
    data, returns = dm.fetch_data()

    if data.empty:
        print("Erreur critique : Pas de données.")
        return
    print(f"Données chargées : {len(data)} jours de trading.")

    engine = PortfolioEngine(returns)

    optimizer = PortfolioOptimizer(engine)
    
    print("\n" + "="*50)
    print("⚡ COMPARAISON DES STRATÉGIES D'OPTIMISATION")
    print("="*50)

    print("\n🔵 CAS A : Optimisation MATHÉMATIQUE (Sans limite)")
    res_raw = optimizer.run_monte_carlo_simulation(5000, apply_constraints=False)
    best_raw = res_raw['max_sharpe']
    
    print(f"\n🟠 CAS B : Optimisation RISK-MANAGED (Max {constraint_limit:.0%})")
    res_cons = optimizer.run_monte_carlo_simulation(5000, apply_constraints=True, max_weight=constraint_limit)
    best_cons = res_cons['max_sharpe']
    
    print_allocation(tickers, best_raw['weights'], title="Portefeuille 'MATHS' (Naïf)")
    print_allocation(tickers, best_cons['weights'], title="Portefeuille 'PRO' (Contraint)")

    print("\nIMPACT SUR LA PERFORMANCE :")
    print(f"{'Metrique':<15} | {'Naïf':<10} | {'Pro (30%)':<10} | {'Différence'}")
    print("-" * 55)
    
    metrics_names = ["Rendement", "Volatilité", "Sharpe"]
    
    for i, name in enumerate(metrics_names):
        val_raw = best_raw['metrics'][i]
        val_cons = best_cons['metrics'][i]
        
        if name == "Sharpe":
            fmt_raw = f"{val_raw:.2f}"
            fmt_cons = f"{val_cons:.2f}"
            diff = val_cons - val_raw
            fmt_diff = f"{diff:+.2f}"
        else:
            fmt_raw = f"{val_raw:.1%}"
            fmt_cons = f"{val_cons:.1%}"
            diff = val_cons - val_raw
            fmt_diff = f"{diff:+.1%}"
            
        print(f"{name:<15} | {fmt_raw:<10} | {fmt_cons:<10} | {fmt_diff}")

    print("\n" + "="*50)
    print("ANALYSE DE RISQUE APPROFONDIE (Sur le portefeuille PRO)")
    print("="*50)
    
    # VaR
    var_95, cvar_95 = engine.calculate_var_cvar(best_cons['weights'])
    print(f"• Value at Risk (95% Daily) : {var_95:.2%} (Perte max attendue 1 jour sur 20)")
    print(f"• CVaR (Expected Shortfall)   : {cvar_95:.2%} (Moyenne des pires cas)")

    # Diversification
    div_benefit = engine.calculate_diversification_benefit(best_cons['weights'])
    print(f"• Gain de Diversification     : {div_benefit['diversification_benefit']:.2%} (Volatilité éliminée grâce aux corrélations)")

    # Data Check pour le Graphique
    df_chart = engine.get_normalized_prices(best_cons['weights'])
    print("\nDonnées graphiques prêtes :")
    print(f"  - Colonnes : {list(df_chart.columns)}")
    print(f"  - Lignes   : {len(df_chart)}")
    print(f"  - Fin Valeur Portefeuille : {df_chart['PORTFOLIO'].iloc[-1]:.2f} (Base 100)")

if __name__ == "__main__":
    main()