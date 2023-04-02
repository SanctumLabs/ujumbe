from dependency_injector import containers, providers
from app.infra.broker.producer import KafkaProducer
from app.infra.database.database_client import DatabaseClient
from app.infra.sms.sms_client import SmsClient
from app.settings import DatabaseSettings, SmsClientSettings


class GatewaysContainer(containers.DeclarativeContainer):
    """
    Dependency Injector container for Gateway services or 3rd party services used in the application
    """
    config = providers.Configuration()
    db_config = providers.Configuration(pydantic_settings=[DatabaseSettings()])
    sms_config = providers.Configuration(pydantic_settings=[SmsClientSettings()])

    kafka_producer_client = providers.Singleton(KafkaProducer)

    database_client = providers.Singleton(DatabaseClient, db_config.url, db_config.logging_enabled)

    sms_client = providers.Singleton(SmsClient, sms_config.account_sid, sms_config.auth_token,
                                     sms_config.messaging_service_sid)
