import pytest
from unittest.mock import patch
from backend.app.models import User
from backend.app.utils.email_verification import generate_verification_token


class TestRegister:
    # Happy path — valid data creates user and returns 201
    def test_register_success(self, client):
        with patch('backend.app.routes.users.send_verification_email'):
            res = client.post('/users/add_user', json={
                'email': 'new@example.com',
                'user_name': 'newuser',
                'password': 'Test@1234'
            })
        assert res.status_code == 201
        assert 'Registration successful' in res.get_json()['message']

    # Missing fields returns 400
    def test_register_missing_fields(self, client):
        res = client.post('/users/add_user', json={'email': 'a@b.com'})
        assert res.status_code == 400

    # Weak password returns 400
    def test_register_weak_password(self, client):
        res = client.post('/users/add_user', json={
            'email': 'a@b.com',
            'user_name': 'someuser',
            'password': 'weak'
        })
        assert res.status_code == 400

    # Duplicate email returns 400
    def test_register_duplicate_email(self, client, verified_user):
        with patch('backend.app.routes.users.send_verification_email'):
            res = client.post('/users/add_user', json={
                'email': 'test@example.com',
                'user_name': 'differentuser',
                'password': 'Test@1234'
            })
        assert res.status_code == 400
        assert 'Email already registered' in res.get_json()['error']

    # Duplicate username returns 400
    def test_register_duplicate_username(self, client, verified_user):
        with patch('backend.app.routes.users.send_verification_email'):
            res = client.post('/users/add_user', json={
                'email': 'different@example.com',
                'user_name': 'testuser',
                'password': 'Test@1234'
            })
        assert res.status_code == 400
        assert 'Username already exists' in res.get_json()['error']

    # Mail failure still returns 201 — user is created
    def test_register_mail_failure_still_succeeds(self, client):
        with patch('backend.app.routes.users.send_verification_email',
                   side_effect=Exception('SMTP error')):
            res = client.post('/users/add_user', json={
                'email': 'mailfail@example.com',
                'user_name': 'mailfailuser',
                'password': 'Test@1234'
            })
        assert res.status_code == 201


class TestLogin:
    # Happy path — verified user gets tokens
    def test_login_success(self, client, verified_user):
        res = client.post('/users/login', json={
            'email': 'test@example.com',
            'password': 'Test@1234'
        })
        assert res.status_code == 200
        data = res.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data

    # Wrong password returns 401
    def test_login_wrong_password(self, client, verified_user):
        res = client.post('/users/login', json={
            'email': 'test@example.com',
            'password': 'WrongPass@1'
        })
        assert res.status_code == 401

    # Unverified user returns 403
    def test_login_unverified_user(self, client, unverified_user):
        res = client.post('/users/login', json={
            'email': 'unverified@example.com',
            'password': 'Test@1234'
        })
        assert res.status_code == 403
        assert 'not verified' in res.get_json()['error'].lower()

    # Non-existent email returns 401
    def test_login_unknown_email(self, client):
        res = client.post('/users/login', json={
            'email': 'nobody@example.com',
            'password': 'Test@1234'
        })
        assert res.status_code == 401

    # Missing fields returns 400
    def test_login_missing_fields(self, client):
        res = client.post('/users/login', json={'email': 'test@example.com'})
        assert res.status_code == 400


class TestEmailVerification:
    # Valid token verifies user
    def test_verify_email_success(self, client, unverified_user, app):
        with app.app_context():
            token = generate_verification_token('unverified@example.com')
        res = client.get(f'/users/verify?token={token}')
        assert res.status_code == 200

    # Invalid token returns error page
    def test_verify_invalid_token(self, client):
        res = client.get('/users/verify?token=badtoken')
        assert res.status_code == 200
        assert b'Invalid' in res.data

    # Missing token returns error page
    def test_verify_missing_token(self, client):
        res = client.get('/users/verify')
        assert res.status_code == 200
        assert b'Missing' in res.data


class TestResendVerification:
    # Unverified user gets a new email
    def test_resend_success(self, client, unverified_user):
        with patch('backend.app.routes.users.send_verification_email'):
            res = client.post('/users/resend-verification', json={
                'email': 'unverified@example.com'
            })
        assert res.status_code == 200

    # Already verified user — same 200 response (no info leakage)
    def test_resend_already_verified(self, client, verified_user):
        res = client.post('/users/resend-verification', json={
            'email': 'test@example.com'
        })
        assert res.status_code == 200

    # Unknown email — same 200 response (no info leakage)
    def test_resend_unknown_email(self, client):
        res = client.post('/users/resend-verification', json={
            'email': 'ghost@example.com'
        })
        assert res.status_code == 200


class TestPasswordReset:
    # Request reset for existing email returns 200
    def test_request_reset_success(self, client, verified_user):
        with patch('backend.app.routes.users.send_password_reset_email'):
            res = client.post('/users/request-password-reset', json={
                'email': 'test@example.com'
            })
        assert res.status_code == 200

    # Request reset for unknown email still returns 200 (no info leakage)
    def test_request_reset_unknown_email(self, client):
        res = client.post('/users/request-password-reset', json={
            'email': 'nobody@example.com'
        })
        assert res.status_code == 200

    # Valid token resets password
    def test_reset_password_success(self, client, verified_user, app):
        from backend.app.utils.password_reset import generate_password_reset_token
        with app.app_context():
            token = generate_password_reset_token('test@example.com')
        res = client.post('/users/reset-password', json={
            'token': token,
            'new_password': 'NewPass@5678'
        })
        assert res.status_code == 200

    # Invalid token returns 400
    def test_reset_password_invalid_token(self, client):
        res = client.post('/users/reset-password', json={
            'token': 'invalidtoken',
            'new_password': 'NewPass@5678'
        })
        assert res.status_code == 400

    # Weak new password returns 400
    def test_reset_password_weak_password(self, client, verified_user, app):
        from backend.app.utils.password_reset import generate_password_reset_token
        with app.app_context():
            token = generate_password_reset_token('test@example.com')
        res = client.post('/users/reset-password', json={
            'token': token,
            'new_password': 'weak'
        })
        assert res.status_code == 400


class TestTokenRefresh:
    # Valid refresh token issues new access token
    def test_refresh_success(self, client, verified_user):
        login = client.post('/users/login', json={
            'email': 'test@example.com',
            'password': 'Test@1234'
        })
        refresh_token = login.get_json()['refresh_token']
        res = client.post('/users/refresh', headers={
            'Authorization': f'Bearer {refresh_token}'
        })
        assert res.status_code == 200
        assert 'access_token' in res.get_json()

    # No token returns 401
    def test_refresh_no_token(self, client):
        res = client.post('/users/refresh')
        assert res.status_code == 401


class TestRateLimiting:
    # Login endpoint gets rate limited after 10 requests per minute
    def test_login_rate_limited(self, client):
        for _ in range(10):
            client.post('/users/login', json={
                'email': 'test@example.com',
                'password': 'wrong'
            })
        res = client.post('/users/login', json={
            'email': 'test@example.com',
            'password': 'wrong'
        })
        assert res.status_code == 429
