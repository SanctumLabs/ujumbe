from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import SerializationContext, MessageField
from ..registry import KafkaRegistry
from ..message import ProducerMessage


class KafkaJsonSerializer:
    def __init__(self, schema: str, registry_client: KafkaRegistry):
        """
        Kafka JSON serializer
        Args:
            schema: JSON schema of message
            registry_client (KafkaRegistry): Kafka Registry client
        """
        self.registry_client = registry_client
        self.json_serializer = JSONSerializer(schema_str=schema, schema_registry_client=self.registry_client)

    @property
    def serializer(self) -> JSONSerializer:
        return self.json_serializer

    def serialize_message_to_json(self, message: ProducerMessage) -> bytes:
        """
        Serializes a message to Protobuf
        Args:
            message (object): message to be serialized
        Returns:
            bytes: byte representation of message serialized to Protobuf
        """

        return self.json_serializer(obj=message.value,
                                    ctx=SerializationContext(topic=message.topic, field=MessageField.VALUE))
