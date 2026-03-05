import pytest
import os
from unittest.mock import patch


class TestEnvironmentConfig:
    # All required env vars are present
    def test_required_env_vars_present(self, app):
        required = [
            'SECRET_KEY',
            'JWT_SECRET_KEY',
            'MAIL_USERNAME',
            'MAIL_PASSWORD',
            'GROQ_API_KEY',
        ]
        with app.app_context():
            for var in required:
                assert app.config.get(var) or os.getenv(var), \
                    f"Missing required env var: {var}"

    # DB is reachable and tables exist
    def test_database_tables_exist(self, app, db):
        from backend.app.models import User, Coin, HistoricalData, TechnicalIndicators
        with app.app_context():
            # Will raise if table doesn't exist
            User.query.first()
            Coin.query.first()
            HistoricalData.query.first()
            TechnicalIndicators.query.first()

    # App starts in correct environment
    def test_app_is_in_testing_mode(self, app):
        assert app.config['TESTING'] is True

    # Mail is suppressed in test environment
    def test_mail_suppressed_in_tests(self, app):
        assert app.config.get('MAIL_SUPPRESS_SEND') is True

    # JWT secret is not the default fallback value
    def test_jwt_secret_is_not_default(self, app):
        jwt_secret = app.config.get('JWT_SECRET_KEY', '')
        assert jwt_secret != 'default_jwt_secret', \
            "JWT_SECRET_KEY is still set to the insecure default value"
