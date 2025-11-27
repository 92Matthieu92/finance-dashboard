import os
import sys
import datetime
import pandas as pd
import yfinance as yf
import numpy as np

# Configuration
ASSETS_TO_TRACK = ["BTC-USD", "EURUSD=X", "^FCHI", "AAPL", "GLD"]
REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")

def ensure_dir():
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

def get_daily_stats(ticker):
    """Récupère les stats du jour pour un actif."""
    try:
        # On télécharge 1 an pour avoir assez d'historique pour la volatilité
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        
        # Gestion multi-index si yfinance renvoie un format complexe
        if isinstance(df.columns, pd.MultiIndex):
            df = df.xs(ticker, level=1, axis=1)

        if df.empty:
            return None

        # Calculs
        last_close = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        open_price = df['Open'].iloc[-1]
        
        # Variation
        daily_return = (last_close - prev_close) / prev_close
        
        # Volatilité (Annualisée sur 30 jours glissants)
        df['Returns'] = df['Close'].pct_change()
        volatility = df['Returns'].tail(30).std() * np.sqrt(252)
        
        # Max Drawdown (sur 1 an)
        roll_max = df['Close'].cummax()
        drawdown = (df['Close'] / roll_max) - 1
        max_dd = drawdown.min()

        return {
            "ticker": ticker,
            "last_close": last_close,
            "open": open_price,
            "return": daily_return,
            "volatility": volatility,
            "max_dd": max_dd
        }
    except Exception as e:
        print(f"Erreur sur {ticker}: {e}")
        return None

def generate_markdown_report(stats_list):
    """Génère le contenu du rapport Markdown."""
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    
    md = f"# 📊 Daily Quantitative Report - {date_str}\n"
    md += f"*Generated automatically at {time_str} via Cron Job*\n\n"
    
    md += "## Market Summary\n"
    md += "| Ticker | Open | Close | Daily Var | Volatility (30d) | Max DD (1y) |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
    
    for s in stats_list:
        trend = "🟢" if s['return'] >= 0 else "🔴"
        md += f"| **{s['ticker']}** | {s['open']:.2f} | {s['last_close']:.2f} | {trend} {s['return']:.2%} | {s['volatility']:.2%} | {s['max_dd']:.2%} |\n"
    
    md += "\n---\n"
    md += "### System Status\n"
    md += "- **Modules Loaded**: Quant A, Quant B\n"
    md += "- **Server**: Linux VM (Ubuntu)\n"
    
    return md

def main():
    print("--- Starting Daily Report Generation ---")
    ensure_dir()
    
    stats_list = []
    for ticker in ASSETS_TO_TRACK:
        print(f"Processing {ticker}...")
        data = get_daily_stats(ticker)
        if data:
            stats_list.append(data)
    
    if stats_list:
        md_content = generate_markdown_report(stats_list)
        
        filename = f"report_{datetime.datetime.now().strftime('%Y-%m-%d')}.md"
        filepath = os.path.join(REPORT_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)
        
        print(f"✅ Report successfully generated: {filepath}")
    else:
        print("❌ Failed to generate report (no data).")

if __name__ == "__main__":
    main()