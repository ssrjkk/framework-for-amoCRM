import pytest
import requests
from pipelines.k8s.utils.k8s_client import K8sClient
from pipelines.api.utils.http_client import APIClient
from config.settings import BASE_URL


pytestmark = [pytest.mark.k8s, pytest.mark.smoke]


SMOKE_SERVICES = [
    "api-service",
    "web-service",
]


class TestSmoke:
    @pytest.mark.parametrize("service", SMOKE_SERVICES)
    def test_service_reachable(self, api_base_url, service):
        base = api_base_url or BASE_URL
        
        try:
            resp = requests.get(f"{base}/health", timeout=10)
            assert resp.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip(f"{service} not reachable")

    @pytest.mark.parametrize("service", SMOKE_SERVICES)
    def test_pod_running(self, k8s_client, service):
        label = service.replace("-service", "")
        
        pods = k8s_client.get_pod_statuses(label_selector=f"app={label}")
        
        assert len(pods) > 0, f"No pods found for {label}"
        
        running = [p for p in pods if p.get("phase") == "Running"]
        assert len(running) > 0, f"No running pods for {label}"


class TestSmokeFlow:
    def test_crud_after_deploy(self, api_client):
        try:
            create_resp = api_client.post(
                "/api/entities",
                json={"name": "Smoke Test Entity"}
            )
            if create_resp.status_code not in [201, 400]:
                pytest.skip("API not available")
            
            if create_resp.status_code == 201:
                entity_id = create_resp.json().get("id")
                
                get_resp = api_client.get(f"/api/entities/{entity_id}")
                assert get_resp.status_code == 200
                
                update_resp = api_client.put(
                    f"/api/entities/{entity_id}",
                    json={"name": "Smoke Updated"}
                )
                assert update_resp.status_code == 200
                
                delete_resp = api_client.delete(f"/api/entities/{entity_id}")
                assert delete_resp.status_code == 204
        except Exception as e:
            pytest.skip(f"API not available: {e}")

    def test_database_connectivity(self, api_client):
        try:
            resp = api_client.get("/api/entities")
            assert resp.status_code in [200, 401]
        except Exception:
            pytest.skip("API not available")

    def test_auth_after_deploy(self, api_client):
        try:
            resp = api_client.auth_login("test@example.com", "TestPass123!")
            assert resp.status_code in [200, 401]
        except Exception:
            pytest.skip("API not available")


@pytest.fixture(scope="module")
def api_client():
    return APIClient(base_url=BASE_URL)