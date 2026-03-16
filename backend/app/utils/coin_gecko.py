"""
CoinGecko API integration for cryptocurrency market data.

Fetches market cap and trading volume data from CoinGecko API and stores
snapshots in the database. Implements retry logic for rate limit handling.
"""
import requests
import time
from datetime import datetime, timezone
from backend.app.models import db, Coin, CoinSnapshot
from backend.app.constants import COIN_SYMBOL_TO_ID

COINGECKO_API = "https://api.coingecko.com/api/v3/coins/markets"


def update_coin_snapshots():
    """
    Fetch and update cryptocurrency market snapshots from CoinGecko.

    Retrieves market cap and trading volume for all configured coins.
    Implements retry logic with backoff for rate limit handling (429 errors).
    Replaces all existing snapshots with fresh data on successful fetch.
    """
    try:
        ids = ",".join(COIN_SYMBOL_TO_ID.values())

        # Retry logic for rate limiting
        max_retries = 1  # 2 total attempts max
        for attempt in range(max_retries + 1):
            response = requests.get(COINGECKO_API, params={"vs_currency": "usd", "ids": ids}, timeout=10)

            if response.status_code == 429:
                if attempt < max_retries:
                    wait_time = 60  # Wait full minute before retry
                    print(f"[Snapshot] Rate limited (429), attempt {attempt + 1}/{max_retries + 1}. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"[Snapshot] Rate limited after {max_retries + 1} attempts. CoinGecko snapshots will be skipped - dashboard will show Binance data only.")
                    return

            if response.status_code != 200:
                print(f"[Snapshot] API error {response.status_code}: {response.text}")
                return

            response.raise_for_status()
            break

        data = response.json()
        now = datetime.now(timezone.utc)

        # Delete all previous entries
        db.session.query(CoinSnapshot).delete()

        for item in data:
            symbol = item["symbol"].upper()
            market_cap = item.get("market_cap")
            global_volume = item.get("total_volume")

            coin = Coin.query.filter_by(coin_symbol=symbol).first()
            if not coin:
                print(f"[Snapshot] Skipping unknown coin: {symbol}")
                continue

            snapshot = CoinSnapshot(
                coin_id=coin.id,
                market_cap=market_cap,
                global_volume=global_volume,
                timestamp=now
            )
            db.session.add(snapshot)

        db.session.commit()
        print("[Snapshot] CoinSnapshots updated successfully.")

    except Exception as e:
        print(f"[Snapshot] Failed to update CoinSnapshots: {e}")
