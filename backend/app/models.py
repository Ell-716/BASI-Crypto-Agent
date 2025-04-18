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
        backref=db.backref('favorited_by', lazy='dynamic'),
        lazy='dynamic'
    )

    def __repr__(self):
        return f"User {self.user_name} - {self.email}"


class Coin(db.Model):
    __tablename__ = 'coins'

    id = db.Column(db.Integer, primary_key=True)
    coin_name = db.Column(db.String(50), nullable=False)
    coin_symbol = db.Column(db.String(10), unique=True, nullable=False)
    coin_image = db.Column(db.String, nullable=True)

    # Relationship with HistoricalData & TechnicalIndicators
    historical_data = db.relationship('HistoricalData', backref='coin', lazy=True, cascade="all, delete-orphan")
    technical_indicators = db.relationship('TechnicalIndicators', backref='coin',
                                           lazy=True, cascade="all, delete-orphan")
    snapshots = db.relationship('CoinSnapshot', backref='coin', lazy=True, cascade="all, delete-orphan")
    top_volume24 = db.relationship('TopVolume24h', backref='coin', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Coin {self.coin_name} ({self.coin_symbol})"


class HistoricalData(db.Model):
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
    __tablename__ = "fear_greed_index"

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    classification = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)

    def __repr__(self):
        return f"<FearGreedIndex {self.classification} ({self.value}) at {self.timestamp}>"


class CoinSnapshot(db.Model):
    __tablename__ = "coin_snapshot"

    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.Integer, db.ForeignKey("coins.id", ondelete="CASCADE"))
    market_cap = db.Column(db.Float, nullable=True)
    global_volume = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)

    def __repr__(self):
        return f"<CoinSnapshot CoinID={self.coin_id} MarketCap={self.market_cap} Volume={self.global_volume} @ {self.timestamp}>"


class TopVolume24h(db.Model):
    __tablename__ = "top_volume_24h"

    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.Integer, db.ForeignKey("coins.id", ondelete="CASCADE"), nullable=False)
    top_volume = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)

    def __repr__(self):
        return f"<TopVolume24h CoinID={self.coin_id} Volume={self.volume} at {self.timestamp}>"