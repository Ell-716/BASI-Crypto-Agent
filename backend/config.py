"""
Application configuration module.

Defines configuration classes for different environments (development, testing, production).
Loads environment variables and sets up Flask, JWT, and database configuration.
"""
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Base configuration class with common settings for all environments.

    Attributes:
        SECRET_KEY: Flask secret key for session security
        JWT_SECRET_KEY: Secret key for JWT token signing
        JWT_ACCESS_TOKEN_EXPIRES: Access token expiration time (1 hour)
        JWT_REFRESH_TOKEN_EXPIRES: Refresh token expiration time (30 days)
        SQLALCHEMY_TRACK_MODIFICATIONS: Disable SQLAlchemy modification tracking
        RESEND_API_KEY: API key for Resend email service
        BACKEND_URL: Backend server URL
        FRONTEND_URL: Frontend application URL
        BINANCE_BASE_URL: Binance API base URL
    """
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
        """Initialize application-specific configuration."""
        pass


class DevelopmentConfig(Config):
    """Development environment configuration with debug mode enabled."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///crypto_agent_dev.db')


class TestingConfig(Config):
    """Testing environment configuration with rate limiting disabled."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///crypto_agent_test.db')
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production environment configuration."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///crypto_agent.db')


# Dictionary to map environment names to configuration classes
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
