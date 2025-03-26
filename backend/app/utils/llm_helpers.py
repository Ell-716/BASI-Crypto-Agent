import pandas as pd
import numpy as np


def resample_and_compute_indicators(data, timeframe):
    if isinstance(data, pd.DataFrame):
        df = data.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    else:
        df = pd.DataFrame([{
            "timestamp": h.timestamp,
            "open": h.price,
            "high": h.high,
            "low": h.low,
            "close": h.price,
            "volume": h.volume
        } for h in data])
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    df.set_index("timestamp", inplace=True)
    df = df.sort_index()

    df = df[df["close"] > 0.01]

    rule = {"1h": "h", "1d": "d", "1w": "W", "1m": "ME"}.get(timeframe, "d")
    df_resampled = df.resample(rule).agg({
        "open": "first", "high": "max", "low": "min",
        "close": "last", "volume": "sum"
    }).dropna()

    if df_resampled.empty:
        return df_resampled

    n = len(df_resampled)
    sma_window = min(n, 50)
    ema_window = min(n, 50)
    rsi_window = min(n, 14)
    bb_window = min(n, 20)

    df_resampled["SMA_50"] = df_resampled["close"].rolling(sma_window, min_periods=1).mean()
    df_resampled["SMA_200"] = df_resampled["close"].rolling(200, min_periods=1).mean()
    df_resampled["EMA_50"] = df_resampled["close"].ewm(span=ema_window, adjust=False).mean()
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
    avg_gain = gain.rolling(rsi_window, min_periods=1).mean()
    avg_loss = loss.rolling(rsi_window, min_periods=1).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df_resampled["RSI"] = (100 - (100 / (1 + rs))).clip(0, 100)

    # Stochastic RSI
    rsi_valid = df_resampled["RSI"]
    stoch_rsi_min = rsi_valid.rolling(14, min_periods=1).min()
    stoch_rsi_max = rsi_valid.rolling(14, min_periods=1).max()
    stoch_k = ((rsi_valid - stoch_rsi_min) / (stoch_rsi_max - stoch_rsi_min)).replace([np.inf, -np.inf], np.nan)
    df_resampled["Stoch_RSI_K"] = stoch_k.rolling(3, min_periods=1).mean().clip(0, 100).fillna(50)
    df_resampled["Stoch_RSI_D"] = df_resampled["Stoch_RSI_K"].rolling(3, min_periods=1).mean().clip(0, 100)

    # Bollinger Bands
    sma = df_resampled["close"].rolling(window=bb_window, min_periods=1).mean()
    std = df_resampled["close"].rolling(window=bb_window, min_periods=1).std()
    std = std.clip(upper=2 * df_resampled["close"].mean())
    df_resampled["BB_middle"] = sma.fillna(df_resampled["close"])
    df_resampled["BB_upper"] = (sma + 2 * std).fillna(df_resampled["close"])
    df_resampled["BB_lower"] = (sma - 2 * std).fillna(df_resampled["close"])

    return df_resampled
