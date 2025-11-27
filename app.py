import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# --- IMPORTS DES MODULES (Vérifiez la structure des dossiers !) ---

# Import général de la classe QuantAEngine grâce à modules/quantA/__init__.py
try:
    from modules.quant_A import QuantAEngine 
    
    # Quant B Imports
    from modules.quant_b.data_manager import AssetDataManager
    from modules.quant_b.portfolio_engine import PortfolioEngine
    from modules.quant_b.optimizer import PortfolioOptimizer
except ImportError as e:
    st.error(f"Erreur d'importation des modules. Assurez-vous que les dossiers 'modules/quantA' et 'modules/quantB' existent et contiennent tous les fichiers (incluant __init__.py). Détails: {e}")
    st.stop()


# --- CONFIGURATION DE BASE ---
APP_TITLE = "Quant Desk Terminal"
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS MINIMALISTE & MODERNE ---
st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }
    h1 { font-weight: 700; color: #f0f2f6; }
    
    /* Conteneur de la métrique */
    div[data-testid="stMetric"] { 
        background-color: #1e2129; 
        border-radius: 10px; 
        padding: 10px; 
        border: 1px solid #2b303b; 
        transition: transform 0.1s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
    }
    
    /* ------------------------------------------- */
    /* NOUVELLES RÈGLES POUR LE TEXTE DES MÉTRIQUES */
    /* ------------------------------------------- */
    
    /* Cible le TITRE (Label) de la métrique et le met en blanc */
    label[data-testid="stMetricLabel"] > div {
        color: #FFFFFF !important; /* Blanc pur */
    }
            
    label[data-testid="stMetricLabel"] > p {
        font-weight: 700 !important;
    }
    
    /* Cible la VALEUR de la métrique et la met en blanc */
    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important; /* Blanc pur */
        font-weight: 300; /* Optionnel: assure un gras pour la valeur */
    }
    
    /* Optionnel: pour les deltas (chiffres vert/rouge) s'ils ne sont pas assez clairs */
    /* div[data-testid="stMetricDelta"] {
        font-weight: 700;
    } */

    /* Style des boutons (inchangé) */
    .stButton>button { 
        width: 100%; 
        border-radius: 5px; 
        font-weight: bold; 
        background-color: #3b5998;
        color: white;
    }
    .stButton>button:hover {
        background-color: #4b69b8;
    }
</style>
""", unsafe_allow_html=True)


# --- NAVIGATION ET GLOBAL REFRESH ---
st.sidebar.title("🏛️ Navigation")
app_mode = st.sidebar.radio("Sélectionner un Module", ["Single Asset", "Portfolio Allocator"])
st.sidebar.markdown("---")

# Logic to automatically refresh the app every 5 minutes (or user-defined)
REFRESH_RATE = st.sidebar.number_input("Auto-Refresh (minutes)", 1, 60, 5)

if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > (REFRESH_RATE * 60):
    st.session_state.last_refresh = time.time()
    st.rerun()
    
def run_quant_a():
    st.title("🔎 Single Asset Analysis")
    st.caption(f"Dernière mise à jour: {time.strftime('%H:%M:%S')}")
    
    # 1. Inputs
    st.sidebar.subheader("Asset & Timeframe")
    ticker = st.sidebar.text_input("Ticker", value="^FCHI").upper() # Utiliser le ^FCHI du test
    period = st.sidebar.select_slider("Période", options=["6mo", "1y", "2y", "5y"], value="2y")
    
    st.sidebar.subheader("Stratégies Techniques")
    strat_select = st.sidebar.radio("Stratégie à Afficher", ["Momentum", "RSI"])
    
    # Paramètres pour les deux stratégies
    momentum_w = st.sidebar.number_input("Fenêtre Momentum (jours)", 5, 50, 20)
    rsi_low = st.sidebar.number_input("RSI Low (Achat)", 10, 40, 30)
    rsi_high = st.sidebar.number_input("RSI High (Vente)", 60, 90, 70)
    
    if st.button("Lancer l'Analyse Quant A", key="run_qa_btn"):
        with st.spinner('Chargement des données et calculs...'):
            try:
                # --- NOUVEAU LANCEMENT via la CLASSE ---
                engine = QuantAEngine(ticker=ticker, period=period, interval="1d")
                df, metrics = engine.run(
                    momentum_window=momentum_w, 
                    rsi_low=rsi_low, 
                    rsi_high=rsi_high
                )
                
                # Récupérer la dernière valeur pour le prix actuel (Approximation)
                current_price = df['price'].iloc[-1]
                
                # Définir les clés dynamiques pour la stratégie sélectionnée
                if strat_select == "Momentum":
                    strategy_key = 'strategy_mom'
                    sharpe_key = 'sharpe_mom'
                    maxdd_key = 'maxdd_mom'
                else:
                    strategy_key = 'strategy_rsi'
                    sharpe_key = 'sharpe_rsi'
                    maxdd_key = 'maxdd_rsi'
                
                # UI Layout
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Prix Actuel", f"{current_price:,.2f}", delta=f"{df['returns'].iloc[-1]:.2%}")
                k2.metric(f"Sharpe ({strat_select})", f"{metrics[sharpe_key]:.2f}", help="vs Buy & Hold")
                k3.metric("Sharpe (B&H)", f"{metrics['sharpe_bh']:.2f}")
                k4.metric(f"Max DD ({strat_select})", f"{metrics[maxdd_key]:.2%}")
                
                # Chart
                st.subheader(f"Courbe de Performance : {strat_select} vs Buy & Hold")
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df[strategy_key], name=f'Stratégie {strat_select}', line=dict(color='#00ff00', width=2)))
                fig.add_trace(go.Scatter(x=df.index, y=df['strategy_bh'], name='Buy & Hold', line=dict(color='#8D99AE', dash='dot')))
                fig.update_layout(template="plotly_dark", height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
                
                # Note: Le bonus ML simple n'a pas été recréé dans votre structure QuantA, 
                # donc on omet cette section ici pour éviter les erreurs.

            except ValueError as ve:
                st.warning(str(ve))
            except Exception as e:
                st.error(f"Erreur d'exécution de Quant A : {e}")


# ==============================================================================
# 🔵 MODULE B : PORTFOLIO OPTIMIZER (Ton travail)
# ... (Le reste du code de run_quant_b reste inchangé)
# ==============================================================================
def run_quant_b():
    st.title("⚖️ Portfolio Optimizer (Multi-Asset)")
    
    # 1. Inputs Latéraux
    st.sidebar.subheader("Univers d'Investissement")
    default_assets = ["AAPL", "MSFT", "GOOGL", "GLD", "BTC-USD"]
    selected_assets = st.sidebar.multiselect(
        "Actifs du Portefeuille", 
        ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "GLD", "BTC-USD", "EURUSD=X"], 
        default=default_assets
    )
    
    st.sidebar.subheader("Paramètres de Risque")
    period_b = st.sidebar.selectbox("Historique (Backtest)", ["1y", "2y", "5y"], index=1)
    
    # --- LA CONTRAINTE PRO ---
    use_constraints = st.sidebar.checkbox("Activer Contrainte (Capping)", value=True)
    MAX_WEIGHT_LIMIT = st.sidebar.slider("Poids Max par Actif", 0.1, 1.0, 0.30, 0.05)
    
    if st.button("Optimiser et Simuler", key="run_qb_btn"):
        if len(selected_assets) < 2:
            st.error("Il faut au moins 2 actifs pour construire un portefeuille.")
            st.stop()
            
        with st.status("Calculs Quantitatifs en cours...", expanded=True) as status:
            
            # A. Chargement Data
            st.write("📥 Récupération des données marché...")
            dm = AssetDataManager(selected_assets, period=period_b)
            _, returns = dm.fetch_data()
            
            if returns.empty:
                st.error("Pas de données communes pour cette période.")
                st.stop()
                
            # B. Initialisation Moteur & Optimisation
            engine = PortfolioEngine(returns)
            optimizer = PortfolioOptimizer(engine)
            
            st.write(f"🚀 Lancement de 5000 simulations Monte Carlo | Max Poids: {MAX_WEIGHT_LIMIT:.0%}...")
            results = optimizer.run_monte_carlo_simulation(5000, apply_constraints=use_constraints, max_weight=MAX_WEIGHT_LIMIT)
            
            if not results:
                st.error("Impossible de trouver un portefeuille : Contraintes trop strictes ou données manquantes.")
                st.stop()
                
            best_port = results['max_sharpe']
            metrics = best_port['metrics']
            status.update(label="Optimisation terminée !", state="complete", expanded=False)

        # --- D. AFFICHAGE DES RÉSULTATS ---
        
        # 1. Métriques Principales
        st.subheader("Performance du Portefeuille Optimal (Max Sharpe)")
        col1, col2, col3 = st.columns(3)
        col1.metric("Rendement Espéré", f"{metrics[0]:.2%}")
        col2.metric("Volatilité", f"{metrics[1]:.2%}")
        col3.metric("Sharpe Ratio", f"{metrics[2]:.2f}")
        
        # 2. Allocation et Frontière
        c_alloc, c_ef = st.columns([1, 2])
        
        with c_alloc:
            st.subheader("Allocation & Poids")
            # Graphique Allocation
            labels = [t for t, w in zip(selected_assets, best_port['weights']) if w > 0.01]
            values = [w for w in best_port['weights'] if w > 0.01]
            
            fig_pie = px.pie(names=labels, values=values, hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=250, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_pie, use_container_width=True)

            # Tableau des poids
            alloc_df = pd.DataFrame({"Actif": selected_assets, "Poids": best_port['weights']})
            alloc_df = alloc_df.sort_values("Poids", ascending=False)
            st.dataframe(alloc_df.style.format({"Poids": "{:.1%}"}), use_container_width=True, hide_index=True)
            
        with c_ef:
            st.subheader("Frontière Efficiente")
            sim_res = results['results_array'] # [Ret, Vol, Sharpe]
            
            fig_ef = px.scatter(x=sim_res[1], y=sim_res[0], 
                                color=sim_res[2], 
                                labels={'x':'Volatilité', 'y':'Rendement'},
                                title="Risque vs Rendement des Portefeuilles Simulés")
            fig_ef.add_trace(go.Scatter(
                x=[metrics[1]], y=[metrics[0]], 
                mode='markers', marker=dict(color='red', size=15, symbol='star'),
                name='Max Sharpe'
            ))
            
            fig_ef.update_layout(
                template="plotly_dark", height=450, 
                xaxis_title="Volatilité (Risque)", yaxis_title="Rendement Espéré",
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_ef, use_container_width=True)

        # 3. Performance & Risque
        st.markdown("---")
        st.subheader("Backtest et Analyse de Risque")
        
        tab1, tab2 = st.tabs(["📈 Courbe de Performance", "🛡️ Risque Avancé"])
        
        with tab1:
            df_norm = engine.get_normalized_prices(best_port['weights'])
            fig_perf = go.Figure()
            # Portefeuille en Blanc Gros
            fig_perf.add_trace(go.Scatter(x=df_norm.index, y=df_norm['PORTFOLIO'], name="Portefeuille Optimal", line=dict(color='white', width=3)))
            # Autres actifs en fin
            for col in df_norm.columns:
                if col != 'PORTFOLIO':
                    fig_perf.add_trace(go.Scatter(x=df_norm.index, y=df_norm[col], name=col, opacity=0.3, line=dict(width=1)))
            
            fig_perf.update_layout(template="plotly_dark", height=450, title="Croissance Base 100 vs Composants", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_perf, use_container_width=True)
            
        with tab2:
            var_95, cvar_95 = engine.calculate_var_cvar(best_port['weights'])
            div_benefit = engine.calculate_diversification_benefit(best_port['weights'])
            
            r1, r2, r3 = st.columns(3)
            r1.metric("VaR (95% Daily)", f"{var_95:.2%}", help="Perte maximale attendue 1 jour sur 20")
            r2.metric("CVaR (Pire Cas)", f"{cvar_95:.2%}", help="Moyenne des pertes dans les 5% pires jours")
            r3.metric("Gain Diversification", f"{div_benefit['diversification_benefit']:.2%}")


# --- Lancement du Module ---
if app_mode == "Single Asset":
    run_quant_a()
else:
    run_quant_b()