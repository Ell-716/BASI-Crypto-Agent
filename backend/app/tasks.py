from backend.app import create_app, db
from backend.app.models import HistoricalData, TechnicalIndicators, Coin
from backend.app.utils.api import fetch_coin_data
from datetime import datetime, timezone, timedelta
import pandas as pd
import pandas_ta as ta

# Create Flask app instance for context management
app = create_app()


def update_historical_data():
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

            # Compute indicators safely
            df['SMA_50'] = ta.sma(df['price'], length=50)
            df['SMA_200'] = ta.sma(df['price'], length=200)
            df['EMA_50'] = ta.ema(df['price'], length=50)
            df['EMA_200'] = ta.ema(df['price'], length=200)
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

            latest_entry = df.iloc[-1]

            new_entry = TechnicalIndicators(
                coin_id=coin.id,
                SMA_50=latest_entry['SMA_50'],
                SMA_200=latest_entry['SMA_200'],
                EMA_50=latest_entry['EMA_50'],
                EMA_200=latest_entry['EMA_200'],
                RSI=latest_entry['RSI'],
                MACD=latest_entry['MACD'],
                MACD_Signal=latest_entry['MACD_Signal'],
                Stoch_RSI_K=latest_entry['Stoch_RSI_K'],
                Stoch_RSI_D=latest_entry['Stoch_RSI_D'],
                BB_upper=latest_entry['BB_upper'],
                BB_middle=latest_entry['BB_middle'],
                BB_lower=latest_entry['BB_lower'],
                Volume_Change=latest_entry['Volume_Change'],
                timestamp=latest_entry.name
            )
            db.session.add(new_entry)

            db.session.commit()
