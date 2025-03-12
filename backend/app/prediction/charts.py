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
