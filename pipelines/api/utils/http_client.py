import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import BASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, base_url: str = BASE_URL, token: str = None):
        self.base_url = base_url
        self.session = requests.Session()
        self._setup_session()
        self.token = token

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
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        logger.info(f"{method} {url}")
        response = self.session.request(
            method, url, headers=self._headers(), **kwargs
        )
        logger.info(f"Status: {response.status_code}")
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

    def auth_login(self, email: str, password: str):
        resp = self.post("/auth/login", json={"email": email, "password": password})
        if resp.status_code == 200:
            data = resp.json()
            self.token = data.get("access_token")
        return resp

    def auth_refresh(self, refresh_token: str):
        return self.post("/auth/refresh", json={"refresh_token": refresh_token})

    def set_token(self, token: str):
        self.token = token