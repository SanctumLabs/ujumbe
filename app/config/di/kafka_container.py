from dependency_injector import containers, providers
from app.infra.broker.kafka.config import KafkaSchemaRegistryConfig, KafkaProducerConfig
from app.infra.broker.kafka.producers.simple_producer import KafkaSimpleProducer
from app.infra.broker.kafka.producers.proto_producer import KafkaProtoProducer
from app.infra.broker.kafka.producers.json_producer import KafkaJsonProducer
from app.infra.broker.kafka.serializers.protobuf_serializer import KafkaProtobufSerializer
from app.infra.broker.kafka.serializers.json_serializer import KafkaJsonSerializer
from app.infra.broker.kafka.registry import KafkaRegistry
from app.settings import KafkaSettings
import app.messages.proto.events.sms_submitted_pb2 as sms_submitted_event
from app.messages.json.sms_schema import sms_json_schema


class KafkaContainer(containers.DeclarativeContainer):
    """
    Dependency Injector container for Kafka
    """

    kafka_config = providers.Configuration(pydantic_settings=[KafkaSettings()])
    kafka_config.from_pydantic(KafkaSettings())

    kafka_schema_registry = providers.Singleton(
        KafkaRegistry,
        params=KafkaSchemaRegistryConfig(url=kafka_config.kafka_bootstrap_servers)
    )

    kafka_producer_client = providers.Singleton(
        KafkaSimpleProducer,
        params=KafkaProducerConfig(bootstrap_servers=kafka_config.kafka_bootstrap_servers)
    )

    kafka_sms_submitted_protobuf_serializer = providers.Singleton(
        KafkaProtobufSerializer,
        msg_type=sms_submitted_event.SmsSubmitted,
        registry_client=kafka_schema_registry
    )

    kafka_sms_submitted_proto_producer_client = providers.Singleton(
        KafkaProtoProducer,
        params=KafkaProducerConfig(bootstrap_servers=kafka_config.kafka_bootstrap_servers),
        serializer=kafka_sms_submitted_protobuf_serializer
    )

    kafka_sms_submitted_json_serializer = providers.Singleton(
        KafkaJsonSerializer,
        schema=sms_json_schema,
        registry_client=kafka_schema_registry
    )

    kafka_json_producer_client = providers.Singleton(
        KafkaJsonProducer,
        params=KafkaProducerConfig(bootstrap_servers=kafka_config.kafka_bootstrap_servers),
        serializer=kafka_sms_submitted_json_serializer
    )
