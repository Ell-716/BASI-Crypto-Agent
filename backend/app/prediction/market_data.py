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


def fetch_market_data(coin_symbol):
    """Fetch real-time market data."""
    data, error = fetch_coin_data(coin_symbol)
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
    return df
    