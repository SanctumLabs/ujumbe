from dependency_injector import containers, providers
from app.infra.database.database_client import DatabaseClient, DatabaseClientParams
from app.infra.sms.sms_client import SmsClient, SmsClientParams

from eventmsg_adaptor.config.kafka import KafkaConfig, KafkaSchemaRegistryConfig
from eventmsg_adaptor import factory
from eventmsg_adaptor.config import Config, AdapterConfigs

from app.settings import get_kafka_settings, get_settings, get_db_settings, get_twilio_settings

_settings = get_settings()
_kafka_settings = get_kafka_settings()
_db_settings = get_db_settings()
_twilio_sms_settings = get_twilio_settings()

event_adapter_config = Config(
    service_name=_settings.server_name,
    default_adapter="kafka",
    adapters=AdapterConfigs(
        kafka=KafkaConfig(
            bootstrap_servers=[_kafka_settings.kafka_bootstrap_servers],
            schema_registry=KafkaSchemaRegistryConfig(
                schema_registry_url=_kafka_settings.kafka_schema_registry,
                schema_registry_user_info=_kafka_settings.kafka_schema_registry_user_info
            )
        )
    )
)


class InfraContainer(containers.DeclarativeContainer):
    """
    Dependency Injector container for Gateway services or 3rd party services used in the application
    """

    kafka_adapter_client = providers.Singleton(factory, config=event_adapter_config, adapter_name="aiokafka")

    database_client = providers.Singleton(
        DatabaseClient,
        DatabaseClientParams(
            dialect=_db_settings.db_dialect,
            driver=_db_settings.db_driver,
            host=_db_settings.db_host,
            port=_db_settings.db_port,
            database=_db_settings.db_name,
            username=_db_settings.db_username,
            password=_db_settings.db_password,
            logging_enabled=_db_settings.db_logging_enabled,
        ),
    )

    sms_client = providers.Singleton(
        SmsClient,
        SmsClientParams(
            account_sid=_twilio_sms_settings.twilio_account_sid,
            auth_token=_twilio_sms_settings.twilio_auth_token,
            messaging_service_sid=_twilio_sms_settings.twilio_messaging_service_sid,
            enabled=_twilio_sms_settings.twilio_enabled
        ),
    )
