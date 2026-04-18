import pytest
from datetime import datetime, timedelta, timezone
from pipelines.logs.utils.kibana_client import KibanaClient


def pytest_configure(config):
    config.addinivalue_line("markers", "logs: Log analysis tests")
    config.addinivalue_line("markers", "kibana: Kibana/Elasticsearch tests")


class TestRunTimer:
    start_time = None
    end_time = None


@pytest.fixture(scope="session")
def test_run_timer():
    return TestRunTimer()


@pytest.fixture(scope="session")
def test_run_window(test_run_timer):
    if not test_run_timer.start_time:
        test_run_timer.start_time = datetime.now(timezone.utc)
    yield test_run_timer.start_time
    test_run_timer.end_time = datetime.now(timezone.utc)


@pytest.fixture(scope="session")
def kibana_client():
    return KibanaClient()


@pytest.fixture(scope="session")
def logs_index_pattern():
    return "logs-*"


@pytest.fixture(scope="session")
def test_context():
    return {
        "session_id": pytest.sessionid if hasattr(pytest, "sessionid") else "default",
        "branch": "main",
    }