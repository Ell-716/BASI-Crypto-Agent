import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Common configuration settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RESEND_API_KEY = os.getenv('RESEND_API_KEY')
    BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5050')
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    BINANCE_BASE_URL = os.getenv('BINANCE_BASE_URL', 'https://api.binance.com')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///crypto_agent_dev.db')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///crypto_agent_test.db')
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///crypto_agent.db')


# Dictionary to map environment names to configuration classes
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
