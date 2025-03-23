import pandas as pd
import numpy as np


def resample_and_compute_indicators(historical_data, timeframe):
    df = pd.DataFrame([{
        "timestamp": h.timestamp,
        "open": h.price,
        "high": h.high,
        "low": h.low,
        "close": h.price,
        "volume": h.volume
    } for h in historical_data])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)
    df = df.sort_index()

    rule = {
        "1h": "1h",
        "1d": "1d",
        "1w": "1w",
        "1m": "30d"
    }.get(timeframe, "1d")

    df_resampled = df.resample(rule).agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum"
    }).dropna()

    # Trend Indicators
    df_resampled["SMA_50"] = df_resampled["close"].rolling(window=50, min_periods=1).mean()
    df_resampled["SMA_200"] = df_resampled["close"].rolling(window=200, min_periods=1).mean()
    df_resampled["EMA_50"] = df_resampled["close"].ewm(span=50, adjust=False).mean()
    df_resampled["EMA_200"] = df_resampled["close"].ewm(span=200, adjust=False).mean()

    # MACD
    ema12 = df_resampled["close"].ewm(span=12, adjust=False).mean()
    ema26 = df_resampled["close"].ewm(span=26, adjust=False).mean()
    df_resampled["MACD"] = ema12 - ema26
    df_resampled["MACD_Signal"] = df_resampled["MACD"].ewm(span=9, adjust=False).mean()

    # RSI
    delta = df_resampled["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=14, min_periods=1).mean()
    avg_loss = loss.rolling(window=14, min_periods=1).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)

    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.fillna(0).clip(0, 100)
    df_resampled["RSI"] = rsi

    # Stochastic RSI
    stoch_rsi_min = rsi.rolling(window=14, min_periods=1).min()
    stoch_rsi_max = rsi.rolling(window=14, min_periods=1).max()
    denominator = stoch_rsi_max - stoch_rsi_min
    denominator[denominator == 0] = np.nan

    stoch_k = ((rsi - stoch_rsi_min) / denominator) * 100
    stoch_k = stoch_k.fillna(method="bfill").clip(0, 100)
    stoch_d = stoch_k.rolling(window=3, min_periods=1).mean()

    df_resampled["Stoch_RSI_K"] = stoch_k
    df_resampled["Stoch_RSI_D"] = stoch_d

    # Bollinger Bands
    middle_band = df_resampled["close"].rolling(window=20, min_periods=1).mean()
    std_dev = df_resampled["close"].rolling(window=20, min_periods=1).std().fillna(0)
    df_resampled["BB_upper"] = (middle_band + 2 * std_dev).fillna(method="bfill")
    df_resampled["BB_middle"] = middle_band.fillna(method="bfill")
    df_resampled["BB_lower"] = (middle_band - 2 * std_dev).fillna(method="bfill")

    return df_resampled
