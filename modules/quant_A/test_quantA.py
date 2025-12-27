from modules.quant_A import QuantAEngine

def main():
    print("=== TEST QUANT A ENGINE ===")

    # Initialisation
    engine = QuantAEngine(
        ticker="^FCHI",      # CAC 40
        period="2y",         # plus rapide pour tester
        interval="1d"
    )

    # Run complet (data + stratégies + métriques)
    df, metrics = engine.run(
        momentum_window=20,
        rsi_low=30,
        rsi_high=70
    )

    print("\n--- Aperçu DataFrame ---")
    print(df.head())
    print(df.tail())

    print("\n--- Colonnes disponibles ---")
    print(df.columns)

    print("\n--- Métriques ---")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")

    # Vérification visuelle des dernières valeurs
    print("\n--- Dernières valeurs des courbes ---")
    print("Buy & Hold :", df['strategy_bh'].iloc[-1])
    print("Momentum   :", df['strategy_mom'].iloc[-1])
    print("RSI        :", df['strategy_rsi'].iloc[-1])

    print("\nTest terminé avec succès.")


if __name__ == "__main__":
    main()
