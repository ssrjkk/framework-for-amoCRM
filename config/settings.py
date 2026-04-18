import os

AMOCRM_SUBDOMAIN = os.getenv("AMOCRM_SUBDOMAIN", "test")
AMOCRM_API_BASE = f"https://{AMOCRM_SUBDOMAIN}.amocrm.ru/api/v4"
AMOCRM_OAUTH_URL = f"https://{AMOCRM_SUBDOMAIN}.amocrm.ru/oauth2"

CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8080/callback")

AMOCRM_LONG_TOKEN = os.getenv("AMOCRM_LONG_TOKEN", "")

DB_DSN = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/amocrm")
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092").split(",")
K8S_NAMESPACE = os.getenv("K8S_NAMESPACE", "default")
KIBANA_URL = os.getenv("KIBANA_URL", "http://localhost:5601")
SELENIUM_GRID = os.getenv("SELENIUM_GRID", "http://localhost:4444/wd/hub")

BROWSERS = ["chrome", "firefox", "edge"]

LOAD_THRESHOLDS = {
    "p95_ms": 500,
    "error_rate_pct": 1.0,
    "rps_min": 100,
}

TEST_USERS = {
    "admin": {"email": "admin@test.com", "password": "Admin123!"},
    "user": {"email": "user@test.com", "password": "User123!"},
}