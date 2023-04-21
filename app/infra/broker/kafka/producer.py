import socket
from typing import Optional
from confluent_kafka import KafkaError, KafkaException, Producer
from confluent_kafka.serialization import SerializationContext, MessageField, Serializer
from app.settings import config
from app.infra.logger import log as logger
from .message import ProducerMessage
from .type_aliases import DeliverReportHandler
from .callbacks import delivery_report

log_prefix = "KafkaProducer> "


class KafkaProducer:
    def __init__(self, bootstrap_servers: str = config.kafka.kafka_bootstrap_servers,
                 client_id: Optional[str] = None,
                 ):
        conf = {
            "bootstrap.servers": bootstrap_servers,
            "client.id": client_id or socket.gethostname(),
            # "security.protocol": config.kafka.kafka_security_protocol,
            # "sasl.mechanisms": config.kafka.sasl_mechanisms,
            # "sasl.username": config.kafka.sasl_password,
            # "sasl.password": config.kafka.sasl_password,
        }
        self._producer = Producer(conf)

    def produce(self,
                message: ProducerMessage,
                serializer: Optional[Serializer] = None,
                report_callback: Optional[DeliverReportHandler] = None):
        """
        Produces a message to a topic on the cluster
        Args:
            message (ProducerMessage): message to be sent to topic on cluster
            serializer (Serializer): optional serializer to use when sending message
            report_callback (DeliverReportHandler): optional callable to handle deliver reports

        Returns:
            None
        """
        try:
            self._producer.produce(
                topic=message.topic,
                key=message.key,
                value=self.serialize_message(message, serializer),
                on_delivery=report_callback or delivery_report
            )
            self._producer.flush()
        except KafkaException as exc:
            # TODO: handle kafka exception
            logger.error(f"{log_prefix} Failed to produce message. Err: {exc}", exc)
            if exc.args[0].code() == KafkaError.MSG_SIZE_TOO_LARGE:
                logger.error(f"{log_prefix} message size too large.")
            else:
                raise exc

    @staticmethod
    def serialize_message(message: ProducerMessage, serializer: Optional[Serializer] = None) -> bytes:
        """
        Serializes a message to bytes. if no serializer is provided, value of message is returned
        Args:
             message (object): message to be serialized
             serializer (Serializer): optional serializer class to handle serializing message
        Returns:
            bytes: Byte representation of message
        """
        if serializer:
            return serializer(message, SerializationContext(topic=message.topic, field=MessageField.VALUE))
        return message.value
