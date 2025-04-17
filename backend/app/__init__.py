from flask import Flask
import os
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
from backend.config import config
from backend.app.models import db
from backend.app.routes.users import users_bp
from backend.app.routes.coins import coins_bp
from backend.app.routes.predictions import predictions_bp
from backend.app.routes.dashboard_routes import dashboard_bp
from backend.app.utils.socket_tasks import start_coin_stream
from backend.app.routes.chart_routes import chart_bp


socketio = SocketIO(cors_allowed_origins="*", async_mode="gevent")
jwt = JWTManager()


def create_app(config_name='development'):
    app = Flask(
        __name__,
        instance_path=os.path.join(os.path.dirname(__file__), '..', 'instance'),
        instance_relative_config=True
    )
    app.config.from_object(config[config_name])
    CORS(app)

    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)
    start_coin_stream(socketio, app)

    #with app.app_context():  # Run once to create the db tables
        #db.create_all()

    # Register Blueprints
    app.register_blueprint(users_bp)
    app.register_blueprint(coins_bp)
    app.register_blueprint(predictions_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(chart_bp)

    return app
