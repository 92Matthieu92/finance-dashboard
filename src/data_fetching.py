import yfinance as yf
import pandas as pd

def get_realtime_data(ticker="^FCHI", period="1mo", interval="30m"):
    """
    Récupère les données du CAC 40 (^FCHI) en quasi temps réel via Yahoo Finance.
    """
    try:
        data = yf.download(ticker, period=period, interval=interval)
        data = data.reset_index()
        data = data.rename(columns={"Date": "Timestamp"})
        return data

    except Exception as e:
        print("Erreur lors de la récupération des données :", e)
        return pd.DataFrame()
