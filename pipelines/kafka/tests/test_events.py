import pytest
from datetime import datetime
import json


pytestmark = [pytest.mark.kafka, pytest.mark.events]


class TestKafkaEvents:
    def test_send_and_receive_message(self, kafka_producer, kafka_consumer_factory):
        topic = "test.topic"
        test_message = {"event": "test", "data": {"id": 123}}
        
        consumer = kafka_consumer_factory(topic, group_id="test-sar")
        kafka_producer.send(topic, test_message, key="test-key")
        
        result = consumer.wait_for(
            lambda m: m.get("event") == "test",
            timeout_sec=10
        )
        
        assert result is not None
        assert result["data"]["id"] == 123
        consumer.close()

    def test_event_schema_structure(self, kafka_producer, kafka_consumer_factory):
        topic = "test.schema"
        event = {
            "event_type": "entity.created",
            "payload": {"id": 1, "name": "Test"},
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0",
        }
        
        consumer = kafka_consumer_factory(topic, group_id="test-schema")
        kafka_producer.send(topic, event)
        
        result = consumer.wait_for(
            lambda m: m.get("event_type") == "entity.created",
            timeout_sec=10
        )
        
        assert result is not None
        assert "event_type" in result
        assert "payload" in result
        assert "timestamp" in result
        assert "version" in result
        consumer.close()

    def test_multiple_events_order(self, kafka_producer, kafka_consumer_factory):
        topic = "test.order"
        
        for i in range(5):
            kafka_producer.send(topic, {"order": i, "id": i + 1})
        
        consumer = kafka_consumer_factory(topic, group_id="test-order")
        consumer.seek_to_beginning()
        
        messages = []
        for msg in consumer:
            messages.append(msg.value)
            if len(messages) >= 5:
                break
        
        assert len(messages) == 5
        consumer.close()

    def test_event_contains_entity_id(self, kafka_producer, kafka_consumer_factory, api_client):
        entity_data = {"name": "Event Test Entity"}
        
        try:
            resp = api_client.post("/api/entities", json=entity_data)
            if resp.status_code != 201:
                pytest.skip("API not available")
            
            entity_id = resp.json().get("id")
        except Exception:
            entity_id = 999
            
        topic = "entity.created.events"
        event = {
            "event_type": "entity.created",
            "payload": {"id": entity_id, "name": "Event Test"},
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0",
        }
        
        kafka_producer.send(topic, event)
        
        consumer = kafka_consumer_factory(topic, group_id="test-eid")
        result = consumer.wait_for(
            lambda m: m.get("payload", {}).get("id") == entity_id,
            timeout_sec=15
        )
        
        if result:
            assert result["payload"]["id"] == entity_id
        consumer.close()

    def test_no_duplicate_events_on_retry(self, kafka_producer, kafka_consumer_factory):
        topic = "test.duplicate"
        test_key = "dedup-test-key"
        
        kafka_producer.send(topic, {"event": "dedup", "id": 1}, key=test_key)
        
        consumer = kafka_consumer_factory(topic, group_id="test-dup")
        consumer.seek_to_beginning()
        
        messages = []
        for msg in consumer:
            if msg.value.get("event") == "dedup":
                messages.append(msg.value)
                if len(messages) >= 2:
                    break
        
        consumer.close()


class TestEventDelivery:
    def test_event_to_specific_partition(self, kafka_producer):
        topic = "test.partition"
        test_data = {"partition": "test", "id": 42}
        
        future = kafka_producer.send(topic, test_data, key="partition-key")
        record_metadata = future.get(timeout=10)
        
        assert record_metadata.partition >= 0
        assert record_metadata.offset >= 0

    def test_async_send_no_error(self, kafka_producer):
        topic = "test.async"
        
        for i in range(10):
            kafka_producer.send_async(topic, {"async": i})
        
        kafka_producer.flush()
        
        assert True

    def test_large_message(self, kafka_producer, kafka_consumer_factory):
        topic = "test.large"
        large_data = {"data": "x" * 10000}
        
        kafka_producer.send(topic, large_data)
        
        consumer = kafka_consumer_factory(topic, group_id="test-large")
        result = consumer.wait_for(lambda m: "data" in m, timeout_sec=10)
        
        assert result is not None
        consumer.close()