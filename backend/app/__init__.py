from flask import Flask
from flask_jwt_extended import JWTManager
from backend.config import config
from backend.app.models import db
from backend.app.routes.users import users_bp
from backend.app.routes.coins import coins_bp


jwt = JWTManager()


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():  # Run once to create the db tables
        db.create_all()

    # Register Blueprints
    app.register_blueprint(users_bp)
    app.register_blueprint(coins_bp)

    return app
