import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import AMOCRM_API_BASE, AMOCRM_OAUTH_URL, CLIENT_ID, CLIENT_SECRET, AMOCRM_LONG_TOKEN
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AmoCRMClient:
    def __init__(self, base_url: str = None, long_token: str = None):
        self.base_url = base_url or AMOCRM_API_BASE
        self.oauth_url = AMOCRM_OAUTH_URL
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.access_token = long_token or AMOCRM_LONG_TOKEN
        self.refresh_token = None
        self.expires_at = 0
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self):
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        logger.info(f"{method} {url}")
        response = self.session.request(
            method, url, headers=self._headers(), **kwargs
        )
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 401 and self.refresh_token:
            self._refresh_token()
            response = self.session.request(
                method, url, headers=self._headers(), **kwargs
            )
        
        return response

    def get(self, path: str, params: dict = None, **kwargs):
        return self.request("GET", path, params=params, **kwargs)

    def post(self, path: str, json: dict = None, **kwargs):
        return self.request("POST", path, json=json, **kwargs)

    def put(self, path: str, json: dict = None, **kwargs):
        return self.request("PUT", path, json=json, **kwargs)

    def patch(self, path: str, json: dict = None, **kwargs):
        return self.request("PATCH", path, json=json, **kwargs)

    def delete(self, path: str, **kwargs):
        return self.request("DELETE", path, **kwargs)

    def oauth_authorize(self, code: str):
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
        }
        resp = self.session.post(f"{self.oauth_url}/token", data=data)
        if resp.status_code == 200:
            tokens = resp.json()
            self.access_token = tokens["access_token"]
            self.refresh_token = tokens["refresh_token"]
            self.expires_at = time.time() + tokens["expires_in"]
        return resp

    def _refresh_token(self):
        if not self.refresh_token:
            return
        
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
        }
        resp = self.session.post(f"{self.oauth_url}/token", data=data)
        if resp.status_code == 200:
            tokens = resp.json()
            self.access_token = tokens["access_token"]
            self.refresh_token = tokens["refresh_token"]
            self.expires_at = time.time() + tokens["expires_in"]

    def set_token(self, token: str):
        self.access_token = token

    @property
    def account(self):
        return AccountAPI(self)

    @property
    def contacts(self):
        return ContactsAPI(self)

    @property
    def companies(self):
        return CompaniesAPI(self)

    @property
    def leads(self):
        return LeadsAPI(self)

    @property
    def tasks(self):
        return TasksAPI(self)

    @property
    def pipelines(self):
        return PipelinesAPI(self)

    @property
    def fields(self):
        return FieldsAPI(self)

    @property
    def tags(self):
        return TagsAPI(self)

    @property
    def users(self):
        return UsersAPI(self)

    @property
    def webhooks(self):
        return WebhooksAPI(self)


class AccountAPI:
    def __init__(self, client: AmoCRMClient):
        self.client = client

    def get(self):
        return self.client.get("/account")


class ContactsAPI:
    def __init__(self, client: AmoCRMClient):
        self.client = client

    def list(self, **params):
        return self.client.get("/contacts", params=params)

    def get(self, contact_id: int):
        return self.client.get(f"/contacts/{contact_id}")

    def create(self, data: dict):
        return self.client.post("/contacts", json=[data])

    def update(self, contact_id: int, data: dict):
        return self.client.patch(f"/contacts/{contact_id}", json=[data])

    def delete(self, contact_id: int):
        return self.client.delete(f"/contacts/{contact_id}")

    def link(self, contact_id: int, entity_type: str, entity_id: int):
        return self.client.post(f"/contacts/{contact_id}/link", json=[{
            "to": {"entity": entity_type, "id": entity_id}
        }])

    def unlink(self, contact_id: int, entity_type: str, entity_id: int):
        return self.client.post(f"/contacts/{contact_id}/unlink", json=[{
            "from": {"entity": entity_type, "id": entity_id}
        }])


class CompaniesAPI:
    def __init__(self, client: AmoCRMClient):
        self.client = client

    def list(self, **params):
        return self.client.get("/companies", params=params)

    def get(self, company_id: int):
        return self.client.get(f"/companies/{company_id}")

    def create(self, data: dict):
        return self.client.post("/companies", json=[data])

    def update(self, company_id: int, data: dict):
        return self.client.patch(f"/companies/{company_id}", json=[data])

    def delete(self, company_id: int):
        return self.client.delete(f"/companies/{company_id}")


class LeadsAPI:
    def __init__(self, client: AmoCRMClient):
        self.client = client

    def list(self, **params):
        return self.client.get("/leads", params=params)

    def get(self, lead_id: int):
        return self.client.get(f"/leads/{lead_id}")

    def create(self, data: dict):
        return self.client.post("/leads", json=[data])

    def update(self, lead_id: int, data: dict):
        return self.client.patch(f"/leads/{lead_id}", json=[data])

    def delete(self, lead_id: int):
        return self.client.delete(f"/leads/{lead_id}")

    def link(self, lead_id: int, entity_type: str, entity_id: int):
        return self.client.post(f"/leads/{lead_id}/link", json=[{
            "to": {"entity": entity_type, "id": entity_id}
        }])


class TasksAPI:
    def __init__(self, client: AmoCRMClient):
        self.client = client

    def list(self, **params):
        return self.client.get("/tasks", params=params)

    def get(self, task_id: int):
        return self.client.get(f"/tasks/{task_id}")

    def create(self, data: dict):
        return self.client.post("/tasks", json=[data])

    def complete(self, task_id: int):
        return self.client.post(f"/tasks/{task_id}/complete", json={})

    def delete(self, task_id: int):
        return self.client.delete(f"/tasks/{task_id}")


class PipelinesAPI:
    def __init__(self, client: AmoCRMClient):
        self.client = client

    def list(self):
        return self.client.get("/leads/pipelines")

    def get(self, pipeline_id: int):
        return self.client.get(f"/leads/pipelines/{pipeline_id}")

    def create(self, data: dict):
        return self.client.post("/leads/pipelines", json=[data])

    def update(self, pipeline_id: int, data: dict):
        return self.client.patch(f"/leads/pipelines/{pipeline_id}", json=[data])

    def delete(self, pipeline_id: int):
        return self.client.delete(f"/leads/pipelines/{pipeline_id}")

    def get_statuses(self, pipeline_id: int):
        return self.client.get(f"/leads/pipelines/{pipeline_id}/statuses")


class FieldsAPI:
    def __init__(self, client: AmoCRMClient):
        self.client = client

    def list(self, entity: str):
        return self.client.get(f"/{entity}/custom_fields")

    def create(self, entity: str, data: dict):
        return self.client.post(f"/{entity}/custom_fields", json=[data])

    def update(self, entity: str, field_id: int, data: dict):
        return self.client.patch(f"/{entity}/custom_fields/{field_id}", json=[data])

    def delete(self, entity: str, field_id: int):
        return self.client.delete(f"/{entity}/custom_fields/{field_id}")


class TagsAPI:
    def __init__(self, client: AmoCRMClient):
        self.client = client

    def list(self):
        return self.client.get("/tags")

    def create(self, data: dict):
        return self.client.post("/tags", json=[data])

    def delete(self, tag_id: int):
        return self.client.delete(f"/tags/{tag_id}")


class UsersAPI:
    def __init__(self, client: AmoCRMClient):
        self.client = client

    def list(self):
        return self.client.get("/users")

    def me(self):
        return self.client.get("/users/me")

    def get(self, user_id: int):
        return self.client.get(f"/users/{user_id}")

    def add(self, data: dict):
        return self.client.post("/users", json=[data])

    def delete(self, user_id: int):
        return self.client.delete(f"/users/{user_id}")


class WebhooksAPI:
    def __init__(self, client: AmoCRMClient):
        self.client = client

    def list(self):
        return self.client.get("/webhooks")

    def subscribe(self, url: str, events: list):
        return self.client.post("/webhooks", json={
            "url": url,
            "events": events
        })

    def unsubscribe(self, webhook_id: int):
        return self.client.delete(f"/webhooks/{webhook_id}")