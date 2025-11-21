import streamlit as st
from modules.quant_a.data_fetching import get_realtime_data
from modules.quant_a.strategies import buy_and_hold, momentum_strategy
from modules.quant_a.metrics import sharpe_ratio, max_drawdown
import plotly.graph_objects as go


def run_single_asset_dashboard():
    st.title("Analyse CAC 40 – Module Quant A")

    st.markdown("### Actif analysé : **CAC 40 (^FCHI)**")

    # Paramètres utilisateur
    short_window = st.slider("Période MA courte", 5, 50, 20)
    long_window = st.slider("Période MA longue", 20, 200, 50)

    # Données
    df = get_realtime_data(ticker="^FCHI")

    if df.empty:
        st.error("Impossible de récupérer les données du CAC 40.")
        return

    # Stratégies
    df = buy_and_hold(df)
    df = momentum_strategy(df, short_window, long_window)

    # Graphique prix
    st.subheader("Prix du CAC 40")
    fig_price = go.Figure()
    fig_price.add_trace(go.Scatter(x=df["Timestamp"], y=df["Close"], name="Close"))
    st.plotly_chart(fig_price, use_container_width=True)

    # Graphique performances
    st.subheader("Performances stratégiques")
    fig_perf = go.Figure()
    fig_perf.add_trace(go.Scatter(x=df["Timestamp"], y=df["BH_Return"], name="Buy & Hold"))
    fig_perf.add_trace(go.Scatter(x=df["Timestamp"], y=df["Cumulative_Strategy"], name="Momentum"))
    st.plotly_chart(fig_perf, use_container_width=True)

    # Metrics
    st.subheader("Indicateurs de performance")
    sr = sharpe_ratio(df)
    if sr is None:
        st.warning("Sharpe Ratio non disponible (pas assez de données)")
    else:
        st.write("📈 **Sharpe Ratio** :", round(sr, 3))    
    st.write("📌 **Max Drawdown** :", round(max_drawdown(df), 3))
