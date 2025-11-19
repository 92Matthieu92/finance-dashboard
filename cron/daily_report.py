from src.data_fetching import get_realtime_data
from src.metrics import sharpe_ratio, max_drawdown
from datetime import datetime

df = get_realtime_data(ticker="^FCHI")

path = f"data/report_{datetime.now().date()}.txt"

with open(path, "w") as f:
    f.write("Rapport Quotidien – CAC 40\n")
    f.write("============================\n\n")
    f.write(f"Sharpe Ratio : {sharpe_ratio(df)}\n")
    f.write(f"Max Drawdown : {max_drawdown(df)}\n")
    f.write(f"Clôture : {df['Close'].iloc[-1]}\n")
