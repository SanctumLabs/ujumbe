"""
Wrapper for Kafka Schema Registry Client
"""
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from app.settings import config


class KafkaRegistry:
    """
    Kafka Schema Registry client
    """

    def __init__(self, url: str = config.kafka.kafka_schema_registry):
        """
        Creates an instance of a Kafka Schema Registry Client
        Args:
            url (str): Kafka Schema Registry URL to connect to. If not provided the default settings will be used
        """
        conf = {
            "url": url
        }
        self._schema_registry = SchemaRegistryClient(conf)

    def get_json_serializer(self, json_schema: str) -> JSONSerializer:
        return JSONSerializer(schema_str=json_schema, schema_registry_client=self._schema_registry)
