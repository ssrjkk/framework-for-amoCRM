import os

BASE_URL = os.getenv("BASE_URL", "https://www.amocrm.ru")
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
    "admin": {"email": "admin@amocrm.ru", "password": "Admin123!"},
    "user": {"email": "user@amocrm.ru", "password": "User123!"},
    "viewer": {"email": "viewer@amocrm.ru", "password": "Viewer123!"},
}

AMOCRM_API_BASE = "https://www.amocrm.ru/api"
AMOCRM_ACCOUNTS_API = "https://accounts.amocrm.ru"