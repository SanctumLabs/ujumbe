from typing import Optional, Any
from confluent_kafka import KafkaException
from app.infra.logger import log as logger
from app.infra.broker.kafka.deserializers.protobuf_deserializer import KafkaProtobufDeserializer
from . import KafkaConsumer
from ..config import KafkaConsumerConfig


class KafkaProtoConsumer(KafkaConsumer):
    """
    Kafka protobuf consumer
    """

    def __init__(self, params: KafkaConsumerConfig, deserializer: KafkaProtobufDeserializer):
        """
        Kafka proto consumer
        Args:
            params (KafkaConsumerConfig): consumer configuration
            deserializer (KafkaProtobufDeserializer): deserializer
        """
        super().__init__(params)
        self.deserializer = deserializer

    def consume(self, timeout: Optional[float] = 1.0) -> Any:
        """
        Consumes a message on a given topic on the cluster
        Args:
            timeout (float): message to be sent to topic on cluster
        Returns:
            None
        """
        try:
            message = self._consumer.poll(timeout=timeout)
            if message:
                logger.info(f"{self.name} consumed message from topic {message.topic()}, key = {message.key()}")
                msg = self.deserializer.deserialize_message(message)
                return msg
        except KafkaException as exc:
            logger.error(f"{self.name}> Failed to consume message. {exc}")
            raise exc
