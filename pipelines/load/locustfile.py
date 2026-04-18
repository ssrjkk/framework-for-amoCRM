from locust import HttpUser, task, between, events, constant
from locust.contrib.fasthttp import FastHttpUser
from pipelines.load.thresholds import THRESHOLDS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AMOUser(FastHttpUser):
    wait_time = between(1, 3)
    token = None
    
    def on_start(self):
        response = self.client.post("/auth/login", json={
            "email": "loadtest@example.com",
            "password": "LoadTest123!"
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            logger.warning(f"Login failed: {response.status_code}")

    def get_headers(self):
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    @task(10)
    def get_entities_list(self):
        with self.client.get("/api/entities", headers=self.get_headers()) as resp:
            pass

    @task(5)
    def get_single_entity(self):
        entity_id = 1
        with self.client.get(
            f"/api/entities/{entity_id}",
            headers=self.get_headers()
        ) as resp:
            pass

    @task(3)
    def create_entity(self):
        with self.client.post(
            "/api/entities",
            json={"name": f"LoadTest_{self.environment.runner.user_gid}"},
            headers=self.get_headers()
        ) as resp:
            pass

    @task(2)
    def update_entity(self):
        entity_id = 1
        with self.client.put(
            f"/api/entities/{entity_id}",
            json={"name": "Updated by load test"},
            headers=self.get_headers()
        ) as resp:
            pass

    @task(1)
    def delete_entity(self):
        create_resp = self.client.post(
            "/api/entities",
            json={"name": "To delete"},
            headers=self.get_headers()
        )
        if create_resp.status_code == 201:
            entity_id = create_resp.json().get("id")
            self.client.delete(
                f"/api/entities/{entity_id}",
                headers=self.get_headers()
            )

    @task(8)
    def get_contacts_list(self):
        with self.client.get("/api/contacts", headers=self.get_headers()) as resp:
            pass

    @task(4)
    def get_contact(self):
        contact_id = 1
        with self.client.get(
            f"/api/contacts/{contact_id}",
            headers=self.get_headers()
        ) as resp:
            pass

    @task(2)
    def create_contact(self):
        import random
        with self.client.post(
            "/api/contacts",
            json={
                "name": f"Contact_{random.randint(1000, 9999)}",
                "email": f"loadtest_{random.randint(1000,9999)}@example.com"
            },
            headers=self.get_headers()
        ) as resp:
            pass

    @task(6)
    def get_pipelines(self):
        with self.client.get("/api/pipelines", headers=self.get_headers()) as resp:
            pass

    @task(3)
    def get_leads(self):
        with self.client.get("/api/leads", headers=self.get_headers()) as resp:
            pass

    @task(1)
    def health_check(self):
        with self.client.get("/health") as resp:
            pass


@events.quitting.add_listener
def check_thresholds(environment, **kwargs):
    stats = environment.runner.stats.total
    
    if stats.fail_ratio > THRESHOLDS["error_rate_pct"] / 100:
        logger.error(
            f"FAIL_THRESHOLD: error_rate {stats.fail_ratio:.2%} exceeds "
            f"{THRESHOLDS['error_rate_pct']}%"
        )
        environment.process_exit_code = 1
    
    if stats.avg_response_time > THRESHOLDS["p95_ms"]:
        logger.warning(
            f"WARN_THRESHOLD: avg_response_time {stats.avg_response_time}ms "
            f"exceeds {THRESHOLDS['p95_ms']}ms"
        )
    
    total_rps = stats.total_rps
    if total_rps < THRESHOLDS["rps_min"]:
        logger.error(
            f"FAIL_THRESHOLD: rps {total_rps:.2f} below minimum {THRESHOLDS['rps_min']}"
        )
        environment.process_exit_code = 1
    
    logger.info(f"Load test stats: {stats}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    logger.info("Load test starting...")
    logger.info(f"Thresholds: {THRESHOLDS}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    logger.info("Load test completed")
    stats = environment.runner.stats.total
    logger.info(f"Total requests: {stats.num_requests}")
    logger.info(f"Total failures: {stats.num_failures}")
    logger.info(f"Fail ratio: {stats.fail_ratio:.2%}")
    logger.info(f"Average response time: {stats.avg_response_time}ms")
    logger.info(f"RPS: {stats.total_rps:.2f}")