from typing import Any
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from confluent_kafka.serialization import SerializationContext, MessageField
from ..registry import KafkaRegistry
from ..message import ProducerMessage


class KafkaProtobufSerializer:
    def __init__(self, msg_type: Any, registry_client: KafkaRegistry):
        """
        Kafka Protobuf serializer
        Args:
            msg_type: Generated protobuf message
            registry_client (KafkaRegistry): Kafka Registry client
        """
        self.registry_client = registry_client
        serializer_config = {"use.deprecated.format": False}

        self.protobuf_serializer = ProtobufSerializer(msg_type=msg_type, schema_registry_client=self.registry_client,
                                                      conf=serializer_config)

    @property
    def serializer(self) -> ProtobufSerializer:
        return self.protobuf_serializer

    def serialize_message_to_protobuf(self, message: ProducerMessage) -> bytes:
        """
        Serializes a message to Protobuf
        Args:
            message (object): message to be serialized
        Returns:
            bytes: byte representation of message serialized to Protobuf
        """

        return self.protobuf_serializer(message=message.value,
                                        ctx=SerializationContext(topic=message.topic, field=MessageField.VALUE))
