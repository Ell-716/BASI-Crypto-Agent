import pandas as pd


def aggregate_candles(df, timeframe):
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    # Preserve indicator columns
    indicator_columns = [col for col in df.columns if col not in ["Open", "High", "Low", "Close", "Volume"]]
    indicators_df = df[indicator_columns] if indicator_columns else None

    # Resample OHLCV data only
    if timeframe == "1h":
        ohlcv_df = df[["Open", "High", "Low", "Close", "Volume"]].tail(96)
    elif timeframe == "1d":
        ohlcv_df = df[["Open", "High", "Low", "Close", "Volume"]].resample("1D").agg({
            "Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"
        }).dropna().tail(120)
    elif timeframe == "1w":
        ohlcv_df = df[["Open", "High", "Low", "Close", "Volume"]].resample("1W").agg({
            "Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"
        }).dropna().tail(96)
    elif timeframe == "1m":
        ohlcv_df = df[["Open", "High", "Low", "Close", "Volume"]].resample("ME").agg({
            "Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"
        }).dropna().tail(36)
    else:
        return df

    # Reattach indicator columns
    if indicators_df is not None:
        filtered_df = ohlcv_df.join(indicators_df, how="left")
    else:
        filtered_df = ohlcv_df

    return filtered_df
