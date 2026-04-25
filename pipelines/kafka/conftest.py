import pytest
from pipelines.kafka.utils.kafka_client import (
    KafkaProducerClient, KafkaConsumerClient
)
from config.settings import KAFKA_BROKERS
import os
import time


def pytest_configure(config):
    config.addinivalue_line("markers", "kafka: Kafka event tests")
    config.addinivalue_line("markers", "async: Async flow tests")
    config.addinivalue_line("markers", "dlq: Dead letter queue tests")


@pytest.fixture(scope="session")
def kafka_brokers():
    brokers = os.getenv("KAFKA_BROKERS", "")
    if not brokers or brokers == "localhost:9092":
        if not KAFKA_BROKERS:
            pytest.skip("KAFKA_BROKERS not configured - using mock mode")
        return KAFKA_BROKERS
    return brokers


@pytest.fixture(scope="session")
def kafka_producer():
    brokers = os.getenv("KAFKA_BROKERS", "") or KAFKA_BROKERS
    if not brokers:
        pytest.skip("Kafka not available - mock mode")
    try:
        producer = KafkaProducerClient()
        yield producer
        producer.close()
    except Exception as e:
        pytest.skip(f"Kafka not available: {e}")


@pytest.fixture(scope="function")
def kafka_consumer_factory():
    brokers = os.getenv("KAFKA_BROKERS", "") or KAFKA_BROKERS
    if not brokers:
        pytest.skip("Kafka not available - mock mode")
    
    def create_consumer(topic: str, group_id: str = None):
        try:
            return KafkaConsumerClient(
                topic=topic,
                group_id=group_id or f"test-{int(time.time() * 1000)}"
            )
        except Exception:
            pytest.skip(f"Kafka not available for topic: {topic}")
    
    return create_consumer


@pytest.fixture(scope="function")
def event_consumer(kafka_consumer_factory):
    consumer = kafka_consumer_factory("entity.created.events")
    yield consumer
    consumer.close()


@pytest.fixture(scope="function")
def dlq_consumer(kafka_consumer_factory):
    consumer = kafka_consumer_factory("dead-letter-queue")
    yield consumer
    consumer.close()


@pytest.fixture(scope="session")
def kafka_topics():
    return {
        "entity_created": "entity.created.events",
        "entity_updated": "entity.updated.events",
        "entity_deleted": "entity.deleted.events",
        "contact_created": "contact.created.events",
        "lead_created": "lead.created.events",
        "notification": "notification.events",
        "dlq": "dead-letter-queue",
    }


@pytest.fixture(scope="session")
def event_schemas():
    return {
        "entity.created": {
            "event_type": "entity.created",
            "payload": {"id": int, "name": str},
            "timestamp": str,
            "version": "1.0",
        },
        "entity.updated": {
            "event_type": "entity.updated",
            "payload": {"id": int, "name": str, "updated_at": str},
            "timestamp": str,
            "version": "1.0",
        },
        "entity.deleted": {
            "event_type": "entity.deleted",
            "payload": {"id": int},
            "timestamp": str,
            "version": "1.0",
        },
    }