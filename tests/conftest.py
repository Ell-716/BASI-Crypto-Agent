import pytest
from unittest.mock import patch, MagicMock
from backend.app import create_app
from backend.app.models import db as _db, User, Coin

@pytest.fixture(scope='session')
def app():
    """Create application with test config — in-memory SQLite, no real mail or Groq."""
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_ACCESS_TOKEN_EXPIRES': False,  # disable expiry in tests
        'MAIL_SUPPRESS_SEND': True,         # suppress all emails
        'WTF_CSRF_ENABLED': False,
    })
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture(scope='function')
def db(app):
    """Provide a clean DB for each test — rolls back after each one."""
    with app.app_context():
        yield _db
        _db.session.rollback()
        # Clean all tables between tests
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture
def verified_user(db, app):
    """A fully verified user ready to log in."""
    from flask_bcrypt import Bcrypt
    bcrypt = Bcrypt()
    with app.app_context():
        user = User(
            email='test@example.com',
            user_name='testuser',
            password_hash=bcrypt.generate_password_hash('Test@1234').decode('utf-8'),
            is_verified=True
        )
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def unverified_user(db, app):
    """A registered but unverified user."""
    from flask_bcrypt import Bcrypt
    bcrypt = Bcrypt()
    with app.app_context():
        user = User(
            email='unverified@example.com',
            user_name='unverifieduser',
            password_hash=bcrypt.generate_password_hash('Test@1234').decode('utf-8'),
            is_verified=False
        )
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def auth_headers(client, verified_user):
    """JWT headers for an authenticated request."""
    res = client.post('/users/login', json={
        'email': 'test@example.com',
        'password': 'Test@1234'
    })
    token = res.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def sample_coin(db, app):
    """A coin with no historical data — just metadata."""
    with app.app_context():
        coin = Coin(
            coin_name='Bitcoin',
            coin_symbol='BTC',
            coin_image='https://example.com/btc.png',
            description='The original cryptocurrency.'
        )
        db.session.add(coin)
        db.session.commit()
        return coin
