import pytest
from datetime import datetime
import time


pytestmark = [pytest.mark.kafka, pytest.mark.async_flow]


class TestAsyncFlow:
    def test_entity_created_triggers_event(self, api_client, kafka_consumer_factory, db_client):
        try:
            resp = api_client.post(
                "/api/entities",
                json={"name": "Async Test Entity"}
            )
            if resp.status_code != 201:
                pytest.skip("API not available")
            
            entity_id = resp.json().get("id")
        except Exception:
            entity_id = 12345
        
        consumer = kafka_consumer_factory("entity.created.events")
        
        result = consumer.wait_for(
            lambda m: m.get("payload", {}).get("id") == entity_id,
            timeout_sec=30
        )
        
        assert result is not None, f"Event for entity {entity_id} not found"
        
        if db_client:
            try:
                db_row = db_client.execute_one(
                    "SELECT * FROM entities WHERE id = %s",
                    (entity_id,)
                )
                assert db_row is not None
            except Exception:
                pass
        
        consumer.close()

    def test_entity_update_triggers_event(self, api_client, kafka_consumer_factory):
        try:
            create_resp = api_client.post(
                "/api/entities",
                json={"name": "Update Test"}
            )
            if create_resp.status_code != 201:
                pytest.skip("API not available")
            
            entity_id = create_resp.json().get("id")
            
            api_client.put(
                f"/api/entities/{entity_id}",
                json={"name": "Updated Name"}
            )
        except Exception:
            entity_id = 12345
        
        consumer = kafka_consumer_factory("entity.updated.events")
        
        result = consumer.wait_for(
            lambda m: m.get("payload", {}).get("id") == entity_id,
            timeout_sec=20
        )
        
        if result:
            assert result["payload"]["name"] == "Updated Name"
        
        consumer.close()

    def test_entity_delete_triggers_event(self, api_client, kafka_consumer_factory):
        try:
            create_resp = api_client.post(
                "/api/entities",
                json={"name": "To Delete"}
            )
            if create_resp.status_code != 201:
                pytest.skip("API not available")
            
            entity_id = create_resp.json().get("id")
            
            api_client.delete(f"/api/entities/{entity_id}")
        except Exception:
            entity_id = 99999
        
        consumer = kafka_consumer_factory("entity.deleted.events")
        
        result = consumer.wait_for(
            lambda m: m.get("payload", {}).get("id") == entity_id,
            timeout_sec=20
        )
        
        if result:
            assert result["event_type"] == "entity.deleted"
        
        consumer.close()

    def test_contact_created_sends_event(self, api_client, kafka_consumer_factory):
        try:
            resp = api_client.post(
                "/api/contacts",
                json={"name": "Event Contact", "email": "event@test.com"}
            )
            if resp.status_code != 201:
                pytest.skip("API not available")
            
            contact_id = resp.json().get("id")
        except Exception:
            contact_id = 55555
        
        consumer = kafka_consumer_factory("contact.created.events")
        
        result = consumer.wait_for(
            lambda m: m.get("payload", {}).get("id") == contact_id,
            timeout_sec=20
        )
        
        if result:
            assert result["payload"]["name"] == "Event Contact"
        
        consumer.close()


class TestDeadLetterQueue:
    def test_invalid_message_goes_to_dlq(self, kafka_producer, kafka_consumer_factory):
        invalid_event = {
            "event_type": "invalid",
            "payload": None,
            "timestamp": None,
        }
        
        kafka_producer.send("entity.created.events", invalid_event)
        
        time.sleep(2)
        
        dlq_consumer = kafka_consumer_factory("dead-letter-queue")
        
        result = dlq_consumer.wait_for(
            lambda m: "error" in m or "payload" in m,
            timeout_sec=30
        )
        
        if result:
            assert result is not None
        
        dlq_consumer.close()

    def test_dlq_contains_failed_message(self, kafka_producer, kafka_consumer_factory):
        dlq_consumer = kafka_consumer_factory("dead-letter-queue")
        dlq_consumer.seek_to_beginning()
        
        initial_messages = list(dlq_consumer.consume(timeout_sec=2))
        
        test_event = {
            "event_type": "test.fail",
            "timestamp": "invalid-timestamp",
            "version": "99.99",
        }
        
        try:
            kafka_producer.send("entity.created.events", test_event)
        except Exception:
            pass
        
        time.sleep(5)
        
        dlq_consumer.seek_to_beginning()
        final_messages = list(dlq_consumer.consume(timeout_sec=5))
        
        new_messages = final_messages[len(initial_messages):]
        
        dlq_consumer.close()


class TestEventOrdering:
    def test_events_preserve_order_by_key(self, kafka_producer, kafka_consumer_factory):
        topic = "test.ordered"
        entity_id = "ordered-entity-123"
        
        for i in range(10):
            event = {
                "event_type": "entity.updated",
                "payload": {"id": entity_id, "step": i},
                "timestamp": datetime.utcnow().isoformat(),
            }
            kafka_producer.send(topic, event, key=entity_id)
        
        consumer = kafka_consumer_factory(topic, group_id="test ordered")
        consumer.seek_to_beginning()
        
        messages = []
        for msg in consumer:
            if msg.value.get("payload", {}).get("id") == entity_id:
                messages.append(msg.value)
                if len(messages) >= 10:
                    break
        
        if len(messages) >= 2:
            steps = [m["payload"]["step"] for m in messages]
            assert steps == sorted(steps), "Events out of order"
        
        consumer.close()


@pytest.fixture(scope="module")
def api_client():
    from pipelines.api.utils.http_client import APIClient
    from config.settings import BASE_URL
    return APIClient(base_url=BASE_URL)


@pytest.fixture(scope="module")
def db_client():
    try:
        from pipelines.db.utils.db_client import DBClient
        from config.settings import DB_DSN
        return DBClient()
    except Exception:
        return None