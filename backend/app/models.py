from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Join Table for Favorite Coins
user_favorite_coins = db.Table(
    'user_favorite_coins',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('coin_id', db.Integer, db.ForeignKey('coins.id'), primary_key=True)
)


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

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

    # Relationship with HistoricalData & AIPredictions
    historical_data = db.relationship('HistoricalData', backref='coin', lazy=True)
    predictions = db.relationship('AIPredictions', backref='coin', lazy=True)

    def __repr__(self):
        return f"Coin {self.coin_name} ({self.coin_symbol})"


class HistoricalData(db.Model):
    __tablename__ = 'historical_data'

    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.Integer, db.ForeignKey('coins.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=True)
    low = db.Column(db.Float, nullable=True)
    volume = db.Column(db.Float, nullable=False)
    market_cap = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    indicators = db.Column(db.Text)  # JSON format for indicators (e.g., "{'RSI': 45, 'MACD': -0.02}")

    def __repr__(self):
        return f"HistoricalData CoinID={self.coin_id} Timestamp={self.timestamp}"


class AIPredictions(db.Model):
    __tablename__ = 'ai_predictions'

    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.Integer, db.ForeignKey('coins.id'), nullable=False)
    prediction = db.Column(db.String(10), nullable=False)  # 'Buy' or 'Sell'
    confidence_score = db.Column(db.Float, nullable=False)  # Confidence score (e.g., 0.75 for 75%)
    reasoning = db.Column(db.Text)  # Reasoning behind the prediction
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"AIPredictions CoinID={self.coin_id} Prediction={self.prediction} Confidence={self.confidence_score}"
