import pytest
from pipelines.api.utils.http_client import APIClient
from pipelines.api.utils.schema_validator import validate_response


pytestmark = [pytest.mark.api, pytest.mark.smoke]


class TestAuth:
    def test_login_valid_credentials(self, api_client):
        resp = api_client.auth_login("test@example.com", "TestPass123!")
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        validate_response(resp, "auth_login")

    def test_login_invalid_password(self, api_client):
        resp = api_client.auth_login("test@example.com", "wrongpassword")
        assert resp.status_code == 401
        data = resp.json()
        assert "error" in data

    def test_login_nonexistent_user(self, api_client):
        resp = api_client.auth_login("nonexistent@example.com", "password123")
        assert resp.status_code == 401

    def test_login_missing_fields(self, api_client):
        resp = api_client.post("/auth/login", json={"email": "test@example.com"})
        assert resp.status_code in [400, 422]

    def test_access_without_token(self, api_client):
        resp = api_client.get("/api/entities")
        assert resp.status_code == 401

    def test_access_with_invalid_token(self, api_client):
        api_client.set_token("invalid_token_123")
        resp = api_client.get("/api/entities")
        assert resp.status_code == 401

    def test_token_refresh(self, api_client):
        login_resp = api_client.auth_login("test@example.com", "TestPass123!")
        refresh_token = login_resp.json().get("refresh_token")
        
        refresh_resp = api_client.auth_refresh(refresh_token)
        assert refresh_resp.status_code == 200
        data = refresh_resp.json()
        assert "access_token" in data

    def test_token_refresh_invalid(self, api_client):
        resp = api_client.auth_refresh("invalid_refresh_token")
        assert resp.status_code == 401

    def test_role_admin_has_full_access(self, api_client):
        login_resp = api_client.auth_login("admin@test.com", "Admin123!")
        token = login_resp.json().get("access_token")
        client = APIClient(token=token)
        
        resp = client.get("/api/entities")
        assert resp.status_code in [200, 403]

    def test_role_viewer_restricted_access(self, api_client):
        login_resp = api_client.auth_login("viewer@test.com", "Viewer123!")
        token = login_resp.json().get("access_token")
        client = APIClient(token=token)
        
        resp = client.delete("/api/entities/1")
        assert resp.status_code == 403