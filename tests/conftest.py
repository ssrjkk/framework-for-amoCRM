"""Pytest fixtures for tests."""

import pytest
from unittest.mock import MagicMock

from api.contacts import ContactsApi
from api.companies import CompaniesApi
from api.deals import DealsApi
from api.users import UsersApi


def create_mock_response(status_code: int = 200, json_data: dict = None, elapsed_ms: int = 50):
    """Create a mock response object."""
    response = MagicMock()
    response.status_code = status_code
    response.json = MagicMock(return_value=json_data or {})
    response.text = ""
    response.raise_for_status = MagicMock()
    response.headers = {"Content-Type": "application/json"}
    mock_elapsed = MagicMock()
    mock_elapsed.total_seconds = MagicMock(return_value=elapsed_ms / 1000)
    response.elapsed = mock_elapsed
    return response


MOCK_COMPANIES = {
    "companies": [
        {"id": 1, "name": "Test Corp", "website": "https://test.com"},
        {"id": 2, "name": "Demo Inc", "website": "https://demo.com"},
    ],
    "total": 2,
    "page": 1,
    "per_page": 20,
}

MOCK_CONTACTS = {
    "contacts": [
        {"id": 1, "name": "John Doe", "email": "john@test.com"},
        {"id": 2, "name": "Jane Smith", "email": "jane@test.com"},
    ],
    "total": 2,
    "page": 1,
    "per_page": 20,
}

MOCK_DEALS = {
    "deals": [
        {"id": 1, "name": "Big Deal", "price": 10000, "status": "pending"},
        {"id": 2, "name": "Small Deal", "price": 1000, "status": "won"},
    ],
    "total": 2,
    "page": 1,
    "per_page": 20,
}

MOCK_USERS = {
    "users": [
        {"id": 1, "name": "Admin", "email": "admin@test.com", "is_admin": True},
        {"id": 2, "name": "User", "email": "user@test.com", "is_admin": False},
    ],
    "total": 2,
    "page": 1,
    "per_page": 20,
}


class MockHTTPClient:
    """Mock HTTP client that returns fake responses."""

    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url

    def get(self, endpoint, params=None):
        endpoint = endpoint.lstrip("/")
        if endpoint == "api/companies" or endpoint.startswith("api/companies/"):
            if params and params.get("query"):
                filtered = {
                    "companies": [
                        c for c in MOCK_COMPANIES["companies"] if params["query"].lower() in c.get("name", "").lower()
                    ],
                    "total": 1,
                }
                return create_mock_response(200, filtered)
            return create_mock_response(200, MOCK_COMPANIES)
        if endpoint == "api/contacts" or endpoint.startswith("api/contacts/"):
            if params and params.get("query"):
                return create_mock_response(200, {"contacts": [], "total": 0})
            return create_mock_response(200, MOCK_CONTACTS)
        if endpoint == "api/deals" or endpoint.startswith("api/deals/"):
            return create_mock_response(200, MOCK_DEALS)
        if endpoint == "api/users" or endpoint.startswith("api/users/"):
            return create_mock_response(200, MOCK_USERS)
        if endpoint == "health" or endpoint.startswith("health/"):
            return create_mock_response(200, {"status": "ok"})
        return create_mock_response(404, {"error": "Not found"})

    def post(self, endpoint, json=None):
        endpoint = endpoint.lstrip("/")
        if endpoint == "api/companies":
            new_company = {"id": 3, "name": json.get("name", "New"), **json}
            return create_mock_response(201, {"company": new_company})
        if endpoint == "api/contacts":
            new_contact = {"id": 3, **json}
            return create_mock_response(201, {"contact": new_contact})
        if endpoint == "api/deals":
            new_deal = {"id": 3, **json}
            return create_mock_response(201, {"deal": new_deal})
        if endpoint == "api/users":
            new_user = {"id": 3, **json}
            return create_mock_response(201, {"user": new_user})
        return create_mock_response(201, {"success": True})

    def put(self, endpoint, json=None):
        endpoint = endpoint.lstrip("/")
        if endpoint.startswith("api/companies/"):
            return create_mock_response(200, {"company": {"id": 1, **json}})
        if endpoint.startswith("api/contacts/"):
            return create_mock_response(200, {"contact": {"id": 1, **json}})
        if endpoint.startswith("api/deals/"):
            return create_mock_response(200, {"deal": {"id": 1, **json}})
        if endpoint.startswith("api/users/"):
            return create_mock_response(200, {"user": {"id": 1, **json}})
        return create_mock_response(200, {"success": True})

    def delete(self, endpoint, params=None):
        endpoint = endpoint.lstrip("/")
        if endpoint.startswith("api/"):
            return create_mock_response(200, {"success": True})
        return create_mock_response(200, {"success": True})

    def close(self):
        pass


@pytest.fixture
def mock_http_client():
    """Provide mock HTTP client for testing."""
    return MockHTTPClient()


@pytest.fixture
def contacts_api(mock_http_client):
    """Contacts API fixture with mock."""
    return ContactsApi(mock_http_client)


@pytest.fixture
def companies_api(mock_http_client):
    """Companies API fixture with mock."""
    return CompaniesApi(mock_http_client)


@pytest.fixture
def deals_api(mock_http_client):
    """Deals API fixture with mock."""
    return DealsApi(mock_http_client)


@pytest.fixture
def users_api(mock_http_client):
    """Users API fixture with mock."""
    return UsersApi(mock_http_client)


@pytest.fixture
def http_client():
    """HTTP client fixture."""
    return MockHTTPClient()


@pytest.fixture
def sample_contact():
    return {"name": "Test User", "email": "test@example.com", "phone": "+1234567890"}


@pytest.fixture
def sample_company():
    return {"name": "Test Company", "website": "https://test.com", "phone": "+1234567890"}


@pytest.fixture
def sample_deal():
    return {"name": "Test Deal", "price": 10000}
