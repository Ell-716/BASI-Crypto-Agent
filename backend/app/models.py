from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# User Model
class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)
    preferences = db.Column(db.Text, nullable=True)  # JSON data (e.g., { "favorite_crypto": "BTC", "alert_threshold": "10%" })

    # Relationship with AIPredictions
    ai_predictions = db.relationship('AIPredictions', backref='user', lazy=True, cascade="all, delete-orphan")


class HistoricalData(db.Model):

    __tablename__ = 'historical_data'

    id = db.Column(db.Integer, primary_key=True)
    coin = db.Column(db.String(10), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Current price
    high_24h = db.Column(db.Float, nullable=True)  # Highest price in the last 24 hours
    low_24h = db.Column(db.Float, nullable=True)  # Lowest price in the last 24 hours
    volume_24h = db.Column(db.Float, nullable=False)  # Trading volume in the last 24 hours
    market_cap = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    indicators = db.Column(db.Text)  # JSON data for technical indicators (e.g., { "RSI": 45, "MACD": -0.02 })

    # Relationship with AIPredictions
    ai_predictions = db.relationship('AIPredictions', backref='historical_data',
                                     lazy=True, cascade="all, delete-orphan")


class AIPredictions(db.Model):

    __tablename__ = 'ai_predictions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    historical_data_id = db.Column(db.Integer, db.ForeignKey('historical_data.id', ondelete="CASCADE"), nullable=False)
    coin = db.Column(db.String(10), nullable=False)
    prediction = db.Column(db.String(10), nullable=False)  # 'Buy' or 'Sell'
    confidence_score = db.Column(db.Float, nullable=False)  # Confidence score (e.g., 0.75 for 75%)
    reasoning = db.Column(db.Text)  # Reasoning behind the prediction
    timestamp = db.Column(db.DateTime, default=datetime.now)
