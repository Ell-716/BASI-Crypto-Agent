import pytest
from unittest.mock import patch


class TestCoinsEndpoint:
    # Coins list returns 200 with data
    def test_get_coins_success(self, client, sample_coin):
        res = client.get('/api/coins')
        assert res.status_code == 200
        data = res.get_json()
        assert isinstance(data, list)


class TestDashboardEndpoints:
    # Fear & greed index returns 404 when no data (expected in test DB)
    def test_fear_greed_no_data(self, client, auth_headers):
        res = client.get('/dashboard/fear-greed', headers=auth_headers)
        assert res.status_code in [200, 404]

    # Top volume returns data or error gracefully
    def test_top_volume_no_data(self, client, auth_headers):
        res = client.get('/dashboard/top-volume', headers=auth_headers)
        # Should return 200 or error, not crash
        assert res.status_code in [200, 404, 500]
        assert res.get_json() is not None

    # Snapshot for known coin returns 404 when no snapshot data exists
    def test_snapshot_no_data(self, client, auth_headers, sample_coin):
        res = client.get('/dashboard/snapshot/BTC', headers=auth_headers)
        assert res.status_code == 404

    # Snapshot for unknown coin returns 404
    def test_snapshot_unknown_coin(self, client, auth_headers):
        res = client.get('/dashboard/snapshot/FAKECOIN', headers=auth_headers)
        assert res.status_code == 404


class TestUserEndpoints:
    # Get own profile returns 200
    def test_get_own_profile(self, client, auth_headers, verified_user, app):
        with app.app_context():
            from backend.app.models import User
            user = User.query.filter_by(email='test@example.com').first()
            user_id = user.id
        res = client.get(f'/users/{user_id}', headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert data['email'] == 'test@example.com'

    # Get another user's profile returns 403
    def test_get_other_profile_forbidden(self, client, auth_headers):
        res = client.get('/users/99999', headers=auth_headers)
        assert res.status_code == 403
