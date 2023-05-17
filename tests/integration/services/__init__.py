import unittest
from testcontainers.kafka import KafkaContainer
from testcontainers.core.container import DockerContainer
from app.infra.broker.kafka.config import KafkaProducerConfig, KafkaSchemaRegistryConfig, KafkaConsumerConfig
from app.infra.broker.kafka.registry import KafkaRegistry

TEST_KAFKA_VERSION = "confluentinc/cp-kafka:7.1.0"
TEST_KAFKA_PORT = 29091
TEST_KAFKA_SCHEMA_REGISTRY_VERSION = "confluentinc/cp-schema-registry:7.1.0"
TEST_KAFKA_SCHEMA_REGISTRY_PORT = 8081


class BaseKafkaIntegrationTestCase(unittest.TestCase):
    started_container: KafkaContainer = None
    started_registry_container: DockerContainer = None

    kafka_bootstrap_server: str = None
    kafka_container_host: str = None
    kafka_container_port: str = None

    kafka_registry_port: str = None

    schema_registry_config: KafkaSchemaRegistryConfig = None
    producer_config: KafkaProducerConfig = None
    consumer_config: KafkaConsumerConfig = None

    kafka_schema_registry: KafkaRegistry = None

    @classmethod
    def setUpClass(cls) -> None:
        kafka_container = KafkaContainer(image=TEST_KAFKA_VERSION, port_to_expose=TEST_KAFKA_PORT)
        cls.started_container = kafka_container.start()

        cls.kafka_bootstrap_server = kafka_container.get_bootstrap_server()
        cls.kafka_container_host = kafka_container.get_container_host_ip()
        cls.kafka_container_port = kafka_container.get_exposed_port(TEST_KAFKA_PORT)

        cls.producer_config = KafkaProducerConfig(bootstrap_servers=cls.kafka_bootstrap_server)

        kafka_registry_container = DockerContainer(image=TEST_KAFKA_SCHEMA_REGISTRY_VERSION) \
            .with_exposed_ports(TEST_KAFKA_SCHEMA_REGISTRY_PORT) \
            .with_env("SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS",
                      f"http://localhost:{cls.kafka_container_port}") \
            .with_env("SCHEMA_REGISTRY_HOST_NAME", "ujumbe-kafka-schema-registry") \
            .with_env("SCHEMA_REGISTRY_LISTENERS", f"http://0.0.0.0:{TEST_KAFKA_SCHEMA_REGISTRY_PORT}")

        cls.started_registry_container = kafka_registry_container.start()

        cls.kafka_registry_port = cls.started_registry_container.get_exposed_port(port=TEST_KAFKA_SCHEMA_REGISTRY_PORT)
        cls.schema_registry_config = KafkaSchemaRegistryConfig(url=f"http://localhost:{cls.kafka_registry_port}")

        cls.kafka_schema_registry = KafkaRegistry(params=cls.schema_registry_config)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.started_container.stop()
        cls.started_registry_container.stop()
