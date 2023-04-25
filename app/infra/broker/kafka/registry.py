"""
Wrapper for Kafka Schema Registry Client
"""
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from app.settings import config
from .config import KafkaSchemaRegistryConfig


class KafkaRegistry:
    """
    Kafka Schema Registry client
    """

    def __init__(self, params: KafkaSchemaRegistryConfig = KafkaSchemaRegistryConfig(url=config.kafka.kafka_schema_registry)):
        """
        Creates an instance of a Kafka Schema Registry Client
        Args:
            params (KafkaSchemaRegistryConfig): Kafka Schema Registry config
        """
        conf = {
            "url": params.url
        }
        self._schema_registry = SchemaRegistryClient(conf)

    def get_json_serializer(self, json_schema: str) -> JSONSerializer:
        return JSONSerializer(schema_str=json_schema, schema_registry_client=self._schema_registry)
