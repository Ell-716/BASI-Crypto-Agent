from backend.app.utils.chart_helpers import aggregate_candles
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


def plot_base_candlestick_chart(df, coin_symbol, timeframe):
    df = aggregate_candles(df, timeframe)
    if df is None or df.empty:
        print("⚠️ Not enough data available for the selected timeframe.")
        return None, None, None

    # Support & Resistance
    resistance_levels = [df["Close"].max() * 1.01, df["Close"].max() * 1.02]
    support_levels = [df["Close"].min() * 0.99, df["Close"].min() * 0.98]

    # Create chart
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True,
                                   gridspec_kw={'height_ratios': [3, 1]})
    fig.patch.set_facecolor('black')

    # Candle width
    candle_width = {
        "1h": 0.03, "1d": 0.8, "1w": 6, "1m": 20
    }.get(timeframe, 0.6)

    # Candlesticks
    for i in range(len(df)):
        date = df.index[i]
        open_price = df["Open"].iloc[i]
        close_price = df["Close"].iloc[i]
        high_price = df["High"].iloc[i]
        low_price = df["Low"].iloc[i]

        # Determine candle color (green for bullish, red for bearish)
        color = "lime" if close_price > open_price else "red"

        # Plot the candle wick (high to low)
        ax1.plot([date, date], [low_price, high_price], color=color, linewidth=0.5)

        # Plot the candle body (open to close) using ax1.bar
        body_height = abs(close_price - open_price)
        body_bottom = min(open_price, close_price)
        ax1.bar(date, body_height, bottom=body_bottom, color=color, width=candle_width, linewidth=0)

    # Draw Support & Resistance Lines
    for r in resistance_levels:
        ax1.axhline(y=r, color="red", linestyle="dashed", linewidth=1.5,
                    label="Resistance" if r == resistance_levels[0] else "")
    for s in support_levels:
        ax1.axhline(y=s, color="green", linestyle="dashed", linewidth=1.5,
                    label="Support" if s == support_levels[0] else "")

    ax1.set_facecolor("black")
    ax1.set_title(f"{coin_symbol}/USD Trading Chart - {timeframe.upper()}", color="white", fontsize=14)
    ax1.set_ylabel("Price (USD)", color="white", fontsize=12)
    ax1.grid(color="gray", linestyle="dashed", linewidth=0.5)
    ax1.tick_params(axis="both", colors="white")
    ax1.legend(loc="upper left", facecolor="black", edgecolor="white", fontsize=10, labelcolor="white")

    # Volume Chart
    ax2.bar(df.index, df["Volume"], color=np.where(df["Close"] > df["Open"], "lime", "red"),
            alpha=0.6, label="Volume", width=candle_width)

    ax2.set_facecolor("black")
    ax2.set_title("Volume", color="white", fontsize=14)
    ax2.set_ylabel("Volume", color="white", fontsize=12)
    ax2.grid(color="gray", linestyle="dashed", linewidth=0.5)
    ax2.tick_params(axis="both", colors="white")
    ax2.legend(loc="upper left", facecolor="black", edgecolor="white", fontsize=10, labelcolor="white")

    # Format x-axis dates
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d'))
    plt.xticks(rotation=45, color="white")
    plt.xlabel("Date", color="white", fontsize=12)

    return fig, ax1, ax2  # for SMA or Bollinger overlays


def plot_price_chart(df, coin_symbol, timeframe=None):
    fig, ax1, ax2 = plot_base_candlestick_chart(df, coin_symbol, timeframe)
    if fig is None:
        return

    ax1.plot(df.index, df["SMA_50"], label="SMA 50", color="yellow", linewidth=1.5)
    ax1.plot(df.index, df["SMA_200"], label="SMA 200", color="pink", linewidth=1.5)

    plt.tight_layout()
    plt.show()


def plot_bollinger_bands(df, coin_symbol, timeframe=None, window=20, num_std=2):
    fig, ax1, ax2 = plot_base_candlestick_chart(df, coin_symbol, timeframe)
    if fig is None:
        return

    # Calculate Bollinger Bands
    df["SMA"] = df["Close"].rolling(window=window, min_periods=1).mean()  # Middle Band
    df["StdDev"] = df["Close"].rolling(window=window, min_periods=1).std()  # Standard Deviation
    df["Upper Band"] = df["SMA"] + (num_std * df["StdDev"])  # Upper Band
    df["Lower Band"] = df["SMA"] - (num_std * df["StdDev"])  # Lower Band

    ax1.plot(df.index, df["SMA"], label="SMA (Middle Band)", color="yellow", linewidth=1.5)
    ax1.plot(df.index, df["Upper Band"], label="Upper Band", color="deepskyblue", linewidth=1.7, linestyle="--")
    ax1.plot(df.index, df["Lower Band"], label="Lower Band", color="deepskyblue", linewidth=1.7, linestyle="--")

    plt.tight_layout()
    plt.show()


def plot_macd_rsi(df, timeframe):
    df = aggregate_candles(df, timeframe)
    if df is None or df.empty:
        print("⚠️ Not enough data available for the selected timeframe.")
        return

    required_columns = ["MACD_Line", "Signal_Line", "MACD_Histogram", "Stoch_K", "Stoch_D"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"⚠️ Missing required columns for MACD/RSI: {missing_columns}. "
              f"Ensure `calculate_indicators(df)` was applied before plotting.")
        return

    smoothing_window = 10
    df["MACD_Line_Smooth"] = df["MACD_Line"].ewm(span=smoothing_window, adjust=False).mean()
    df["Signal_Line_Smooth"] = df["Signal_Line"].ewm(span=smoothing_window, adjust=False).mean()
    df["Stoch_K_Smooth"] = df["Stoch_K"].rolling(window=5, min_periods=1).mean().rolling(window=3, min_periods=1).mean()
    df["Stoch_D_Smooth"] = df["Stoch_D"].rolling(window=5, min_periods=1).mean().rolling(window=3, min_periods=1).mean()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True,
                                   gridspec_kw={'height_ratios': [1, 1]})
    fig.patch.set_facecolor('black')

    bar_width = {
        "1h": 0.03,
        "1d": 0.6,
        "1w": 4,
        "1m": 27,
    }.get(timeframe, 0.6)

    ax1.plot(df.index, df["MACD_Line_Smooth"], label="MACD Line", color="deepskyblue", linewidth=1.5)
    ax1.plot(df.index, df["Signal_Line_Smooth"], label="Signal Line", color="orange", linewidth=1.5)
    ax1.bar(df.index, df["MACD_Histogram"], width=bar_width,
            color=np.where(df["MACD_Histogram"] >= 0, 'lime', 'red'),
            alpha=0.6, label="MACD Histogram")

    ax1.set_facecolor("black")
    ax1.set_title("MACD (12, 26, 9)", color="white")
    ax1.set_ylabel("MACD", color="white")
    ax1.grid(color="gray", linestyle="dashed", linewidth=0.5)
    ax1.tick_params(axis="both", colors="white")
    ax1.legend(loc="upper left", facecolor="black", edgecolor="white", labelcolor="white")

    ax2.plot(df.index, df["Stoch_K_Smooth"], label="%K (Stoch RSI)", color="deepskyblue", linewidth=1.5)
    ax2.plot(df.index, df["Stoch_D_Smooth"], label="%D (Signal)", color="orange", linewidth=1.5)
    ax2.axhline(80, color="red", linestyle="dashed", linewidth=1)
    ax2.axhline(20, color="green", linestyle="dashed", linewidth=1)

    ax2.set_facecolor("black")
    ax2.set_title("Stochastic RSI (14, 3, 3)", color="white")
    ax2.set_ylabel("Stoch RSI", color="white")
    ax2.set_ylim(0, 100)
    ax2.grid(color="gray", linestyle="dashed", linewidth=0.5)
    ax2.tick_params(axis="both", colors="white")
    ax2.legend(loc="upper left", facecolor="black", edgecolor="white", labelcolor="white")

    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d'))
    plt.xticks(rotation=45, color="white")
    plt.xlabel("Date", color="white")

    plt.tight_layout()
    plt.show()
