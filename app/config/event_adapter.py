from typing import cast

from eventmsg_adaptor.config.kafka import KafkaConfig, KafkaSchemaRegistryConfig, KafkaSecurityProtocolConfig
from eventmsg_adaptor.event_streams import AsyncEventStream
from eventmsg_adaptor import factory
from eventmsg_adaptor.config import Config, AdapterConfigs

from app.settings import get_kafka_settings, get_settings

_settings = get_settings()
_kafka_settings = get_kafka_settings()

event_adapter_config = Config(
    service_name=_settings.server_name,
    default_adapter="kafka",
    adapters=AdapterConfigs(
        kafka=KafkaConfig(
            bootstrap_servers=[_kafka_settings.kafka_bootstrap_servers],
            schema_registry=KafkaSchemaRegistryConfig(
                schema_registry_url=_kafka_settings.kafka_schema_registry
            )
        )
    )
)

kafka_event_stream = cast(AsyncEventStream, factory(event_adapter_config, adapter_name="aiokafka"))
