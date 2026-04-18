import requests
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from config.settings import KIBANA_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KibanaClient:
    def __init__(
        self,
        base_url: str = None,
        es_host: str = None,
        index_pattern: str = "logs-*"
    ):
        self.base_url = base_url or KIBANA_URL
        self.es_host = es_host or self.base_url.replace("5601", "9200")
        self.index_pattern = index_pattern
        self._client = None

    def _get_client(self):
        if not self._client:
            try:
                self._client = Elasticsearch([self.es_host])
            except Exception as e:
                logger.warning(f"Cannot connect to Elasticsearch: {e}")
                self._client = None
        return self._client

    def search(
        self,
        query: dict = None,
        start: datetime = None,
        end: datetime = None,
        size: int = 100
    ) -> list:
        client = self._get_client()
        if not client:
            return []
        
        if not start:
            start = datetime.utcnow() - timedelta(minutes=30)
        if not end:
            end = datetime.utcnow()
        
        must = []
        
        if start and end:
            must.append({
                "range": {
                    "@timestamp": {
                        "gte": start.isoformat(),
                        "lte": end.isoformat()
                    }
                }
            })
        
        if query:
            must.append(query)
        
        body = {
            "query": {
                "bool": {
                    "must": must if must else [{"match_all": {}}
                }
            },
            "sort": [{"@timestamp": "desc"}],
            "size": size
        }
        
        try:
            result = client.search(index=self.index_pattern, body=body)
            return [hit["_source"] for hit in result["hits"]["hits"]]
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def search_errors(
        self,
        start: datetime = None,
        end: datetime = None,
        level: str = "ERROR"
    ) -> list:
        query = {
            "term": {"level": level}
        }
        return self.search(query, start, end)

    def get_error_count(
        self,
        start: datetime = None,
        end: datetime = None
    ) -> int:
        results = self.search_errors(start, end)
        return len(results)

    def get_logs_by_trace_id(self, trace_id: str) -> list:
        query = {"term": {"trace_id": trace_id}}
        return self.search(query)

    def get_logs_by_service(
        self,
        service: str,
        start: datetime = None,
        end: datetime = None
    ) -> list:
        query = {"term": {"service.name": service}}
        return self.search(query, start, end)

    def get_recent_errors(self, minutes: int = 30) -> list:
        start = datetime.utcnow() - timedelta(minutes=minutes)
        end = datetime.utcnow()
        return self.search_errors(start, end)

    def get_service_errors(
        self,
        service: str,
        minutes: int = 30
    ) -> list:
        start = datetime.utcnow() - timedelta(minutes=minutes)
        end = datetime.utcnow()
        query = {
            "bool": {
                "must": [
                    {"term": {"service.name": service}},
                    {"term": {"level": "ERROR"}}
                ]
            }
        }
        return self.search(query, start, end)

    def check_index_exists(self, index_pattern: str = None) -> bool:
        client = self._get_client()
        if not client:
            return False
        
        pattern = index_pattern or self.index_pattern
        try:
            return client.indices.exists(index=pattern)
        except Exception:
            return False


@pytest.fixture(scope="session")
def kibana_client():
    return KibanaClient()


@pytest.fixture(scope="session")
def log_index_pattern():
    return "logs-*"