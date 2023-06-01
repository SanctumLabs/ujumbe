"""
Protobuf Deserializer
"""
from typing import Any
from confluent_kafka.schema_registry.protobuf import ProtobufDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka import Message
from app.infra.logger import log


class KafkaProtobufDeserializer:
    def __init__(self, msg_type: Any):
        """
        Kafka Protobuf deserializer
        Args:
            msg_type: Generated protobuf message
        """
        self.msg_type = msg_type
        self.serializer_config = {"use.deprecated.format": False}

        self.protobuf_deserializer = ProtobufDeserializer(message_type=msg_type, conf=self.serializer_config)

    @property
    def deserializer(self) -> ProtobufDeserializer:
        return self.protobuf_deserializer

    def deserialize_message(self, message: Message) -> Any:
        """
        Deserializes a message from Protobuf
        Args:
            message (object): message to be serialized
        Returns:
            bytes: deserialized message
        """
        try:
            if message:
                log.info(f"ProtobufDeserializer> deserializing message...")
                return self.deserializer(data=message.value(),
                                         ctx=SerializationContext(topic=message.topic(), field=MessageField.VALUE))
            log.warning(f"ProtobufDeserializer> message is none, skipping deserialization...")
        except Exception as exc:
            log.error(f"ProtobufDeserializer> Failed to deserialize message {message} from protobuf. Err: {exc}")
            raise exc
