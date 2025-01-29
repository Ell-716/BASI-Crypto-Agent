from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)  # Use DevelopmentConfig directly

    db.init_app(app)

    with app.app_context():  # Run once to create the db tables
        db.create_all()

    return app