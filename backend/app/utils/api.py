import requests
import time
from backend.app.models import Coin, CoinSnapshot
from backend.app.utils.coin_gecko import COINGECKO_API
from backend.app.constants import TOP_10_BINANCE_COINS, COIN_SYMBOL_TO_ID

# Cache for CoinGecko market data
_coingecko_cache = {
    "data": None,
    "timestamp": 0
}

# Cache for Binance ticker data
_binance_cache = {
    "data": None,
    "timestamp": 0
}

BINANCE_BASE_URL = "https://data.binance.com"


def get_cached_coingecko_data():
    now = time.time()
    if _coingecko_cache["data"] and now - _coingecko_cache["timestamp"] < 60:
        return _coingecko_cache["data"]

    try:
        ids = ",".join(COIN_SYMBOL_TO_ID.values())
        res = requests.get(COINGECKO_API, params={"vs_currency": "usd", "ids": ids}, timeout=10)
        res.raise_for_status()
        data = res.json()
        _coingecko_cache["data"] = data
        _coingecko_cache["timestamp"] = now
        return data
    except Exception as e:
        print(f"[CoinGecko] Error fetching market data: {e}")
        return []


def get_cached_binance_tickers():
    """Fetch all Binance tickers with caching to avoid rate limits"""
    now = time.time()
    # Cache for 60 seconds to reduce API calls
    if _binance_cache["data"] and now - _binance_cache["timestamp"] < 60:
        return _binance_cache["data"]

    try:
        # Single API call to get ALL tickers at once
        res = requests.get(f"{BINANCE_BASE_URL}/api/v3/ticker/24hr", timeout=10)
        if res.status_code != 200:
            print(f"[Binance] API error {res.status_code}: {res.text}")
            return []

        data = res.json()
        _binance_cache["data"] = data
        _binance_cache["timestamp"] = now
        print(f"[Binance] Cached {len(data)} tickers")
        return data
    except Exception as e:
        print(f"[Binance] Error fetching tickers: {e}")
        return []


def fetch_coin_data(coin_id=None):
    coins = []

    # Get all tickers at once (cached)
    all_tickers = get_cached_binance_tickers()
    if not all_tickers:
        return [], "Failed to fetch Binance tickers"

    # Build a lookup map for fast access
    ticker_map = {ticker["symbol"]: ticker for ticker in all_tickers}

    for coin in TOP_10_BINANCE_COINS:
        if coin_id and coin_id.lower() not in coin["name"].lower():
            continue

        symbol = coin["symbol"]
        clean_symbol = symbol.replace("USDT", "")

        # Get ticker data from cached response
        ticker_data = ticker_map.get(symbol)
        if not ticker_data:
            print(f"[API] No ticker data for {symbol}")
            continue

        # Fetch snapshot from DB
        coin_obj = Coin.query.filter_by(coin_symbol=clean_symbol).first()
        snapshot = None
        if coin_obj:
            snapshot = (
                CoinSnapshot.query
                .filter_by(coin_id=coin_obj.id)
                .order_by(CoinSnapshot.timestamp.desc())
                .first()
            )

        coins.append({
            "symbol": clean_symbol,
            "name": coin["name"],
            "image": coin["image"],
            "current_price": float(ticker_data.get("lastPrice", 0)),
            "high_24h": float(ticker_data.get("highPrice", 0)),
            "low_24h": float(ticker_data.get("lowPrice", 0)),
            "total_volume": float(ticker_data.get("volume", 0)),
            "global_volume": snapshot.global_volume if snapshot else None,
            "market_cap": snapshot.market_cap if snapshot else None
        })

    return coins, None
