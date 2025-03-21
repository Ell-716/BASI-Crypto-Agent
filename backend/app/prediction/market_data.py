import requests
import pandas as pd
from backend.app.prediction.charts import plot_price_chart, plot_macd_rsi, plot_bollinger_bands, aggregate_candles

BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"


def fetch_market_data(symbol, interval, limit=1000):

    params = {
        "symbol": f"{symbol.upper()}USDT",
        "interval": interval,  # "1h", "1d", "1w", "1M"
        "limit": limit  # Max candles
    }
    try:
        response = requests.get(BINANCE_KLINES_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        df = pd.DataFrame(data, columns=[
            "timestamp", "Open", "High", "Low", "Close", "Volume",
            "CloseTime", "QuoteAssetVolume", "Trades", "TakerBuyBase", "TakerBuyQuote", "Ignore"
        ])
        df["Date"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
        df.set_index("Date", inplace=True)
        df = df.astype(float)
        return df
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error fetching Binance data: {e}")
        return None


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
    market_data = fetch_market_data(coin_symbol, timeframe)

    if market_data is not None:
        # Aggregate OHLCV data for selected timeframe
        df_resampled = aggregate_candles(market_data, timeframe)

        # If resampling failed, skip plotting
        if df_resampled is None or df_resampled.empty:
            print(f"⚠️ Not enough data for {coin_symbol} ({timeframe}).")
            return

        # Calculate indicators for resampled data
        df_with_indicators = calculate_indicators(df_resampled)

        # Plot all charts
        plot_price_chart(df_resampled, coin_symbol, timeframe)
        plot_bollinger_bands(df_resampled, coin_symbol, timeframe)
        plot_macd_rsi(df_with_indicators, timeframe)  # Now correctly computed
    else:
        print(f"⚠️ Failed to fetch market data for {coin_symbol}")


if __name__ == "__main__":
    generate_and_plot_charts("bitcoin", timeframe="1d")

