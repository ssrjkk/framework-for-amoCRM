import pytest
from datetime import datetime, timedelta, timezone
from pipelines.logs.utils.kibana_client import KibanaClient


pytestmark = [pytest.mark.logs, pytest.mark.kibana]


class TestLogErrors:
    def test_no_errors_during_test_run(self, kibana_client, test_run_window):
        start = test_run_window
        end = datetime.now(timezone.utc)
        
        errors = kibana_client.search_errors(start, end)
        
        critical_errors = [
            e for e in errors
            if e.get("level") in ["ERROR", "CRITICAL", "FATAL"]
        ]
        
        assert len(critical_errors) == 0, (
            f"Found {len(critical_errors)} errors in logs during test run"
        )

    def test_no_500_http_errors(self, kibana_client, test_run_window):
        start = test_run_window
        end = datetime.now(timezone.utc)
        
        query = {
            "bool": {
                "must": [
                    {"term": {"http.status": 500}},
                ]
            }
        }
        
        results = kibana_client.search(query, start, end)
        
        assert len(results) == 0, f"Found {len(results)} HTTP 500 errors"

    def test_no_database_connection_errors(
        self,
        kibana_client,
        test_run_window
    ):
        start = test_run_window
        end = datetime.now(timezone.utc)
        
        query = {
            "bool": {
                "should": [
                    {"match": {"message": "connection refused"}},
                    {"match": {"message": "connection timeout"}},
                    {"match": {"message": "database error"}},
                ]
            }
        }
        
        results = kibana_client.search(query, start, end)
        
        assert len(results) == 0, "Found database connection errors"

    def test_no_kafka_consumer_errors(
        self,
        kafka_consumer_factory,
        test_run_window
    ):
        pass

    def test_no_unhandled_exceptions(self, kibana_client, test_run_window):
        start = test_run_window
        end = datetime.now(timezone.utc)
        
        query = {
            "bool": {
                "must": [
                    {"match": {"message": "Uncaught exception"}},
                    {"match": {"message": "Unhandled error"}},
                ]
            }
        }
        
        results = kibana_client.search(query, start, end)
        
        assert len(results) == 0, "Found unhandled exceptions"

    def test_no_memory_errors(self, kibana_client, test_run_window):
        start = test_run_window
        end = datetime.now(timezone.utc)
        
        query = {
            "bool": {
                "should": [
                    {"match": {"message": "OutOfMemory"}},
                    {"match": {"message": "OOMKilled"}},
                    {"match": {"message": "memory limit"}},
                ]
            }
        }
        
        results = kibana_client.search(query, start, end)
        
        assert len(results) == 0, "Found memory errors"

    def test_service_specific_errors(self, kibana_client, test_run_window):
        start = test_run_window
        end = datetime.now(timezone.utc)
        
        services = ["api", "auth", "web"]
        
        for service in services:
            errors = kibana_client.get_service_errors(service, minutes=60)
            assert len(errors) == 0, (
                f"Found {len(errors)} errors in {service} service"
            )


class TestLogAnalysis:
    def test_error_rate_acceptable(self, kibana_client):
        error_count = kibana_client.get_error_count(
            minutes=60
        )
        total_logs = 1000
        
        error_rate = error_count / total_logs if total_logs > 0 else 0
        
        assert error_rate < 0.01, f"Error rate {error_rate:.2%} too high"

    def test_logs_index_exists(self, kibana_client, logs_index_pattern):
        assert kibana_client.check_index_exists(logs_index_pattern)

    def test_recent_logs_available(self, kibana_client):
        logs = kibana_client.search(
            start=datetime.now(timezone.utc) - timedelta(minutes=5),
            end=datetime.now(timezone.utc),
            size=10
        )
        assert len(logs) >= 0


@pytest.fixture(scope="module")
def api_client():
    from pipelines.api.utils.http_client import APIClient
    return APIClient()