import pytest
import json
from pipelines.api.utils.schema_validator import (
    validate, validate_response, JSON_SCHEMAS
)
from pipelines.api.utils.http_client import APIClient


pytestmark = [pytest.mark.api, pytest.mark.contract]


class TestContractValidation:
    def test_auth_login_contract(self, api_client):
        resp = api_client.auth_login("test@example.com", "TestPass123!")
        assert resp.status_code == 200
        assert validate_response(resp, "auth_login")

    def test_auth_refresh_contract(self, api_client):
        login_resp = api_client.auth_login("test@example.com", "TestPass123!")
        refresh_token = login_resp.json().get("refresh_token")
        
        resp = api_client.auth_refresh(refresh_token)
        assert resp.status_code == 200
        assert validate_response(resp, "auth_refresh")

    def test_entity_contract(self, authenticated_client):
        resp = authenticated_client.post(
            "/api/entities",
            json={"name": "Contract Test"}
        )
        assert resp.status_code == 201
        assert validate_response(resp, "entity")

    def test_contact_contract(self, authenticated_client):
        resp = authenticated_client.post(
            "/api/contacts",
            json={"name": "Contract Test", "email": "test@test.com"}
        )
        assert resp.status_code == 201
        assert validate_response(resp, "contact")

    def test_error_response_contract(self, api_client):
        resp = api_client.get("/api/nonexistent-endpoint")
        assert resp.status_code >= 400
        assert validate_response(resp, "error")

    def test_pagination_contract(self, authenticated_client):
        resp = authenticated_client.get("/api/entities")
        assert resp.status_code == 200
        assert validate_response(resp, "pagination")


class TestContractNegative:
    def test_invalid_email_format(self, api_client):
        resp = api_client.auth_login("not-an-email", "password")
        assert resp.status_code in [400, 401, 422]

    def test_entity_name_too_long(self, authenticated_client):
        long_name = "x" * 1000
        resp = authenticated_client.post(
            "/api/entities",
            json={"name": long_name}
        )
        assert resp.status_code in [400, 422]

    def test_invalid_contact_email(self, authenticated_client):
        resp = authenticated_client.post(
            "/api/contacts",
            json={"name": "Test", "email": "invalid-email"}
        )
        assert resp.status_code in [400, 422]

    def test_negative_price(self, authenticated_client):
        resp = authenticated_client.post(
            "/api/leads",
            json={"name": "Test", "price": -100}
        )
        assert resp.status_code in [400, 422]


class TestContractEdgeCases:
    def test_empty_required_field(self, authenticated_client):
        resp = authenticated_client.post("/api/entities", json={})
        assert resp.status_code in [400, 422]

    def test_null_required_field(self, authenticated_client):
        resp = authenticated_client.post(
            "/api/entities",
            json={"name": None}
        )
        assert resp.status_code in [400, 422]

    def test_additional_properties_in_request(self, authenticated_client):
        resp = authenticated_client.post(
            "/api/entities",
            json={"name": "Test", "extra_field": "should be ignored"}
        )
        assert resp.status_code in [200, 201, 400, 422]

    def test_valid_pagination_with_zero_page_size(self, authenticated_client):
        resp = authenticated_client.get(
            "/api/entities",
            params={"page": 1, "page_size": 0}
        )
        assert resp.status_code in [200, 400]


class TestFullContractSuite:
    @pytest.mark.parametrize("schema_name", list(JSON_SCHEMAS.keys()))
    def test_all_schemas_exist(self, schema_name):
        assert schema_name in JSON_SCHEMAS
        assert JSON_SCHEMAS[schema_name] is not None

    def test_schema_structure(self):
        for schema_name, schema in JSON_SCHEMAS.items():
            assert "type" in schema, f"Missing 'type' in {schema_name}"
            assert "properties" in schema, f"Missing 'properties' in {schema_name}"