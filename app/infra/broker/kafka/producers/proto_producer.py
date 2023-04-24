from typing import Optional
from confluent_kafka import KafkaError, KafkaException, SerializingProducer
from confluent_kafka.serialization import StringSerializer
from app.settings import config
from app.infra.logger import log as logger
from app.infra.broker.kafka.message import ProducerMessage
from app.infra.broker.kafka.serializers.protobuf_serializer import KafkaProtobufSerializer
from app.infra.broker.kafka.type_aliases import DeliverReportHandler
from app.infra.broker.kafka.callbacks import delivery_report
from . import KafkaProducer


class KafkaProtoProducer(KafkaProducer):
    def __init__(self, serializer: KafkaProtobufSerializer,
                 bootstrap_servers: str = config.kafka.kafka_bootstrap_servers, client_id: Optional[str] = None):
        super().__init__(bootstrap_servers, client_id)
        key_serializer = StringSerializer()
        self.conf.update({
            "key.serializer": key_serializer,
            "value.serializer": serializer.serializer
        })
        self._producer = SerializingProducer(self.conf)

    def produce(self, message: ProducerMessage, report_callback: Optional[DeliverReportHandler] = None, **kwargs):
        """
        Produces a message to a topic on the cluster
        Args:
            **kwargs:
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
            logger.error(f"{self.log_prefix}> Failed to produce message. Err: {exc}", exc)
            if exc.args[0].code() == KafkaError.MSG_SIZE_TOO_LARGE:
                logger.error(f"{self.log_prefix}> message size too large.")
            else:
                raise exc
