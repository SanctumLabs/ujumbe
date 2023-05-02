"""
Contains abstract kafka consumer that can be subclasses by consumer classes
"""
from typing import Optional, List, Any
import socket
from abc import abstractmethod, ABCMeta
from confluent_kafka import Consumer, OFFSET_BEGINNING, TopicPartition
from app.infra.logger import log as logging
from app.infra.logger import log as logger
from ..config import KafkaConsumerConfig


class KafkaConsumer(metaclass=ABCMeta):
    """
    Abstract Kafka consumer
    """

    def __init__(self, config: KafkaConsumerConfig):
        """
        Initializes a Kafka Consumer
        Args:
            config (KafkaConsumerConfig): kafka consumer config
        """
        security_config = config.security
        self.conf = {
            "bootstrap.servers": config.bootstrap_servers,
            "group.id": config.group_id,
            "client.id": config.client_id or socket.gethostname(),
            'auto.offset.reset': config.auto_offset_reset
        }

        if security_config:
            if security_config.security_protocol:
                self.conf["security.protocol"] = security_config.security_protocol
            if security_config.sasl_password and security_config.sasl_mechanisms and security_config.sasl_username:
                self.conf["sasl.mechanisms"] = security_config.sasl_mechanisms
                self.conf["sasl.username"] = security_config.sasl_password
                self.conf["sasl.password"] = security_config.sasl_password
        self._consumer = Consumer(self.conf)
        self._consumer.subscribe(topics=config.topics)

    @abstractmethod
    def consume(self, timeout: Optional[float] = 1.0) -> Optional[Any]:
        """
        Consumes a message to a topic on the cluster
        Args:
            timeout (float): when to timeout consuming messages, defaults to 1.0
        Returns:
            message (Message): Kafka Message
        """
        raise NotImplementedError("Not Yet Implemented")

    def close(self):
        """
        Closes this consumer's connection to broker
        Returns: None
        """
        try:
            self._consumer.close()
        except Exception as exc:
            logger.error(f"{self.name}> Failed to close consumer", exc)

    @staticmethod
    def reset_offset(consumer: Consumer, partitions: List[TopicPartition]):
        """
        Callback to reset the offset on a consumer
        Args:
            consumer: Consumer application
            partitions: list of topic partitions
        """
        logging.warning(f"{__name__} Resetting offset on consumer for partitions: {partitions} ...")
        for p in partitions:
            p.offset = OFFSET_BEGINNING
        consumer.assign(partitions)

    @property
    def name(self):
        """
        Name of consumer
        Returns: Name of class
        """
        return self.__class__.__name__
