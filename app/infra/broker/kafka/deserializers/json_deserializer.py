"""
Kafka JSON deserializer
"""
from typing import Any
from confluent_kafka.schema_registry.json_schema import JSONDeserializer
from confluent_kafka import Message
from confluent_kafka.serialization import SerializationContext, MessageField


class KafkaJsonDeserializer:
    def __init__(self, schema: str):
        """
        Kafka JSON serializer
        Args:
            schema: JSON schema of message
        """
        self.json_deserializer = JSONDeserializer(schema_str=schema)

    @property
    def deserializer(self) -> JSONDeserializer:
        return self.json_deserializer

    def deserialize_message(self, message: Message) -> Any:
        """
        Deserializes a message from JSON
        Args:
            message (Message): message to be deserialized
        Returns:
            bytes: deserialized representation of message
        """

        return self.json_deserializer(data=message.value(),
                                      ctx=SerializationContext(topic=message.topic(), field=MessageField.VALUE))
