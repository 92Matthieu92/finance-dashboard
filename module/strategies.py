import pandas as pd
import numpy as np


def apply_buy_hold(df):
    """
    Buy & Hold : position = 1 tout le temps.
    """
    df['signal_bh'] = 1
    df['strategy_bh'] = (1 + df['returns']).cumprod()
    return df


def apply_momentum(df, window=20):
    """
    Momentum : achat si prix > SMA(window)
    """
    df['sma'] = df['price'].rolling(window).mean()

    # Conversion explicite en Series → fix définitif
    price = df['price'].squeeze()
    sma = df['sma'].squeeze()

    # Alignement explicite
    price, sma = price.align(sma, join='inner')

    df.loc[price.index, 'signal_mom'] = (price > sma).astype(int)

    # retours stratégique momentum
    df['strategy_mom_ret'] = df['signal_mom'].shift(1) * df['returns']
    df['strategy_mom'] = (1 + df['strategy_mom_ret']).cumprod()

    return df



def compute_rsi(series, window=14):
    """
    Calcule le RSI.
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()

    rs = gain / loss
    return 100 - (100 / (1 + rs))


def apply_rsi_strategy(df, rsi_low=30, rsi_high=70):
    """
    Achat si RSI < rsi_low
    Vente si RSI > rsi_high
    """
    df['rsi'] = compute_rsi(df['price'])

    df['signal_rsi'] = 0
    df.loc[df['rsi'] < rsi_low, 'signal_rsi'] = 1
    df.loc[df['rsi'] > rsi_high, 'signal_rsi'] = 0

    # retours RSI
    df['strategy_rsi_ret'] = df['signal_rsi'].shift(1) * df['returns']
    df['strategy_rsi'] = (1 + df['strategy_rsi_ret']).cumprod()
    return df
