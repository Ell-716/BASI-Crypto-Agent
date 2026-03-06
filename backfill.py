import requests
import datetime
import time
import re
from backend.app import create_app, db
from backend.app.models import Coin, HistoricalData
from backend.app.tasks import update_technical_indicators
from backend.app.constants import COINS

BINANCE_URL = "https://api.binance.com/api/v3/klines"

def fetch_binance_ohlcv(symbol, interval="1h", limit=1440):
    url = f"{BINANCE_URL}?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()

def backfill_historical_data():
    app = create_app()
    with app.app_context():
        for coin in COINS:
            binance_symbol = coin["binance_symbol"]
            name = coin["name"]
            image = coin["image"]

            # Ensure coin exists
            clean_symbol = binance_symbol.replace("USDT", "")
            coin_obj = Coin.query.filter_by(coin_symbol=clean_symbol).first()
            if not coin_obj:
                coin_obj = Coin(coin_name=name, coin_symbol=clean_symbol, coin_image=image)
                db.session.add(coin_obj)
                db.session.commit()

            print(f"Fetching data for {binance_symbol}")
            try:
                ohlcv = fetch_binance_ohlcv(binance_symbol)
            except Exception as e:
                print(f"Failed to fetch {binance_symbol}: {e}")
                continue

            for entry in ohlcv:
                ts = datetime.datetime.fromtimestamp(entry[0] / 1000.0, tz=datetime.timezone.utc)
                exists = HistoricalData.query.filter_by(coin_id=coin_obj.id, timestamp=ts).first()
                if exists:
                    continue
                hd = HistoricalData(
                    coin_id=coin_obj.id,
                    price=float(entry[4]),
                    high=float(entry[2]),
                    low=float(entry[3]),
                    volume=float(entry[5]),
                    timestamp=ts
                )
                db.session.add(hd)

            db.session.commit()
            time.sleep(1)

        print("Updating technical indicators...")
        update_technical_indicators()
        print("Backfill complete.")


def strip_html(text):
    """Remove HTML tags from CoinGecko description text."""
    clean = re.sub(r'<[^>]+>', '', text)
    # Collapse multiple spaces/newlines
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def seed_descriptions():
    """
    Fetch coin descriptions from CoinGecko and save to DB.
    Run once after backfill_historical_data().
    Safe to re-run — only updates coins with missing descriptions.
    """
    app = create_app()
    with app.app_context():
        for coin_data in COINS:
            coin_obj = Coin.query.filter_by(coin_symbol=coin_data["symbol"]).first()
            if not coin_obj:
                print(f"[Descriptions] Coin not found in DB: {coin_data['symbol']} — run backfill first")
                continue

            # Skip if description already exists
            if coin_obj.description:
                print(f"[Descriptions] {coin_data['symbol']} already has a description, skipping")
                continue

            try:
                url = f"https://api.coingecko.com/api/v3/coins/{coin_data['coingecko_id']}"
                res = requests.get(url, params={"localization": "false"}, timeout=10)
                res.raise_for_status()
                data = res.json()

                raw_description = data.get("description", {}).get("en", "")
                if not raw_description:
                    print(f"[Descriptions] No description found for {coin_data['symbol']}")
                    continue

                coin_obj.description = strip_html(raw_description)
                db.session.commit()
                print(f"[Descriptions] ✅ Saved description for {coin_data['symbol']}")

                # CoinGecko free tier allows ~30 req/min — be polite
                time.sleep(2)

            except Exception as e:
                print(f"[Descriptions] Failed for {coin_data['symbol']}: {e}")
                continue

        print("[Descriptions] Done.")


if __name__ == "__main__":
    print("=== Step 1: Backfilling historical data ===")
    backfill_historical_data()
    print("\n=== Step 2: Seeding coin descriptions ===")
    seed_descriptions()
    print("\n✅ All done. You can now start the app.")
