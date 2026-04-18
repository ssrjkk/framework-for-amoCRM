import pytest
from pipelines.api.utils.schema_validator import validate_response


pytestmark = [pytest.mark.api, pytest.mark.contract]


class TestEntityCRUD:
    def test_create_entity_success(self, authenticated_client):
        resp = authenticated_client.post(
            "/api/entities",
            json={"name": "Test Entity", "description": "Test description"}
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert data["name"] == "Test Entity"
        validate_response(resp, "entity")

    def test_create_entity_missing_name(self, authenticated_client):
        resp = authenticated_client.post(
            "/api/entities",
            json={"description": "Test"}
        )
        assert resp.status_code in [400, 422]

    def test_create_entity_empty_name(self, authenticated_client):
        resp = authenticated_client.post(
            "/api/entities",
            json={"name": ""}
        )
        assert resp.status_code in [400, 422]

    def test_get_entity(self, authenticated_client, test_entity):
        if not test_entity:
            pytest.skip("Cannot create test entity")
        resp = authenticated_client.get(f"/api/entities/{test_entity}")
        assert resp.status_code == 200
        validate_response(resp, "entity")

    def test_get_entity_not_found(self, authenticated_client):
        resp = authenticated_client.get("/api/entities/999999999")
        assert resp.status_code == 404

    def test_update_entity(self, authenticated_client, test_entity):
        if not test_entity:
            pytest.skip("Cannot create test entity")
        resp = authenticated_client.put(
            f"/api/entities/{test_entity}",
            json={"name": "Updated Name"}
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"

    def test_delete_entity(self, authenticated_client, test_entity):
        if not test_entity:
            pytest.skip("Cannot create test entity")
        resp = authenticated_client.delete(f"/api/entities/{test_entity}")
        assert resp.status_code == 204
        
        get_resp = authenticated_client.get(f"/api/entities/{test_entity}")
        assert get_resp.status_code == 404

    def test_list_entities(self, authenticated_client):
        resp = authenticated_client.get("/api/entities")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        validate_response(resp, "pagination")


class TestContactCRUD:
    def test_create_contact(self, authenticated_client):
        resp = authenticated_client.post(
            "/api/contacts",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "company": "ACME Corp"
            }
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "John Doe"
        validate_response(resp, "contact")

    def test_get_contact(self, authenticated_client):
        create_resp = authenticated_client.post(
            "/api/contacts",
            json={"name": "Test Contact", "email": "test@test.com"}
        )
        contact_id = create_resp.json().get("id")
        
        resp = authenticated_client.get(f"/api/contacts/{contact_id}")
        assert resp.status_code == 200
        
        authenticated_client.delete(f"/api/contacts/{contact_id}")

    def test_update_contact(self, authenticated_client):
        create_resp = authenticated_client.post(
            "/api/contacts",
            json={"name": "Original Name", "email": "orig@test.com"}
        )
        contact_id = create_resp.json().get("id")
        
        resp = authenticated_client.patch(
            f"/api/contacts/{contact_id}",
            json={"name": "Updated Name"}
        )
        assert resp.status_code == 200
        
        authenticated_client.delete(f"/api/contacts/{contact_id}")

    def test_delete_contact(self, authenticated_client):
        create_resp = authenticated_client.post(
            "/api/contacts",
            json={"name": "To Delete", "email": "del@test.com"}
        )
        contact_id = create_resp.json().get("id")
        
        resp = authenticated_client.delete(f"/api/contacts/{contact_id}")
        assert resp.status_code == 204

    def test_list_contacts_with_filters(self, authenticated_client):
        resp = authenticated_client.get(
            "/api/contacts",
            params={"page": 1, "page_size": 10}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert data["page"] == 1
        assert data["page_size"] == 10


class TestLeadPipeline:
    def test_list_pipelines(self, authenticated_client):
        resp = authenticated_client.get("/api/pipelines")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data

    def test_get_pipeline_by_id(self, authenticated_client):
        list_resp = authenticated_client.get("/api/pipelines")
        pipelines = list_resp.json().get("items", [])
        
        if pipelines:
            pipeline_id = pipelines[0]["id"]
            resp = authenticated_client.get(f"/api/pipelines/{pipeline_id}")
            assert resp.status_code == 200

    def test_create_lead(self, authenticated_client):
        resp = authenticated_client.post(
            "/api/leads",
            json={
                "name": "New Lead",
                "price": 50000,
                "pipeline_id": 1
            }
        )
        assert resp.status_code in [201, 400]


class TestPagination:
    @pytest.mark.parametrize("page_size", [10, 25, 50, 100])
    def test_pagination_page_sizes(self, authenticated_client, page_size):
        resp = authenticated_client.get(
            "/api/entities",
            params={"page": 1, "page_size": page_size}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) <= page_size
        assert data["page_size"] == page_size

    def test_pagination_out_of_range(self, authenticated_client):
        resp = authenticated_client.get(
            "/api/entities",
            params={"page": 999999, "page_size": 10}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 0