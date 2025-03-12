import numpy as np
import requests
import pandas as pd
from backend.app.api import fetch_coin_data
from datetime import datetime, timezone

BINANCE_ORDER_BOOK_URL = "https://api.binance.com/api/v3/depth"


def fetch_order_book(coin_symbol):
    """Fetch order book data to determine buying/selling pressure."""
    symbol = f"{coin_symbol.upper()}USDT"
    params = {"symbol": symbol, "limit": 100}

    try:
        response = requests.get(BINANCE_ORDER_BOOK_URL, params=params, timeout=10)
        data = response.json()

        bids = np.sum([float(order[1]) for order in data["bids"]])
        asks = np.sum([float(order[1]) for order in data["asks"]])

        buying_pressure = "High" if bids > asks else "Low" if asks > bids else "Medium"
        selling_pressure = "High" if asks > bids else "Low" if bids > asks else "Medium"

        return buying_pressure, selling_pressure
    except requests.exceptions.RequestException:
        return "Unknown", "Unknown"


def calculate_indicators(df):
    df["SMA_9"] = df["Close"].rolling(window=9, min_periods=1).mean()
    df["SMA_50"] = df["Close"].rolling(window=50, min_periods=1).mean()
    df["SMA_200"] = df["Close"].rolling(window=200, min_periods=1).mean()

    # MACD Calculation
    short_ema = df["Close"].ewm(span=12, adjust=False).mean()
    long_ema = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD_Line"] = short_ema - long_ema
    df["Signal_Line"] = df["MACD_Line"].ewm(span=9, adjust=False).mean()
    df["MACD_Histogram"] = df["MACD_Line"] - df["Signal_Line"]

    # RSI Calculation
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14, min_periods=1).mean()
    avg_loss = loss.rolling(window=14, min_periods=1).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # Stochastic RSI Calculation
    min_rsi = df["RSI"].rolling(window=14, min_periods=1).min()
    max_rsi = df["RSI"].rolling(window=14, min_periods=1).max()
    df["Stoch_K"] = 100 * (df["RSI"] - min_rsi) / (max_rsi - min_rsi)
    df["Stoch_D"] = df["Stoch_K"].rolling(3).mean()

    # Bollinger Bands Calculation
    df["SMA_20"] = df["Close"].rolling(window=20, min_periods=1).mean()
    df["StdDev"] = df["Close"].rolling(window=20, min_periods=1).std()
    df["Upper_Band"] = df["SMA_20"] + (2 * df["StdDev"])
    df["Lower_Band"] = df["SMA_20"] - (2 * df["StdDev"])

    return df


def fetch_market_data(coin_symbol):
    """Fetch real-time market data."""
    all_coins, error = fetch_coin_data()
    if error or not all_coins:
        return None

    coin_id = None
    for coin in all_coins:
        if coin["symbol"].lower() == coin_symbol.lower():
            coin_id = coin["id"]
            break

    if not coin_id:
        return None

    data, error = fetch_coin_data(coin_id)
    if error or not data:
        return None

    coin_data = data[0]  # Extract first (and only) entry
    timestamp = datetime.now(timezone.utc)

    df = pd.DataFrame([{
        "Date": timestamp,
        "Open": coin_data["current_price"],  # No historical open, using last price
        "Close": coin_data["current_price"],
        "High": coin_data["high_24h"],
        "Low": coin_data["low_24h"],
        "Volume": coin_data["total_volume"],
    }])

    df.set_index("Date", inplace=True)
    df = calculate_indicators(df)

    buying_pressure, selling_pressure = fetch_order_book(coin_symbol)

    return {
        "df": df,  # Full DataFrame with indicators
        "coin_symbol": coin_symbol.upper(),
        "market_sentiment": "Bullish" if df["SMA_9"].iloc[-1] > df["SMA_50"].iloc[-1] else "Bearish",
        "support_levels": [df["Low"].min() * 0.98, df["Low"].min() * 0.95],
        "resistance_levels": [df["High"].max() * 1.02, df["High"].max() * 1.05],
        "buying_pressure": buying_pressure,
        "selling_pressure": selling_pressure
    }
