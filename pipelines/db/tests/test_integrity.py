import pytest
from pipelines.db.utils.db_client import DBClient


pytestmark = [pytest.mark.db, pytest.mark.integrity]


class TestDataIntegrity:
    def test_no_nulls_in_required_entity_fields(self, db_client):
        result = db_client.execute(
            "SELECT COUNT(*) as cnt FROM entities WHERE name IS NULL OR status IS NULL"
        )
        assert result[0]["cnt"] == 0, "Found entities with NULL in required fields"

    def test_no_duplicate_entity_ids(self, db_client):
        result = db_client.execute("""
            SELECT id, COUNT(*) as cnt 
            FROM entities 
            GROUP BY id 
            HAVING COUNT(*) > 1
        """)
        assert len(result) == 0, "Found duplicate entity IDs"

    def test_contacts_email_unique(self, db_client):
        result = db_client.execute("""
            SELECT email, COUNT(*) as cnt 
            FROM contacts 
            WHERE email IS NOT NULL
            GROUP BY email 
            HAVING COUNT(*) > 1
        """)
        assert len(result) == 0, "Found duplicate contact emails"

    def test_leads_foreign_keys_valid(self, db_client):
        result = db_client.execute("""
            SELECT l.id 
            FROM leads l 
            LEFT JOIN pipelines p ON l.pipeline_id = p.id 
            WHERE l.pipeline_id IS NOT NULL AND p.id IS NULL
        """)
        assert len(result) == 0, "Found leads with invalid pipeline_id"

    def test_timestamps_not_in_future(self, db_client):
        result = db_client.execute("""
            SELECT COUNT(*) as cnt 
            FROM entities 
            WHERE created_at > NOW() OR updated_at > NOW()
        """)
        assert result[0]["cnt"] == 0, "Found entities with future timestamps"

    def test_no_negative_prices_in_leads(self, db_client):
        result = db_client.execute("""
            SELECT COUNT(*) as cnt 
            FROM leads 
            WHERE price < 0
        """)
        assert result[0]["cnt"] == 0, "Found leads with negative price"

    def test_entity_name_length_valid(self, db_client):
        result = db_client.execute("""
            SELECT COUNT(*) as cnt 
            FROM entities 
            WHERE LENGTH(name) > 255
        """)
        assert result[0]["cnt"] == 0, "Found entities with name > 255 chars"

    def test_contacts_name_not_empty(self, db_client):
        result = db_client.execute("""
            SELECT COUNT(*) as cnt 
            FROM contacts 
            WHERE name IS NULL OR LENGTH(TRIM(name)) = 0
        """)
        assert len(result) == 0 or result[0]["cnt"] == 0, "Found contacts with empty name"


class TestConstraints:
    def test_check_total_greater_than_zero(self, db_client):
        result = db_client.execute("""
            SELECT COUNT(*) as cnt 
            FROM entities 
            WHERE total < 0
        """)
        assert result[0]["cnt"] == 0

    def test_pipeline_stages_order_valid(self, db_client):
        result = db_client.execute("""
            SELECT id, sort 
            FROM pipeline_stages 
            WHERE sort < 0
        """)
        assert len(result) == 0, "Found pipeline stages with negative sort order"

    def test_user_unique_constraint(self, db_client):
        result = db_client.execute("""
            SELECT email, COUNT(*) as cnt 
            FROM users 
            WHERE email IS NOT NULL
            GROUP BY email 
            HAVING COUNT(*) > 1
        """)
        assert len(result) == 0, "Found duplicate user emails"


class TestIndexes:
    def test_entities_have_primary_key(self, db_client):
        result = db_client.execute("""
            SELECT COUNT(*) as cnt 
            FROM information_schema.table_constraints 
            WHERE table_name = 'entities' 
            AND constraint_type = 'PRIMARY KEY'
        """)
        assert result[0]["cnt"] >= 1, "Entities table has no primary key"

    def test_contacts_have_indexes(self, db_client):
        result = db_client.execute("""
            SELECT COUNT(*) as cnt 
            FROM pg_indexes 
            WHERE tablename = 'contacts'
        """)
        assert result[0]["cnt"] >= 1, "Contacts table has no indexes"

    def test_leads_pipeline_id_indexed(self, db_client):
        result = db_client.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'leads' 
            AND indexdef LIKE '%pipeline_id%'
        """)
        assert len(result) >= 1, "leads.pipeline_id is not indexed"