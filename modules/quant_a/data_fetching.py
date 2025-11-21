import yfinance as yf
import pandas as pd

def get_realtime_data(ticker="^FCHI", period="1mo", interval="30m"):
    """
    Récupère les données du CAC 40 (^FCHI) en temps réel via Yahoo Finance.
    Garantit un format cohérent (colonne 'Timestamp').
    """
    try:
        data = yf.download(ticker, period=period, interval=interval)

        # Reset index to convert DatetimeIndex → column
        data = data.reset_index()

        # Harmoniser le nom de la colonne datetime
        if "Datetime" in data.columns:
            data = data.rename(columns={"Datetime": "Timestamp"})
        elif "Date" in data.columns:
            data = data.rename(columns={"Date": "Timestamp"})
        else:
            # Sécuriser en cas d'indice bizarre
            data.insert(0, "Timestamp", data.index)

        return data

    except Exception as e:
        print("Erreur lors de la récupération des données :", e)
        return pd.DataFrame()
