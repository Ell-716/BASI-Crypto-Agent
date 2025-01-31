from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from backend.config import config

db = SQLAlchemy()


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    with app.app_context():  # Run once to create the db tables
        db.create_all()

    return app