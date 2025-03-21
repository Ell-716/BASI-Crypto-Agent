import numpy as np
import requests
import pandas as pd
from datetime import datetime
from backend.app.prediction.charts import plot_price_chart, plot_macd_rsi, plot_bollinger_bands

BINANCE_ORDER_BOOK_URL = "https://api.binance.com/api/v3/depth"
COINGECKO_MARKET_CHART_URL = "https://api.coingecko.com/api/v3/coins/{}/market_chart"


def fetch_market_data(coin_symbol, days=365):

    url = COINGECKO_MARKET_CHART_URL.format(coin_symbol.lower())
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}

    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    if response.status_code == 200:
        data = response.json()

        timestamps = [entry[0] for entry in data["prices"]]
        closes = [entry[1] for entry in data["prices"]]
        highs = [entry[1] for entry in data["prices"]]
        lows = [entry[1] for entry in data["prices"]]
        volumes = [entry[1] for entry in data["total_volumes"]]

        df = pd.DataFrame({
            "Date": [datetime.fromtimestamp(ts / 1000) for ts in timestamps],
            "Open": closes,
            "Close": closes,
            "High": highs,
            "Low": lows,
            "Volume": volumes
        })

        df["Open"] = df["Close"].shift(1).fillna(df["Close"])
        df["High"] = df["Close"] * np.random.uniform(1.001, 1.02, len(df))
        df["Low"] = df["Close"] * np.random.uniform(0.98, 0.999, len(df))

        df.set_index("Date", inplace=True)
        return df
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None


def fetch_order_book(coin_symbol):

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


def generate_and_plot_charts(coin_symbol, timeframe=None):

    market_data = fetch_market_data(coin_symbol)
    if market_data is not None:
        df = calculate_indicators(market_data)

        plot_price_chart(df, coin_symbol, timeframe)
        plot_macd_rsi(df, timeframe)
        plot_bollinger_bands(df, coin_symbol, timeframe)
    else:
        print(f"❌ Failed to fetch market data for {coin_symbol}")


if __name__ == "__main__":
    generate_and_plot_charts("bitcoin", timeframe="1d")

