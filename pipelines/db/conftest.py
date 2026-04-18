import pytest
import os
from pipelines.db.utils.db_client import DBClient
from config.settings import DB_DSN


def pytest_configure(config):
    config.addinivalue_line("markers", "db: Database pipeline tests")
    config.addinivalue_line("markers", "consistency: UI/API/DB consistency tests")
    config.addinivalue_line("markers", "integrity: Data integrity tests")


@pytest.fixture(scope="session")
def db_client():
    dsn = os.getenv("DATABASE_URL", DB_DSN)
    client = DBClient(dsn)
    yield client
    client.close()


@pytest.fixture(scope="function")
def db(db_client):
    return db_client


@pytest.fixture(scope="session")
def db_tables():
    return {
        "entities": "entities",
        "contacts": "contacts",
        "leads": "leads",
        "pipelines": "pipelines",
        "users": "users",
    }


@pytest.fixture(scope="session")
def api_endpoints():
    return {
        "entities": "/api/entities",
        "contacts": "/api/contacts",
        "leads": "/api/leads",
        "pipelines": "/api/pipelines",
    }