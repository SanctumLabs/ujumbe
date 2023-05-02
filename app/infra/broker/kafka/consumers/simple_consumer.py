"""
Contains Kafka simple consumer
"""
from typing import List, Optional
from confluent_kafka import Consumer, OFFSET_BEGINNING, TopicPartition, Message
from app.infra.logger import log as logging
from . import KafkaConsumer
from ..config import KafkaConsumerConfig


class KafkaSimpleConsumer(KafkaConsumer):
    def __init__(self, params: KafkaConsumerConfig):
        """
        Creates an instance of a Kafka consumer
        Args:
            params: KafkaConsumerParams to initialize a Kafka Consumer
        """
        super().__init__(params)

    def consume(self, timeout: Optional[float] = 1.0) -> Optional[Message]:
        try:
            message = self._consumer.poll(timeout=timeout)
            return message
        except Exception as exc:
            logging.error(f"failed to consume messages", exc)
            raise exc

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
