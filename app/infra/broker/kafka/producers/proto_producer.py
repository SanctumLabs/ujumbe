from typing import Optional
from confluent_kafka import KafkaError, KafkaException, SerializingProducer
from confluent_kafka.serialization import StringSerializer
from app.infra.logger import log as logger
from app.infra.broker.kafka.message import ProducerMessage
from app.infra.broker.kafka.serializers.protobuf_serializer import KafkaProtobufSerializer
from app.infra.broker.kafka.type_aliases import DeliverReportHandler
from app.infra.broker.kafka.callbacks import delivery_report
from . import KafkaProducer
from ..config import KafkaProducerConfig


class KafkaProtoProducer(KafkaProducer):
    def __init__(self, params: KafkaProducerConfig, serializer: KafkaProtobufSerializer):
        super().__init__(params)
        self.key_serializer = StringSerializer()
        self.serializer = serializer
        self.config = self.conf.copy()
        self.config.update({
            "key.serializer": self.key_serializer,
            "value.serializer": self.serializer.serializer
        })
        self._producer = SerializingProducer(self.config)

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
                key=self.key_serializer(message.key),
                value=self.serializer.serialize_message_to_protobuf(message),
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
