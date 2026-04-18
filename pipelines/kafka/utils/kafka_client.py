import json
import logging
from kafka import KafkaProducer as KafkaProducerClient
from kafka import KafkaConsumer as KafkaConsumerClient
from kafka.errors import NoBrokersAvailable
from config.settings import KAFKA_BROKERS
from typing import Callable, Optional, Any
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KafkaProducerClient:
    def __init__(self, brokers: list = None, serializer: str = "json"):
        self.brokers = brokers or KAFKA_BROKERS
        self.serializer = serializer
        self._producer = None

    def _get_producer(self):
        if not self._producer:
            self._producer = KafkaProducerClient(
                bootstrap_servers=self.brokers,
                value_serializer=self._serialize,
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",
                retries=3,
            )
        return self._producer

    def _serialize(self, value):
        if self.serializer == "json":
            return json.dumps(value).encode("utf-8")
        return value

    def send(self, topic: str, value: dict, key: str = None):
        logger.info(f"Sending to {topic}: {value}")
        future = self._get_producer().send(topic, value=value, key=key)
        return future.get(timeout=10)

    def send_async(self, topic: str, value: dict, key: str = None):
        return self._get_producer().send(topic, value=value, key=key)

    def flush(self):
        if self._producer:
            self._producer.flush()

    def close(self):
        if self._producer:
            self._producer.close()


class KafkaConsumerClient:
    def __init__(
        self,
        topic: str,
        brokers: list = None,
        group_id: str = "test-consumer",
        auto_offset_reset: str = "latest",
        deserializer: str = "json",
    ):
        self.topic = topic
        self.brokers = brokers or KAFKA_BROKERS
        self.group_id = group_id
        self.deserializer = deserializer
        self._consumer = None
        self.auto_offset_reset = auto_offset_reset

    def _get_consumer(self):
        if not self._consumer:
            self._consumer = KafkaConsumerClient(
                self.topic,
                bootstrap_servers=self.brokers,
                group_id=self.group_id,
                auto_offset_reset=self.auto_offset_reset,
                enable_auto_commit=True,
                value_deserializer=self._deserialize,
            )
        return self._consumer

    def _deserialize(self, value):
        if self.deserializer == "json":
            return json.loads(value.decode("utf-8"))
        return value

    def __iter__(self):
        return self._get_consumer().__iter__()

    def consume(self, timeout_sec: int = 10):
        messages = []
        start_time = time.time()
        for msg in self._get_consumer():
            if time.time() - start_time > timeout_sec:
                break
            messages.append(msg.value)
        return messages

    def wait_for(
        self, predicate: Callable[[dict], bool], timeout_sec: int = 30
    ) -> Optional[dict]:
        start_time = time.time()
        for msg in self._get_consumer():
            if predicate(msg.value):
                logger.info(f"Found message: {msg.value}")
                return msg.value
            if time.time() - start_time > timeout_sec:
                logger.warning("Timeout waiting for message")
                return None
        return None

    def seek_to_beginning(self):
        self._get_consumer().seek_to_beginning()

    def close(self):
        if self._consumer:
            self._consumer.close()


@pytest.fixture(scope="session")
def kafka_producer():
    producer = KafkaProducerClient()
    yield producer
    producer.close()


@pytest.fixture(scope="function")
def kafka_consumer():
    return None


@pytest.fixture(scope="session")
def kafka_topics():
    return {
        "entity_created": "entity.created.events",
        "entity_updated": "entity.updated.events",
        "entity_deleted": "entity.deleted.events",
        "contact_created": "contact.created.events",
        "lead_created": "lead.created.events",
        "dlq": "dead-letter-queue",
    }