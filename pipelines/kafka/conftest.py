import pytest
from pipelines.kafka.utils.kafka_client import (
    KafkaProducerClient, KafkaConsumerClient
)
from config.settings import KAFKA_BROKERS
import time


def pytest_configure(config):
    config.addinivalue_line("markers", "kafka: Kafka event tests")
    config.addinivalue_line("markers", "async: Async flow tests")
    config.addinivalue_line("markers", "dlq: Dead letter queue tests")


@pytest.fixture(scope="session")
def kafka_brokers():
    return KAFKA_BROKERS


@pytest.fixture(scope="session")
def kafka_producer():
    producer = KafkaProducerClient()
    yield producer
    producer.close()


@pytest.fixture(scope="function")
def kafka_consumer_factory():
    def create_consumer(topic: str, group_id: str = None):
        return KafkaConsumerClient(
            topic=topic,
            group_id=group_id or f"test-{int(time.time() * 1000)}"
        )
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