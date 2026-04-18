import pytest
import os
from pipelines.api.utils.http_client import APIClient
from config.settings import BASE_URL


def pytest_configure(config):
    config.addinivalue_line("markers", "api: API pipeline tests")
    config.addinivalue_line("markers", "contract: Contract validation tests")
    config.addinivalue_line("markers", "smoke: Quick smoke tests")


@pytest.fixture(scope="session")
def api_client():
    return APIClient(base_url=BASE_URL)


@pytest.fixture(scope="session")
def api_token(api_client):
    email = os.getenv("AMO_TEST_EMAIL", "test@example.com")
    password = os.getenv("AMO_TEST_PASSWORD", "TestPass123!")
    resp = api_client.auth_login(email, password)
    if resp.status_code == 200:
        return resp.json().get("access_token")
    pytest.skip(f"Cannot obtain token: {resp.status_code}")


@pytest.fixture(scope="session")
def authenticated_client(api_client, api_token):
    api_client.set_token(api_token)
    return api_client


@pytest.fixture(scope="function")
def test_entity(authenticated_client):
    resp = authenticated_client.post("/entities", json={"name": "test_entity"})
    if resp.status_code != 201:
        yield None
    else:
        entity_id = resp.json().get("id")
        yield entity_id
        try:
            authenticated_client.delete(f"/entities/{entity_id}")
        except:
            pass


@pytest.fixture(scope="session")
def api_base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def test_users():
    return {
        "admin": {"email": "admin@test.com", "password": "Admin123!", "role": "admin"},
        "user": {"email": "user@test.com", "password": "User123!", "role": "user"},
        "viewer": {"email": "viewer@test.com", "password": "Viewer123!", "role": "viewer"},
    }