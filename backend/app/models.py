"""
Database models for the cryptocurrency tracking application.

Defines SQLAlchemy ORM models for users, coins, historical data, technical indicators,
market snapshots, and fear & greed index data.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Join Table for Favorite Coins
user_favorite_coins = db.Table(
    'user_favorite_coins',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    db.Column('coin_id', db.Integer, db.ForeignKey('coins.id', ondelete="CASCADE"), primary_key=True)
)


class User(db.Model):
    """
    User model for authentication and favorites tracking.

    Attributes:
        id: Primary key
        email: Unique user email address
        password_hash: Hashed password for authentication
        user_name: Unique username
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        is_verified: Email verification status
        favorite_coins: Many-to-many relationship with Coin model
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)
    is_verified = db.Column(db.Boolean, default=False)

    # Many-to-Many Relationship with Coin (Favorites)
    favorite_coins = db.relationship(
        'Coin',
        secondary=user_favorite_coins,
        backref=db.backref('favorited_by')
    )

    def __repr__(self):
        return f"User {self.user_name} - {self.email}"


class Coin(db.Model):
    """
    Cryptocurrency model.

    Attributes:
        id: Primary key
        coin_name: Full name of the cryptocurrency
        coin_symbol: Trading symbol (e.g., BTC, ETH)
        coin_image: URL to coin image/logo
        description: Detailed description of the cryptocurrency
        historical_data: One-to-many relationship with HistoricalData
        technical_indicators: One-to-many relationship with TechnicalIndicators
        snapshots: One-to-many relationship with CoinSnapshot
        top_volume24: One-to-many relationship with TopVolume24h
    """
    __tablename__ = 'coins'

    id = db.Column(db.Integer, primary_key=True)
    coin_name = db.Column(db.String(50), nullable=False)
    coin_symbol = db.Column(db.String(10), unique=True, nullable=False)
    coin_image = db.Column(db.String, nullable=True)
    description = db.Column(db.Text, nullable=True)

    # Relationship with HistoricalData & TechnicalIndicators
    historical_data = db.relationship('HistoricalData', backref='coin', lazy=True, cascade="all, delete-orphan")
    technical_indicators = db.relationship('TechnicalIndicators', backref='coin',
                                           lazy=True, cascade="all, delete-orphan")
    snapshots = db.relationship('CoinSnapshot', backref='coin', lazy=True, cascade="all, delete-orphan")
    top_volume24 = db.relationship('TopVolume24h', backref='coin', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Coin {self.coin_name} ({self.coin_symbol})"


class HistoricalData(db.Model):
    """
    Historical price and volume data for cryptocurrencies.

    Attributes:
        id: Primary key
        coin_id: Foreign key to Coin model
        price: Closing price
        high: Highest price in the period
        low: Lowest price in the period
        volume: Trading volume
        timestamp: Data timestamp
    """
    __tablename__ = 'historical_data'

    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.Integer, db.ForeignKey('coins.id', ondelete="CASCADE"), nullable=False)
    price = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=True)
    low = db.Column(db.Float, nullable=True)
    volume = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"HistoricalData CoinID={self.coin_id} Timestamp={self.timestamp}"


class TechnicalIndicators(db.Model):
    """
    Technical analysis indicators for cryptocurrency price action.

    Attributes:
        id: Primary key
        coin_id: Foreign key to Coin model
        SMA_50: 50-period Simple Moving Average
        SMA_200: 200-period Simple Moving Average
        EMA_50: 50-period Exponential Moving Average
        EMA_200: 200-period Exponential Moving Average
        RSI: Relative Strength Index
        Stoch_RSI_K: Stochastic RSI %K line
        Stoch_RSI_D: Stochastic RSI %D line
        MACD: Moving Average Convergence Divergence
        MACD_Signal: MACD signal line
        Volume_Change: Volume change percentage
        BB_upper: Bollinger Bands upper line
        BB_middle: Bollinger Bands middle line
        BB_lower: Bollinger Bands lower line
        timestamp: Indicator calculation timestamp
    """
    __tablename__ = 'technical_indicators'

    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.Integer, db.ForeignKey('coins.id', ondelete="CASCADE"), nullable=False)
    SMA_50 = db.Column(db.Float, nullable=False)
    SMA_200 = db.Column(db.Float, nullable=False)
    EMA_50 = db.Column(db.Float, nullable=False)
    EMA_200 = db.Column(db.Float, nullable=False)
    RSI = db.Column(db.Float, nullable=False)
    Stoch_RSI_K = db.Column(db.Float, nullable=True)  # %K
    Stoch_RSI_D = db.Column(db.Float, nullable=True)  # %D
    MACD = db.Column(db.Float, nullable=False)
    MACD_Signal = db.Column(db.Float, nullable=False)
    Volume_Change = db.Column(db.Float, nullable=False)
    BB_upper = db.Column(db.Float, nullable=True)
    BB_middle = db.Column(db.Float, nullable=True)
    BB_lower = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"TechnicalIndicators CoinID={self.coin_id} Timestamp={self.timestamp}"


class FearGreedIndex(db.Model):
    """
    Crypto Fear & Greed Index data.

    Attributes:
        id: Primary key
        value: Index value (0-100)
        classification: Human-readable classification (e.g., Extreme Fear, Greed)
        timestamp: Index data timestamp
    """
    __tablename__ = "fear_greed_index"

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    classification = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)

    def __repr__(self):
        return f"<FearGreedIndex {self.classification} ({self.value}) at {self.timestamp}>"


class CoinSnapshot(db.Model):
    """
    Daily snapshot of cryptocurrency market cap and volume data.

    Attributes:
        id: Primary key
        coin_id: Foreign key to Coin model
        market_cap: Total market capitalization
        global_volume: Total 24h trading volume
        timestamp: Snapshot timestamp
    """
    __tablename__ = "coin_snapshot"

    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.Integer, db.ForeignKey("coins.id", ondelete="CASCADE"))
    market_cap = db.Column(db.Float, nullable=True)
    global_volume = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)

    def __repr__(self):
        return f"<CoinSnapshot CoinID={self.coin_id} MarketCap={self.market_cap} Volume={self.global_volume} @ {self.timestamp}>"


class TopVolume24h(db.Model):
    """
    Tracks the cryptocurrency with highest 24h trading volume.

    Attributes:
        id: Primary key
        coin_id: Foreign key to Coin model
        top_volume: 24h trading volume in quote currency
        timestamp: Record timestamp
    """
    __tablename__ = "top_volume_24h"

    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.Integer, db.ForeignKey("coins.id", ondelete="CASCADE"), nullable=False)
    top_volume = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)

    def __repr__(self):
        return f"<TopVolume24h CoinID={self.coin_id} Volume={self.volume} at {self.timestamp}>"