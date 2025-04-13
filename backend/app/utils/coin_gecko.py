import requests
from datetime import datetime, timezone
from backend.app.models import db, Coin, CoinSnapshot

COINGECKO_API = "https://api.coingecko.com/api/v3/coins/markets"
COIN_SYMBOL_TO_ID = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BNB": "binancecoin",
    "SOL": "solana",
    "XRP": "ripple",
    "ADA": "cardano",
    "AVAX": "avalanche-2",
    "DOGE": "dogecoin",
    "DOT": "polkadot",
    "LINK": "chainlink"
}


def update_coin_snapshots():
    try:
        ids = ",".join(COIN_SYMBOL_TO_ID.values())
        response = requests.get(COINGECKO_API, params={"vs_currency": "usd", "ids": ids}, timeout=10)
        response.raise_for_status()
        data = response.json()
        now = datetime.now(timezone.utc)

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
