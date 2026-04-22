from locust import task, between, events
from locust.contrib.fasthttp import FastHttpUser
from pipelines.load.thresholds import THRESHOLDS
import logging
import os
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AMOCRM_SUBDOMAIN = os.getenv("AMOCRM_SUBDOMAIN", "test")
AMOCRM_LONG_TOKEN = os.getenv("AMOCRM_LONG_TOKEN", "")
USE_MOCK = os.getenv("USE_MOCK", "true").lower() == "true"

if USE_MOCK or not AMOCRM_LONG_TOKEN:
    BASE_URL = os.getenv("APP_URL", "http://localhost:8080")
    logger.info(f"Using mock mode: {BASE_URL}")
else:
    BASE_URL = f"https://{AMOCRM_SUBDOMAIN}.amocrm.ru/api/v4"
    logger.info(f"Using real API: {BASE_URL}")


class AmoCRMUser(FastHttpUser):
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        self.token = AMOCRM_LONG_TOKEN
        if not self.token:
            logger.warning("No LONG_TOKEN configured")

    def get_headers(self):
        if self.token:
            return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        return {"Content-Type": "application/json"}

    @task(10)
    def list_contacts(self):
        with self.client.get(f"{BASE_URL}/contacts", headers=self.get_headers()):
            pass

    @task(5)
    def get_single_contact(self):
        with self.client.get(f"{BASE_URL}/contacts/1", headers=self.get_headers()):
            pass

    @task(3)
    def create_contact(self):
        name = f"LoadTest_{random.randint(1000, 9999)}"
        with self.client.post(f"{BASE_URL}/contacts", json=[{"name": name}], headers=self.get_headers()):
            pass

    @task(8)
    def list_companies(self):
        with self.client.get(f"{BASE_URL}/companies", headers=self.get_headers()):
            pass

    @task(6)
    def list_leads(self):
        with self.client.get(f"{BASE_URL}/leads", headers=self.get_headers()):
            pass

    @task(4)
    def create_lead(self):
        with self.client.post(
            f"{BASE_URL}/leads",
            json=[{"name": f"Lead_{random.randint(1000, 9999)}", "price": random.randint(1000, 100000)}],
            headers=self.get_headers(),
        ):
            pass

    @task(2)
    def list_tasks(self):
        with self.client.get(f"{BASE_URL}/tasks", headers=self.get_headers()):
            pass

    @task(5)
    def list_pipelines(self):
        with self.client.get(f"{BASE_URL}/leads/pipelines", headers=self.get_headers()):
            pass

    @task(3)
    def list_users(self):
        with self.client.get(f"{BASE_URL}/users", headers=self.get_headers()):
            pass

    @task(2)
    def list_tags(self):
        with self.client.get(f"{BASE_URL}/tags", headers=self.get_headers()):
            pass

    @task(1)
    def account_info(self):
        with self.client.get(f"{BASE_URL}/account", headers=self.get_headers()):
            pass


@events.quitting.add_listener
def check_thresholds(environment, **kwargs):
    stats = environment.runner.stats.total

    if stats.fail_ratio > THRESHOLDS["error_rate_pct"] / 100:
        logger.error(f"FAIL: error_rate {stats.fail_ratio:.2%} > {THRESHOLDS['error_rate_pct']}%")
        environment.process_exit_code = 1

    if stats.avg_response_time > THRESHOLDS["p95_ms"]:
        logger.warning(f"WARN: avg {stats.avg_response_time}ms > {THRESHOLDS['p95_ms']}ms")

    total_rps = stats.total_rps
    if total_rps < THRESHOLDS["rps_min"]:
        logger.error(f"FAIL: rps {total_rps:.2f} < {THRESHOLDS['rps_min']}")
        environment.process_exit_code = 1

    logger.info(
        f"Stats: {stats.num_requests} req, {stats.fail_ratio:.2%} fail, {stats.avg_response_time}ms avg, {total_rps:.2f} rps"
    )


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    logger.info(f"Load test started against {BASE_URL}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    stats = environment.runner.stats.total
    logger.info(f"Load test complete: {stats.num_requests} requests, {stats.num_failures} failures")
