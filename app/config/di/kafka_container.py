"""
Kafka DI container
"""
from dependency_injector import containers, providers
from app.infra.broker.kafka.config import KafkaSchemaRegistryConfig, KafkaProducerConfig, KafkaConsumerConfig
from app.infra.broker.kafka.producers.simple_producer import KafkaSimpleProducer
from app.infra.broker.kafka.producers.proto_producer import KafkaProtoProducer
from app.infra.broker.kafka.producers.json_producer import KafkaJsonProducer
from app.infra.broker.kafka.consumers.proto_consumer import KafkaProtoConsumer
from app.infra.broker.kafka.serializers.protobuf_serializer import KafkaProtobufSerializer
from app.infra.broker.kafka.serializers.json_serializer import KafkaJsonSerializer
from app.infra.broker.kafka.deserializers.protobuf_deserializer import KafkaProtobufDeserializer
from app.infra.broker.kafka.deserializers.json_deserializer import KafkaJsonDeserializer
from app.infra.broker.kafka.registry import KafkaRegistry
from app.settings import KafkaSettings
from app.messages.json.sms_schema import sms_json_schema
import app.messages.events.v1.events_pb2 as sms_submitted_event


class KafkaContainer(containers.DeclarativeContainer):
    """
    Dependency Injector container for Kafka
    """

    config = providers.Configuration(pydantic_settings=[KafkaSettings()])
    config.from_pydantic(KafkaSettings())

    schema_registry = providers.Singleton(
        KafkaRegistry,
        params=KafkaSchemaRegistryConfig(url=config.kafka_schema_registry())
    )

    simple_producer_client = providers.Singleton(
        KafkaSimpleProducer,
        params=KafkaProducerConfig(bootstrap_servers=config.kafka_bootstrap_servers())
    )

    sms_submitted_protobuf_serializer = providers.Singleton(
        KafkaProtobufSerializer,
        msg_type=sms_submitted_event.SmsSubmitted,
        registry_client=schema_registry
    )

    sms_submitted_protobuf_deserializer = providers.Singleton(
        KafkaProtobufDeserializer,
        msg_type=sms_submitted_event.SmsSubmitted
    )

    sms_submitted_protobuf_producer = providers.Singleton(
        KafkaProtoProducer,
        params=KafkaProducerConfig(bootstrap_servers=config.kafka_bootstrap_servers()),
        serializer=sms_submitted_protobuf_serializer
    )

    sms_submitted_protobuf_consumer = providers.Singleton(
        KafkaProtoConsumer,
        params=KafkaConsumerConfig(bootstrap_servers=config.kafka_bootstrap_servers(),
                                   topic=config.sms_received_topic(),
                                   group_id=config.sms_received_group_id()),
        deserializer=sms_submitted_protobuf_deserializer
    )

    sms_submitted_json_serializer = providers.Singleton(
        KafkaJsonSerializer,
        schema=sms_json_schema,
        registry_client=schema_registry
    )

    sms_submitted_json_deserializer = providers.Singleton(
        KafkaJsonDeserializer,
        schema=sms_json_schema
    )

    json_producer_client = providers.Singleton(
        KafkaJsonProducer,
        params=KafkaProducerConfig(bootstrap_servers=config.kafka_bootstrap_servers()),
        serializer=sms_submitted_json_serializer
    )
