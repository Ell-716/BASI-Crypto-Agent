import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


def plot_price_chart(df, coin_symbol, timeframe='1M'):
    df.index = pd.to_datetime(df.index)

    # Filter Data to show only the last month
    if timeframe == "1M":
        filtered_df = df.loc[df.index >= df.index.max() - pd.Timedelta(days=30)].copy()
    else:
        filtered_df = df.copy()

    if filtered_df.empty:
        print("⚠️ Not enough data available for the selected timeframe.")
        return

    # Calculate Moving Averages
    filtered_df["SMA_9"] = filtered_df["Close"].rolling(window=9, min_periods=1).mean()
    filtered_df["SMA_21"] = filtered_df["Close"].rolling(window=21, min_periods=1).mean()

    # Define Support and Resistance Levels
    resistance_levels = [filtered_df["Close"].max() * 1.01, filtered_df["Close"].max() * 1.02]
    support_levels = [filtered_df["Close"].min() * 0.99, filtered_df["Close"].min() * 0.98]

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
    fig.patch.set_facecolor('black')

    candle_width = 0.6

    # Candlestick Chart
    for i in range(len(filtered_df)):
        date = filtered_df.index[i]
        open_price = filtered_df["Open"].iloc[i]
        close_price = filtered_df["Close"].iloc[i]
        high_price = filtered_df["High"].iloc[i]
        low_price = filtered_df["Low"].iloc[i]

        # Determine candle color (green for bullish, red for bearish)
        color = "lime" if close_price > open_price else "red"

        # Plot the candle wick (high to low)
        ax1.plot([date, date], [low_price, high_price], color=color, linewidth=0.5)

        body_height = abs(close_price - open_price)
        body_bottom = min(open_price, close_price)
        ax1.bar(date, body_height, bottom=body_bottom, color=color, width=candle_width, linewidth=0)

    # Plot Moving Averages
    ax1.plot(filtered_df.index, filtered_df["SMA_9"], label="SMA 9", color="yellow", linewidth=1.5)
    ax1.plot(filtered_df.index, filtered_df["SMA_21"], label="SMA 21", color="pink", linewidth=1.5)

    # Draw Support & Resistance Lines
    for r_level in resistance_levels:
        ax1.axhline(y=r_level, color="red", linestyle="dashed", linewidth=1.5, label="Resistance" if r_level == resistance_levels[0] else "")
    for s_level in support_levels:
        ax1.axhline(y=s_level, color="green", linestyle="dashed", linewidth=1.5, label="Support" if s_level == support_levels[0] else "")

    ax1.set_facecolor("black")
    ax1.set_title(f"{coin_symbol}/USD Trading Chart - {timeframe.upper()}", color="white", fontsize=14)
    ax1.set_ylabel("Price (USD)", color="white", fontsize=12)
    ax1.grid(color="gray", linestyle="dashed", linewidth=0.5)
    ax1.tick_params(axis="both", colors="white")
    ax1.legend(loc="upper left", facecolor="black", edgecolor="white", fontsize=10, labelcolor="white")

    # Volume Chart
    ax2.bar(filtered_df.index, filtered_df["Volume"], color=np.where(filtered_df["Close"] > filtered_df["Open"], "lime",
                                                                     "red"), alpha=0.6, label="Volume")

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

    plt.tight_layout()
    plt.show()


def plot_macd_rsi(df):

    smoothing_window = 7
    df["MACD_Line_Smooth"] = df["MACD_Line"].ewm(span=smoothing_window, adjust=False).mean()
    df["Signal_Line_Smooth"] = df["Signal_Line"].ewm(span=smoothing_window, adjust=False).mean()
    df["Stoch_K_Smooth"] = df["Stoch_K"].ewm(span=smoothing_window, adjust=False).mean()
    df["Stoch_D_Smooth"] = df["Stoch_D"].ewm(span=smoothing_window, adjust=False).mean()

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [1, 1]})
    fig.patch.set_facecolor('black')

    # MACD Chart
    ax1.plot(df.index, df["MACD_Line_Smooth"], label="MACD Line", color="deepskyblue", linewidth=1.5)
    ax1.plot(df.index, df["Signal_Line_Smooth"], label="Signal Line", color="orange", linewidth=1.5)
    ax1.bar(df.index, df["MACD_Histogram"], color=np.where(df["MACD_Histogram"] >= 0, 'lime', 'red'), alpha=0.6, label="MACD Histogram")

    ax1.set_facecolor("black")
    ax1.set_title("MACD (12, 26, 9)", color="white")
    ax1.set_ylabel("MACD", color="white")
    ax1.grid(color="gray", linestyle="dashed", linewidth=0.5)
    ax1.tick_params(axis="both", colors="white")
    ax1.legend(loc="upper left", facecolor="black", edgecolor="white", labelcolor="white")

    # Stochastic RSI Chart
    ax2.plot(df.index, df["Stoch_K_Smooth"], label="%K (Stoch RSI)", color="deepskyblue", linewidth=1.5)
    ax2.plot(df.index, df["Stoch_D_Smooth"], label="%D (Signal)", color="orange", linewidth=1.5)
    ax2.axhline(80, color="red", linestyle="dashed", linewidth=1)  # Overbought level
    ax2.axhline(20, color="green", linestyle="dashed", linewidth=1)  # Oversold level

    ax2.set_facecolor("black")
    ax2.set_title("Stochastic RSI (14, 3, 3)", color="white")
    ax2.set_ylabel("Stoch RSI", color="white")
    ax2.set_ylim(0, 100)  # Ensure scaling from 0 to 100
    ax2.grid(color="gray", linestyle="dashed", linewidth=0.5)
    ax2.tick_params(axis="both", colors="white")
    ax2.legend(loc="upper left", facecolor="black", edgecolor="white", labelcolor="white")

    # Format x-axis dates
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d'))
    plt.xticks(rotation=45, color="white")
    plt.xlabel("Date", color="white")

    plt.tight_layout()
    plt.show()


def plot_bollinger_bands(df, coin_symbol, timeframe="1M", window=20, num_std=2):
    df.index = pd.to_datetime(df.index)

    # Filter Data to show only the last month
    if timeframe == "1M":
        filtered_df = df.loc[df.index >= df.index.max() - pd.Timedelta(days=30)].copy()
    else:
        filtered_df = df.copy()

    if filtered_df.empty:
        print("⚠️ Not enough data available for the selected timeframe.")
        return

    # Calculate Bollinger Bands
    filtered_df["SMA"] = filtered_df["Close"].rolling(window=window, min_periods=1).mean()  # Middle Band
    filtered_df["StdDev"] = filtered_df["Close"].rolling(window=window, min_periods=1).std()  # Standard Deviation
    filtered_df["Upper Band"] = filtered_df["SMA"] + (num_std * filtered_df["StdDev"])  # Upper Band
    filtered_df["Lower Band"] = filtered_df["SMA"] - (num_std * filtered_df["StdDev"])  # Lower Band

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
    fig.patch.set_facecolor('black')

    # Candlestick Chart
    candle_width = 0.6  # Width of the candle bodies
    for i in range(len(filtered_df)):
        date = filtered_df.index[i]
        open_price = filtered_df["Open"].iloc[i]
        close_price = filtered_df["Close"].iloc[i]
        high_price = filtered_df["High"].iloc[i]
        low_price = filtered_df["Low"].iloc[i]

        # Determine candle color (green for bullish, red for bearish)
        color = "lime" if close_price > open_price else "red"

        # Plot the candle wick (high to low)
        ax1.plot([date, date], [low_price, high_price], color=color, linewidth=0.5)

        # Plot the candle body (open to close) using ax1.bar
        body_height = abs(close_price - open_price)
        body_bottom = min(open_price, close_price)
        ax1.bar(date, body_height, bottom=body_bottom, color=color, width=candle_width, linewidth=0)

    # Plot Bollinger Bands
    ax1.plot(filtered_df.index, filtered_df["SMA"], label="SMA (Middle Band)", color="yellow", linewidth=1.5)
    ax1.plot(filtered_df.index, filtered_df["Upper Band"], label="Upper Band", color="blue", linewidth=1.5, linestyle="--")
    ax1.plot(filtered_df.index, filtered_df["Lower Band"], label="Lower Band", color="blue", linewidth=1.5, linestyle="--")

    ax1.set_facecolor("black")
    ax1.set_title(f"{coin_symbol}/USD Trading Chart with Bollinger Bands - {timeframe.upper()}", color="white", fontsize=14)
    ax1.set_ylabel("Price (USD)", color="white", fontsize=12)
    ax1.grid(color="gray", linestyle="dashed", linewidth=0.5)
    ax1.tick_params(axis="both", colors="white")
    ax1.legend(loc="upper left", facecolor="black", edgecolor="white", fontsize=10, labelcolor="white")

    # Volume Chart
    ax2.bar(filtered_df.index, filtered_df["Volume"], color=np.where(filtered_df["Close"] > filtered_df["Open"], "lime", "red"), alpha=0.6, label="Volume")

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

    # Adjust layout and display
    plt.tight_layout()
    plt.show()
