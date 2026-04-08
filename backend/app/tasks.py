"""
Background tasks for updating historical data and technical indicators.

Provides functions to fetch cryptocurrency data from external APIs and calculate
technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, etc.) for analysis.
Implements a 60-day rolling window to manage database size.
"""
from backend.app import create_app, db
from backend.app.models import HistoricalData, TechnicalIndicators, Coin
from backend.app.utils.api import fetch_coin_data
from backend.app.constants import COINS
from datetime import datetime, timezone, timedelta
import os
import requests
import pandas as pd
import pandas_ta as ta

BINANCE_BASE_URL = os.environ.get('BINANCE_BASE_URL', 'https://api.binance.com')

# Create Flask app instance for context management
app = create_app()


def backfill_recent_klines(days=8):
    """
    Backfill missing hourly price data for the last N days using Binance klines.

    Called on cold start when historical data is stale (e.g. after Render free-tier
    sleep). Fetches recent 1h candles and inserts any hours not already in the DB,
    ensuring the 7-day sparkline always has enough data points.
    Duplicate hours are skipped via the coin_id + timestamp uniqueness check.
    """
    with app.app_context():
        limit = days * 24  # hourly candles to request

        for coin in COINS:
            binance_symbol = coin["binance_symbol"]
            clean_symbol = coin["symbol"]

            coin_obj = Coin.query.filter_by(coin_symbol=clean_symbol).first()
            if not coin_obj:
                print(f"[BackfillRecent] Coin not found in DB: {clean_symbol}, skipping")
                continue

            try:
                url = f"{BINANCE_BASE_URL}/api/v3/klines"
                params = {"symbol": binance_symbol, "interval": "1h", "limit": limit}
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                klines = response.json()
            except Exception as e:
                print(f"[BackfillRecent] Failed to fetch klines for {binance_symbol}: {e}")
                continue

            new_count = 0
            for entry in klines:
                # Store as naive UTC to match the rest of the DB
                ts = datetime.fromtimestamp(entry[0] / 1000.0, tz=timezone.utc).replace(tzinfo=None)

                existing = HistoricalData.query.filter_by(
                    coin_id=coin_obj.id, timestamp=ts
                ).first()
                if existing:
                    continue

                db.session.add(HistoricalData(
                    coin_id=coin_obj.id,
                    price=float(entry[4]),   # close price of that hourly candle
                    high=float(entry[2]),
                    low=float(entry[3]),
                    volume=float(entry[5]),
                    timestamp=ts
                ))
                new_count += 1

            db.session.commit()
            print(f"[BackfillRecent] {clean_symbol}: inserted {new_count} missing hourly candles")


def update_historical_data():
    """Fetches latest coin data from API and stores in database with 60-day rolling window."""
    with app.app_context():
        # Enforce rolling window mechanism
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=60)
        db.session.query(HistoricalData).filter(HistoricalData.timestamp < cutoff_date).delete()
        db.session.commit()

        # Fetch and Store Latest Data
        data, error = fetch_coin_data()
        if error:
            return

        for coin in data:
            coin_symbol = coin["symbol"].upper()
            coin_name = coin["name"]
            coin_image = coin.get("image", None)
            price = coin["current_price"]
            volume = coin["total_volume"]
            high = coin["high_24h"]
            low = coin["low_24h"]

            # Ensure the coin exists in the database
            coin_obj = Coin.query.filter_by(coin_symbol=coin_symbol).first()
            if not coin_obj:
                coin_obj = Coin(coin_name=coin_name, coin_symbol=coin_symbol, coin_image=coin_image)
                db.session.add(coin_obj)
                db.session.commit()

            # Round to the hour to avoid minute-level duplicates
            timestamp = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

            # Convert to naive datetime for consistent comparison with DB
            timestamp = timestamp.replace(tzinfo=None)

            # Skip if data for this coin already exists for this hour
            existing = HistoricalData.query.filter_by(coin_id=coin_obj.id, timestamp=timestamp).first()
            if existing:
                continue

            # Insert new historical price
            historical_entry = HistoricalData(
                coin_id=coin_obj.id,
                price=price,
                high=high,
                low=low,
                volume=volume,
                timestamp=timestamp
            )
            db.session.add(historical_entry)

        db.session.commit()

    # Update Indicators after updating historical data
    update_technical_indicators()


def update_technical_indicators():
    """Calculates and stores technical indicators for all coins based on historical data."""
    with app.app_context():
        # Rolling window cleanup
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=60)
        db.session.query(TechnicalIndicators).filter(TechnicalIndicators.timestamp < cutoff_date).delete()
        db.session.commit()

        coins = Coin.query.all()

        for coin in coins:
            data = HistoricalData.query.filter(
                HistoricalData.coin_id == coin.id
            ).order_by(HistoricalData.timestamp.desc()).limit(200).all()
            df = pd.DataFrame([(d.timestamp, d.price, d.volume) for d in data],
                              columns=['timestamp', 'price', 'volume'])
            df.set_index('timestamp', inplace=True)

            if df.empty:
                continue

            # Compute indicators safely with min_periods to avoid excessive NaN
            df['SMA_50'] = df['price'].rolling(window=50, min_periods=1).mean()
            df['SMA_200'] = df['price'].rolling(window=200, min_periods=1).mean()
            df['EMA_50'] = df['price'].ewm(span=50, adjust=False, min_periods=1).mean()
            df['EMA_200'] = df['price'].ewm(span=200, adjust=False, min_periods=1).mean()
            df['RSI'] = ta.rsi(df['price'], length=14)
            df['Volume_Change'] = df['volume'].diff()

            macd_values = ta.macd(df['price'])
            if macd_values is not None and isinstance(macd_values, pd.DataFrame) and not macd_values.empty:
                df['MACD'], df['MACD_Signal'] = macd_values.iloc[:, 0], macd_values.iloc[:, 1]
            else:
                df['MACD'], df['MACD_Signal'] = None, None

            # Stochastic RSI Calculation
            stoch_rsi_values = ta.stochrsi(df['price'])
            if stoch_rsi_values is not None and isinstance(stoch_rsi_values,
                                                           pd.DataFrame) and not stoch_rsi_values.empty:
                df['Stoch_RSI_K'], df['Stoch_RSI_D'] = stoch_rsi_values.iloc[:, 0], stoch_rsi_values.iloc[:, 1]
            else:
                df['Stoch_RSI_K'], df['Stoch_RSI_D'] = None, None

            bb_values = ta.bbands(df['price'])
            if bb_values is not None and isinstance(bb_values, pd.DataFrame) and not bb_values.empty:
                (
                    df["BB_upper"],
                    df["BB_middle"],
                    df["BB_lower"]
                ) = (
                    bb_values.iloc[:, 0],
                    bb_values.iloc[:, 1],
                    bb_values.iloc[:, 2]
                )
            else:
                df['BB_upper'], df['BB_middle'], df['BB_lower'] = None, None, None

            df.dropna(inplace=True)  # Remove rows with NaN values
            if df.empty:
                continue

            # Save all calculated indicators, not just the latest
            for timestamp, row in df.iterrows():
                # Check if this timestamp already exists to avoid duplicates
                existing = TechnicalIndicators.query.filter_by(
                    coin_id=coin.id,
                    timestamp=timestamp
                ).first()

                if existing:
                    continue  # Skip if already exists

                new_entry = TechnicalIndicators(
                    coin_id=coin.id,
                    SMA_50=row['SMA_50'],
                    SMA_200=row['SMA_200'],
                    EMA_50=row['EMA_50'],
                    EMA_200=row['EMA_200'],
                    RSI=row['RSI'],
                    MACD=row['MACD'],
                    MACD_Signal=row['MACD_Signal'],
                    Stoch_RSI_K=row['Stoch_RSI_K'],
                    Stoch_RSI_D=row['Stoch_RSI_D'],
                    BB_upper=row['BB_upper'],
                    BB_middle=row['BB_middle'],
                    BB_lower=row['BB_lower'],
                    Volume_Change=row['Volume_Change'],
                    timestamp=timestamp
                )
                db.session.add(new_entry)

            db.session.commit()
