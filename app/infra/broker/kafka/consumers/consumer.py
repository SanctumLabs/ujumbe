from typing import List, Union, Optional
from dataclasses import dataclass
from confluent_kafka import Consumer, OFFSET_BEGINNING, TopicPartition, Message
from app.infra.logger import log as logging


@dataclass
class KafkaConsumerParams:
    """
    bootstrap_servers: Kafka bootstrap servers to listen on
    topic: Either a single topic or a list of topics for this consumer to listen to
    group_id: Group ID this consumer belongs to
    """
    bootstrap_servers: str
    topic: Union[str, List[str]]
    group_id: str

    @property
    def topics(self) -> Union[str, List[str]]:
        if isinstance(self.topic, str):
            return [self.topic]
        else:
            return self.topic


class KafkaConsumer:
    def __init__(self, params: KafkaConsumerParams):
        """
        Creates an instance of a Kafka consumer
        Args:
            params: KafkaConsumerParams to initialize a Kafka Consumer
        """
        conf = {
            "bootstrap.servers": params.bootstrap_servers,
            "group.id": params.group_id
            # "security.protocol": config.kafka.security_protocol,
            # "sasl.mechanisms": config.kafka.sasl_mechanisms,
            # "sasl.username": config.kafka.sasl_password,
            # "sasl.password": config.kafka.sasl_password,
        }
        self._consumer = Consumer(conf)
        self._consumer.subscribe(topics=params.topics)

    def consume(self, timeout: Optional[float] = 1.0) -> Optional[Message]:
        try:
            message = self._consumer.poll(timeout=timeout)
            return message
        except Exception as exc:
            logging.error(f"failed to consume messages", exc)
            raise exc

    def close(self):
        try:
            self._consumer.close()
        except Exception as exc:
            logging.error(f"failed to close consumer", exc)

    @staticmethod
    def reset_offset(consumer: Consumer, partitions: List[TopicPartition]):
        """
        Callback to reset the offset on a consumer
        Args:
            consumer: Consumer application
            partitions: list of topic partitions
        """
        logging.warning(f"Resetting offset on consumer for partitions: {partitions} ...")
        for p in partitions:
            p.offset = OFFSET_BEGINNING
        consumer.assign(partitions)
