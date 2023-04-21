import socket
from typing import Optional
from confluent_kafka import KafkaError, KafkaException, SerializingProducer
from confluent_kafka.serialization import StringSerializer
from app.settings import config
from app.infra.logger import log as logger
from .message import ProducerMessage
from .serializers.json_serializer import KafkaJsonSerializer
from .type_aliases import DeliverReportHandler
from .callbacks import delivery_report

log_prefix = "KafkaProducer> "


class KafkaJsonProducer:
    def __init__(self, serializer: KafkaJsonSerializer, bootstrap_servers: str = config.kafka.kafka_bootstrap_servers,
                 client_id: Optional[str] = None,
                 ):
        key_serializer = StringSerializer()
        conf = {
            "bootstrap.servers": bootstrap_servers,
            "client.id": client_id or socket.gethostname(),
            "key.serializer": key_serializer,
            "value.serializer": serializer.serializer,
            # "security.protocol": config.kafka.kafka_security_protocol,
            # "sasl.mechanisms": config.kafka.sasl_mechanisms,
            # "sasl.username": config.kafka.sasl_password,
            # "sasl.password": config.kafka.sasl_password,
        }
        self._producer = SerializingProducer(conf)

    def produce(self,
                message: ProducerMessage,
                report_callback: Optional[DeliverReportHandler] = None):
        """
        Produces a message to a topic on the cluster
        Args:
            message (ProducerMessage): message to be sent to topic on cluster
            report_callback (DeliverReportHandler): optional callable to handle deliver reports

        Returns:
            None
        """
        try:
            self._producer.produce(
                topic=message.topic,
                key=message.key,
                value=message.value,
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
