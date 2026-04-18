from kubernetes import client, config
from kubernetes.client import ApiClient
from config.settings import K8S_NAMESPACE
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class K8sClient:
    def __init__(self, namespace: str = None):
        self.namespace = namespace or K8S_NAMESPACE
        self._core_v1 = None
        self._apps_v1 = None
        self._networking_v1 = None
        self._load_config()

    def _load_config(self):
        try:
            if os.getenv("KUBERNETES_SERVICE_HOST"):
                config.load_incluster_config()
                logger.info("Loaded in-cluster config")
            else:
                config.load_kube_config()
                logger.info("Loaded kubeconfig")
        except Exception as e:
            logger.warning(f"Could not load K8s config: {e}")
        
        self._core_v1 = client.CoreV1Api()
        self._apps_v1 = client.AppsV1Api()
        self._networking_v1 = client.NetworkingV1Api()

    @property
    def core_v1(self):
        return self._core_v1

    @property
    def apps_v1(self):
        return self._apps_v1

    def list_pods(self, label_selector: str = None, field_selector: str = None):
        return self._core_v1.list_namespaced_pod(
            self.namespace,
            label_selector=label_selector,
            field_selector=field_selector
        )

    def get_pod_status(self, pod_name: str):
        try:
            return self._core_v1.read_namespaced_pod(pod_name, self.namespace)
        except Exception as e:
            logger.error(f"Pod {pod_name} not found: {e}")
            return None

    def get_pod_statuses(self, label_selector: str = None) -> list:
        pods = self.list_pods(label_selector=label_selector)
        result = []
        for pod in pods.items:
            result.append({
                "name": pod.metadata.name,
                "phase": pod.status.phase,
                "ready": self._is_pod_ready(pod),
                "restarts": self._get_restart_count(pod),
                "age": pod.metadata.creation_timestamp,
            })
        return result

    def _is_pod_ready(self, pod) -> bool:
        if not pod.status.conditions:
            return False
        for condition in pod.status.conditions:
            if condition.type == "Ready":
                return condition.status == "True"
        return False

    def _get_restart_count(self, pod) -> int:
        return sum(
            c.restart_count for c in (pod.status.container_statuses or [])
        )

    def list_services(self, label_selector: str = None):
        return self._core_v1.list_namespaced_service(
            self.namespace,
            label_selector=label_selector
        )

    def get_service(self, service_name: str):
        try:
            return self._core_v1.read_namespaced_service(
                service_name, self.namespace
            )
        except Exception as e:
            logger.error(f"Service {service_name} not found: {e}")
            return None

    def get_service_endpoint(self, service_name: str) -> str:
        service = self.get_service(service_name)
        if not service:
            return None
        
        if service.spec.type == "LoadBalancer":
            return service.status.load_balancer.ingress[0].ip if service.status.load_balancer.ingress else None
        
        return service.spec.cluster_ip

    def list_deployments(self, label_selector: str = None):
        return self._apps_v1.list_namespaced_deployment(
            self.namespace,
            label_selector=label_selector
        )

    def get_deployment(self, deployment_name: str):
        try:
            return self._apps_v1.read_namespaced_deployment(
                deployment_name, self.namespace
            )
        except Exception:
            return None

    def get_deployment_status(self, deployment_name: str) -> dict:
        deployment = self.get_deployment(deployment_name)
        if not deployment:
            return None
        
        return {
            "name": deployment.metadata.name,
            "replicas": deployment.spec.replicas,
            "ready_replicas": deployment.status.ready_replicas,
            "available_replicas": deployment.status.available_replicas,
            "updated_replicas": deployment.status.updated_replicas,
        }

    def list_ingresses(self, label_selector: str = None):
        return self._networking_v1.list_namespaced_ingress(
            self.namespace,
            label_selector=label_selector
        )

    def check_health(self, app_label: str) -> dict:
        pods = self.get_pod_statuses(label_selector=f"app={app_label}")
        
        all_ready = all(p["ready"] for p in pods) if pods else False
        any_restarting = any(p["restarts"] > 5 for p in pods) if pods else False
        
        return {
            "namespace": self.namespace,
            "app": app_label,
            "pods_count": len(pods),
            "all_ready": all_ready,
            "has_issues": any_restarting,
            "pods": pods,
        }


@pytest.fixture(scope="session")
def k8s_client():
    return K8sClient()


@pytest.fixture(scope="session")
def k8s_namespace():
    return K8S_NAMESPACE