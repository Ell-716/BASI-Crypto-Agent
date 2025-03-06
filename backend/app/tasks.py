from backend.app import create_app, db
from backend.app.models import HistoricalData, TechnicalIndicators, Coin
from backend.app.api import fetch_coin_data
from datetime import datetime, timezone, timedelta
import pandas as pd
import pandas_ta as ta


# Create Flask app instance for context management
app = create_app()


def update_historical_data():
    with app.app_context():
        # Enforce Rolling Window (Delete Oldest Data)
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
            market_cap = coin["market_cap"]

            # Ensure the coin exists in the database
            coin_obj = Coin.query.filter_by(coin_symbol=coin_symbol).first()
            if not coin_obj:
                coin_obj = Coin(coin_name=coin_name, coin_symbol=coin_symbol, coin_image=coin_image)
                db.session.add(coin_obj)
                db.session.commit()

            # Insert new historical price
            timestamp = datetime.now(timezone.utc)
            historical_entry = HistoricalData(
                coin_id=coin_obj.id,
                price=price,
                high=high,
                low=low,
                volume=volume,
                market_cap=market_cap,
                timestamp=timestamp
            )
            db.session.add(historical_entry)
        db.session.commit()

    # Update Indicators after updating historical data
    update_technical_indicators()


def update_technical_indicators():
    with app.app_context():
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

            # MACD Calculation
            macd_values = ta.macd(df['price'])
            if macd_values is not None and macd_values.shape[1] >= 2:
                df['MACD'], df['MACD_Signal'] = macd_values.iloc[:, 0], macd_values.iloc[:, 1]
            else:
                df['MACD'], df['MACD_Signal'] = None, None

            stoch_rsi_values = ta.stochrsi(df['price'])

            # Check if the result is None before proceeding
            if stoch_rsi_values is None or isinstance(stoch_rsi_values, pd.DataFrame) and stoch_rsi_values.empty:
                df['Stoch_RSI_K'], df['Stoch_RSI_D'] = None, None
            else:
                # Ensure at least two columns exist (`%K` and `%D`)
                stoch_rsi_values = stoch_rsi_values.dropna()
                if isinstance(stoch_rsi_values, pd.DataFrame) and stoch_rsi_values.shape[1] >= 2:
                    df['Stoch_RSI_K'], df['Stoch_RSI_D'] = stoch_rsi_values.iloc[:, 0], stoch_rsi_values.iloc[:, 1]
                else:
                    df['Stoch_RSI_K'], df['Stoch_RSI_D'] = None, None

            # Bollinger Bands Calculation
            bb_values = ta.bbands(df['price'])
            if isinstance(bb_values, pd.DataFrame) and bb_values.shape[1] >= 3:
                df['BB_upper'], df['BB_middle'], df['BB_lower'] = bb_values.iloc[:, 0], bb_values.iloc[:, 1], bb_values.iloc[:, 2]
            else:
                df['BB_upper'], df['BB_middle'], df['BB_lower'] = None, None, None

            df.dropna(inplace=True)  # Remove rows with NaN values

            if df.empty:
                continue

            # Store in database (overwrite latest indicators)
            latest_entry = df.iloc[-1]
            existing_entry = TechnicalIndicators.query.filter_by(coin_id=coin.id).first()
            if existing_entry:
                existing_entry.SMA_50 = latest_entry['SMA_50']
                existing_entry.SMA_200 = latest_entry['SMA_200']
                existing_entry.EMA_50 = latest_entry['EMA_50']
                existing_entry.EMA_200 = latest_entry['EMA_200']
                existing_entry.RSI = latest_entry['RSI']
                existing_entry.MACD = latest_entry['MACD']
                existing_entry.MACD_Signal = latest_entry['MACD_Signal']
                existing_entry.Stoch_RSI_K = latest_entry['Stoch_RSI_K']
                existing_entry.Stoch_RSI_D = latest_entry['Stoch_RSI_D']
                existing_entry.BB_upper = latest_entry['BB_upper']
                existing_entry.BB_middle = latest_entry['BB_middle']
                existing_entry.BB_lower = latest_entry['BB_lower']
                existing_entry.Volume_Change = latest_entry['Volume_Change']

            else:
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
                    Volume_Change=latest_entry['Volume_Change']
                )
                db.session.add(new_entry)

            db.session.commit()
