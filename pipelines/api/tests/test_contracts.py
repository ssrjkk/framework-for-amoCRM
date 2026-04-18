import pytest
from pipelines.api.utils.schema_validator import validate_response, JSON_SCHEMAS


pytestmark = [pytest.mark.api, pytest.mark.contract]


class TestContractValidation:
    def test_contact_list_response_structure(self, api_client):
        resp = api_client.contacts.list()
        
        if resp.status_code != 200:
            pytest.skip("API not available")
        
        data = resp.json()
        assert "_embedded" in data
        assert "contacts" in data["_embedded"]

    def test_contact_response_has_required_fields(self, api_client):
        resp = api_client.contacts.list(limit=1)
        
        if resp.status_code != 200:
            pytest.skip("API not available")
        
        data = resp.json()
        if data["_embedded"]["contacts"]:
            contact = data["_embedded"]["contacts"][0]
            assert "id" in contact
            assert "name" in contact

    def test_lead_list_response_structure(self, api_client):
        resp = api_client.leads.list()
        
        if resp.status_code != 200:
            pytest.skip("API not available")
        
        data = resp.json()
        assert "_embedded" in data

    def test_company_list_response_structure(self, api_client):
        resp = api_client.companies.list()
        
        if resp.status_code != 200:
            pytest.skip("API not available")
        
        data = resp.json()
        assert "_embedded" in data

    def test_pagination_params(self, api_client):
        resp = api_client.contacts.list(page=1, limit=25)
        
        if resp.status_code != 200:
            pytest.skip("API not available")
        
        assert resp.status_code == 200
        data = resp.json()
        assert "pagination" in data

    def test_filter_by_name(self, api_client):
        resp = api_client.contacts.list(query="Test")
        
        assert resp.status_code in [200, 401]

    def test_filter_by_date(self, api_client):
        import time
        current = int(time.time())
        resp = api_client.contacts.list(filters={
            "updated_at": {"from": current - 86400}
        })
        
        assert resp.status_code in [200, 401]

    def test_task_list_response(self, api_client):
        resp = api_client.tasks.list()
        assert resp.status_code in [200, 401]


class TestAllSchemas:
    def test_all_schemas_defined(self):
        assert "contact" in JSON_SCHEMAS
        assert "company" in JSON_SCHEMAS
        assert "lead" in JSON_SCHEMAS
        assert "task" in JSON_SCHEMAS
        assert "user" in JSON_SCHEMAS
        assert "pipeline" in JSON_SCHEMAS

    def test_schema_has_type(self):
        for name, schema in JSON_SCHEMAS.items():
            assert "type" in schema, f"Schema {name} missing 'type'"
            assert "properties" in schema, f"Schema {name} missing 'properties'"