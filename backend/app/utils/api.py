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


def fetch_coin_data(coin_id=None):
    coins = []
    errors = []

    for coin in TOP_10_BINANCE_COINS:
        if coin_id and coin_id.lower() not in coin["name"].lower():
            continue

        symbol = coin["symbol"]
        clean_symbol = symbol.replace("USDT", "")

        # Fetch Binance data
        try:
            res = requests.get(
                f"{BINANCE_BASE_URL}/api/v3/ticker/24hr",
                params={"symbol": symbol},
                timeout=10
            )
            if res.status_code != 200:
                error_msg = f"Binance API error {res.status_code} for {symbol}"
                print(f"[API] {error_msg}")
                errors.append(error_msg)
                continue  # Skip this coin but continue with others
            data = res.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error for {symbol}: {str(e)}"
            print(f"[API] {error_msg}")
            errors.append(error_msg)
            continue  # Skip this coin but continue with others
        except (ValueError, KeyError) as e:
            error_msg = f"Invalid response for {symbol}: {e}"
            print(f"[API] {error_msg}")
            errors.append(error_msg)
            continue  # Skip this coin but continue with others

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
            "current_price": float(data.get("lastPrice", 0)),
            "high_24h": float(data.get("highPrice", 0)),
            "low_24h": float(data.get("lowPrice", 0)),
            "total_volume": float(data.get("volume", 0)),
            "global_volume": snapshot.global_volume if snapshot else None,
            "market_cap": snapshot.market_cap if snapshot else None
        })

    # Return what we have, even if some coins failed
    if not coins and errors:
        return [], f"All coins failed: {'; '.join(errors[:3])}"

    return coins, None
