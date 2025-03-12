import numpy as np
import requests

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
    