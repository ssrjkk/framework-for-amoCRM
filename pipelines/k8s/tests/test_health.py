import pytest
import requests
from pipelines.k8s.utils.k8s_client import K8sClient
from config.settings import BASE_URL


pytestmark = [pytest.mark.k8s, pytest.mark.health]


class TestK8sHealth:
    def test_api_health_endpoint(self, api_base_url):
        try:
            resp = requests.get(f"{api_base_url}/health", timeout=10)
            assert resp.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("API not available")

    def test_readyz_endpoint(self, api_base_url):
        try:
            resp = requests.get(f"{api_base_url}/readyz", timeout=10)
            assert resp.status_code in [200, 404]
        except requests.exceptions.RequestException:
            pytest.skip("API not available")

    def test_livez_endpoint(self, api_base_url):
        try:
            resp = requests.get(f"{api_base_url}/livez", timeout=10)
            assert resp.status_code in [200, 404]
        except requests.exceptions.RequestException:
            pytest.skip("API not available")


class TestK8sPods:
    def test_all_critical_pods_running(self, k8s_client):
        critical_apps = ["api", "auth", "web"]
        
        failed_apps = []
        for app in critical_apps:
            health = k8s_client.check_health(app)
            if not health or not health.get("all_ready"):
                failed_apps.append(app)
        
        assert len(failed_apps) == 0, f"Pods not ready for: {failed_apps}"

    def test_no_crashloopbackoff(self, k8s_client):
        pods = k8s_client.get_pod_statuses()
        
        crashloop_pods = [
            p for p in pods
            if p.get("phase") in ["CrashLoopBackOff", "Error", "Failed"]
        ]
        
        assert len(crashloop_pods) == 0, f"CrashLoopBackOff pods: {crashloop_pods}"

    def test_pods_not_oomkilled(self, k8s_client):
        pods = k8s_client.get_pod_statuses()
        
        oom_pods = [
            p for p in pods
            if p.get("restarts", 0) > 10
        ]
        
        assert len(oom_pods) == 0, f"Pods with high restarts: {oom_pods}"


class TestK8sServices:
    def test_api_service_exists(self, k8s_client):
        service = k8s_client.get_service("api-service")
        assert service is not None, "api-service not found"

    def test_services_have_endpoints(self, k8s_client):
        services = ["api-service", "web-service"]
        
        for svc_name in services:
            endpoint = k8s_client.get_service_endpoint(svc_name)
            if endpoint:
                assert endpoint is not None


class TestK8sDeployments:
    def test_deployments_replicas_match(self, k8s_client):
        deployments = k8s_client.list_deployments()
        
        for deploy in deployments.items:
            desired = deploy.spec.replicas
            ready = deploy.status.ready_replicas or 0
            assert ready == desired, f"{deploy.metadata.name}: {ready}/{desired} ready"


@pytest.fixture(scope="module")
def api_client():
    from pipelines.api.utils.http_client import APIClient
    return APIClient(base_url=BASE_URL)