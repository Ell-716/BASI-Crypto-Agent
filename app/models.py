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

    historical_data = db.relationship('HistoricalData', backref='user', lazy=True, cascade="all, delete-orphan")
    ai_predictions = db.relationship('AIPredictions', backref='user', lazy=True, cascade="all, delete-orphan")


class HistoricalData(db.Model):

    __tablename__ = 'historical_data'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    crypto_symbol = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    indicators = db.Column(db.Text)  # JSON data for RSI, MACD, etc. (e.g., { "RSI": 45, "MACD": -0.02 })


class AIPredictions(db.Model):

    __tablename__ = 'ai_predictions'

    id = db.Column(db.Interger, primary_key=True)
    user_id = db.Column(db.Interger, db.ForeignKey('users.id', ondelete='CASCADE'))
    crypto_symbol = db.Column(db.String(10), nullabale=False)
    prediction = db.Column(db.String(10), nullable=False)  # 'Buy' or 'Sell'
    confidence_score = db.Column(db.Float, nullabale=False)
    reasoning = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now)
