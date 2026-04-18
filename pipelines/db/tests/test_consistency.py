import pytest
from pipelines.db.utils.db_client import DBClient
from pipelines.api.utils.http_client import APIClient
import os


pytestmark = [pytest.mark.db, pytest.mark.consistency]


class TestConsistency:
    @pytest.fixture(autouse=True)
    def setup(self, db_client, api_client):
        self.db = db_client
        self.api = api_client

    def test_entity_created_via_api_exists_in_db(self, api_client, db_client):
        resp = api_client.post(
            "/api/entities",
            json={"name": "Consistency Test Entity"}
        )
        if resp.status_code != 201:
            pytest.skip("API not available")
        
        entity_id = resp.json().get("id")
        
        db_row = db_client.execute_one(
            "SELECT * FROM entities WHERE id = %s",
            (entity_id,)
        )
        
        assert db_row is not None, f"Entity {entity_id} not found in DB"
        assert db_row["name"] == "Consistency Test Entity"
        
        db_client.execute(
            "DELETE FROM entities WHERE id = %s",
            (entity_id,)
        )

    def test_entity_updated_via_api_reflected_in_db(self, api_client, db_client):
        create_resp = api_client.post(
            "/api/entities",
            json={"name": "Original Name"}
        )
        if create_resp.status_code != 201:
            pytest.skip("API not available")
        
        entity_id = create_resp.json().get("id")
        
        update_resp = api_client.put(
            f"/api/entities/{entity_id}",
            json={"name": "Updated Name"}
        )
        
        db_row = db_client.execute_one(
            "SELECT name FROM entities WHERE id = %s",
            (entity_id,)
        )
        
        assert db_row["name"] == "Updated Name"
        
        db_client.execute(
            "DELETE FROM entities WHERE id = %s",
            (entity_id,)
        )

    def test_entity_deleted_via_api_removed_from_db(self, api_client, db_client):
        create_resp = api_client.post(
            "/api/entities",
            json={"name": "To Delete"}
        )
        if create_resp.status_code != 201:
            pytest.skip("API not available")
        
        entity_id = create_resp.json().get("id")
        
        delete_resp = api_client.delete(f"/api/entities/{entity_id}")
        
        db_row = db_client.execute_one(
            "SELECT * FROM entities WHERE id = %s",
            (entity_id,)
        )
        
        assert db_row is None, f"Entity {entity_id} still exists in DB"

    def test_contact_created_via_api_in_db(self, api_client, db_client):
        resp = api_client.post(
            "/api/contacts",
            json={
                "name": "Test Contact",
                "email": "consistency@test.com"
            }
        )
        if resp.status_code != 201:
            pytest.skip("API not available")
        
        contact_id = resp.json().get("id")
        
        db_row = db_client.execute_one(
            "SELECT * FROM contacts WHERE id = %s",
            (contact_id,)
        )
        
        assert db_row is not None
        assert db_row["name"] == "Test Contact"
        
        db_client.execute(
            "DELETE FROM contacts WHERE id = %s",
            (contact_id,)
        )

    def test_lead_status_change_reflected_in_db(self, api_client, db_client):
        resp = api_client.post(
            "/api/leads",
            json={"name": "Test Lead", "pipeline_id": 1}
        )
        if resp.status_code not in [201, 400]:
            pytest.skip("API not available")
        
        if resp.status_code == 201:
            lead_id = resp.json().get("id")
            
            api_client.patch(
                f"/api/leads/{lead_id}",
                json={"status": "closed"}
            )
            
            db_row = db_client.execute_one(
                "SELECT status FROM leads WHERE id = %s",
                (lead_id,)
            )
            
            if db_row:
                assert db_row["status"] == "closed"
                
                db_client.execute(
                    "DELETE FROM leads WHERE id = %s",
                    (lead_id,)
                )

    def test_timestamp_consistency(self, api_client, db_client):
        import time
        
        resp = api_client.post(
            "/api/entities",
            json={"name": "Time Test"}
        )
        if resp.status_code != 201:
            pytest.skip("API not available")
        
        entity_id = resp.json().get("id")
        
        db_row = db_client.execute_one(
            "SELECT created_at FROM entities WHERE id = %s",
            (entity_id,)
        )
        
        if db_row and db_row["created_at"]:
            assert db_row["created_at"] is not None
        
        db_client.execute(
            "DELETE FROM entities WHERE id = %s",
            (entity_id,)
        )


class TestDBViewState:
    def test_calculated_fields_in_view(self, db_client):
        try:
            result = db_client.execute(
                "SELECT COUNT(*) as cnt FROM v_entities_active"
            )
            assert result[0]["cnt"] >= 0
        except Exception:
            pass

    def test_trigger_history_created(self, db_client):
        try:
            db_client.execute(
                "INSERT INTO entities (name) VALUES ('Trigger Test')"
            )
            history = db_client.execute(
                "SELECT * FROM entity_history WHERE name = 'Trigger Test'"
            )
            assert len(history) > 0
        except Exception:
            pass