import pytest
import os
from pipelines.api.utils.http_client import AmoCRMClient
from config.settings import AMOCRM_LONG_TOKEN, CLIENT_ID, CLIENT_SECRET, AMOCRM_SUBDOMAIN


def pytest_configure(config):
    config.addinivalue_line("markers", "api: API pipeline tests")
    config.addinivalue_line("markers", "contract: Contract validation tests")
    config.addinivalue_line("markers", "smoke: Quick smoke tests")


@pytest.fixture(scope="session")
def api_client():
    token = os.getenv("AMOCRM_LONG_TOKEN", AMOCRM_LONG_TOKEN)
    return AmoCRMClient(long_token=token)


@pytest.fixture(scope="session")
def api_token(api_client):
    if not api_client.access_token:
        pytest.skip("No LONG_TOKEN configured")
    return api_client.access_token


@pytest.fixture(scope="session")
def authenticated_client(api_client):
    if not api_client.access_token:
        pytest.skip("No LONG_TOKEN configured")
    return api_client


@pytest.fixture(scope="function")
def test_contact(authenticated_client):
    resp = authenticated_client.contacts.create({
        "name": "Test Contact",
        "custom_fields_values": [
            {"field_id": 1, "values": [{"value": "test@test.com"}]}
        ]}
    })
    
    if resp.status_code != 200:
        yield None
    else:
        contact_id = resp.json()["_embedded"]["contacts"][0]["id"]
        yield contact_id
        try:
            authenticated_client.contacts.delete(contact_id)
        except:
            pass


@pytest.fixture(scope="function")
def test_lead(authenticated_client):
    resp = authenticated_client.leads.create({
        "name": "Test Lead",
        "price": 10000,
    })
    
    if resp.status_code != 200:
        yield None
    else:
        lead_id = resp.json()["_embedded"]["leads"][0]["id"]
        yield lead_id
        try:
            authenticated_client.leads.delete(lead_id)
        except:
            pass


@pytest.fixture(scope="session")
def account(authenticated_client):
    return authenticated_client.account.get()


@pytest.fixture(scope="session")
def api_base_url():
    from config.settings import AMOCRM_API_BASE
    return AMOCRM_API_BASE