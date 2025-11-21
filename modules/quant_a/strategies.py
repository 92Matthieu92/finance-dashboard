def buy_and_hold(df):
    df["BH_Return"] = df["Close"] / df["Close"].iloc[0]
    return df


def momentum_strategy(df, short=20, long=50):
    df["SMA_short"] = df["Close"].rolling(short).mean()
    df["SMA_long"] = df["Close"].rolling(long).mean()

    df["Signal"] = (df["SMA_short"] > df["SMA_long"]).astype(int)
    df["Position"] = df["Signal"].shift(1).fillna(0)

    df["Daily_Return"] = df["Close"].pct_change()
    df["Strategy_Return"] = df["Position"] * df["Daily_Return"]

    df["Cumulative_Strategy"] = (1 + df["Strategy_Return"]).cumprod()

    return df
