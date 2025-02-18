from backend.app import db
from backend.app.models import HistoricalData, TechnicalIndicators, Coin
from backend.app.api import fetch_coin_data
from datetime import datetime, timezone
import pandas as pd
import pandas_ta as ta
from celery import Celery


# Celery Configuration
celery = Celery('tasks', broker='redis://localhost:6379/0')


@celery.task
def update_historical_data():
    coins = Coin.query.all()
    for coin in coins:
        data, error = fetch_coin_data(coin.coin_symbol)
        if data:
            for entry in data['prices']:
                timestamp = datetime.fromtimestamp(entry[0] / 1000, timezone.utc)
                price = entry[1]
                historical_entry = HistoricalData.query.filter_by(coin_id=coin.id, timestamp=timestamp).first()
                if not historical_entry:
                    new_data = HistoricalData(
                        coin_id=coin.id,
                        price=price,
                        timestamp=timestamp
                    )
                    db.session.add(new_data)
            db.session.commit()
    update_technical_indicators()


@celery.task
def update_technical_indicators():
    """Recalculate and update technical indicators for all coins."""
    coins = Coin.query.all()
    for coin in coins:
        data = HistoricalData.query.filter(
            HistoricalData.coin_id == coin.id).order_by(HistoricalData.timestamp.desc()).limit(50).all()
        if data:
            df = pd.DataFrame([(d.timestamp, d.price) for d in data], columns=['timestamp', 'price'])
            df.set_index('timestamp', inplace=True)

            # Compute indicators
            df['SMA_50'] = ta.sma(df['price'], length=50)
            df['SMA_200'] = ta.sma(df['price'], length=200)
            df['EMA_50'] = ta.ema(df['price'], length=50)
            df['EMA_200'] = ta.ema(df['price'], length=200)
            df['RSI'] = ta.rsi(df['price'], length=14)
            df['MACD'], df['MACD_Signal'], _ = ta.macd(df['price'])
            df['Stoch_RSI'] = ta.stochrsi(df['price'])
            df['BB_upper'], df['BB_middle'], df['BB_lower'] = ta.bbands(df['price']).T.values
            df.dropna(inplace=True)

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
                existing_entry.Stoch_RSI = latest_entry['Stoch_RSI']
                existing_entry.BB_upper = latest_entry['BB_upper']
                existing_entry.BB_middle = latest_entry['BB_middle']
                existing_entry.BB_lower = latest_entry['BB_lower']
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
                    Stoch_RSI=latest_entry['Stoch_RSI'],
                    BB_upper=latest_entry['BB_upper'],
                    BB_middle=latest_entry['BB_middle'],
                    BB_lower=latest_entry['BB_lower']
                )
                db.session.add(new_entry)
            db.session.commit()
