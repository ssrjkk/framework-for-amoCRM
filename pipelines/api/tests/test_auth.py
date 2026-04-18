import pytest
import os


pytestmark = [pytest.mark.api, pytest.mark.smoke]


class TestAuth:
    def test_account_info(self, api_client):
        resp = api_client.account.get()
        assert resp.status_code in [200, 401]
        
        if resp.status_code == 200:
            data = resp.json()
            assert "id" in data or "account" in data

    def test_users_me(self, api_client):
        resp = api_client.users.me()
        assert resp.status_code in [200, 401]

    def test_no_token_returns_401(self):
        from pipelines.api.utils.http_client import AmoCRMClient
        client = AmoCRMClient()
        resp = client.account.get()
        assert resp.status_code == 401

    def test_invalid_token_returns_401(self):
        from pipelines.api.utils.http_client import AmoCRMClient
        client = AmoCRMClient(long_token="invalid_token_123")
        resp = client.account.get()
        assert resp.status_code == 401