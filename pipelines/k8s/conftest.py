import pytest
from pipelines.k8s.utils.k8s_client import K8sClient
from config.settings import K8S_NAMESPACE, BASE_URL


def pytest_configure(config):
    config.addinivalue_line("markers", "k8s: Kubernetes smoke tests")
    config.addinivalue_line("markers", "smoke: Quick smoke tests")
    config.addinivalue_line("markers", "health: Health check tests")


@pytest.fixture(scope="session")
def k8s_client():
    return K8sClient()


@pytest.fixture(scope="session")
def k8s_namespace():
    return K8S_NAMESPACE


@pytest.fixture(scope="session")
def api_base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def app_labels():
    return {
        "api": "app=api",
        "auth": "app=auth",
        "web": "app=web",
        "db": "app=postgres",
        "kafka": "app=kafka",
    }


@pytest.fixture(scope="session")
def smoke_services():
    return ["api", "auth", "web"]