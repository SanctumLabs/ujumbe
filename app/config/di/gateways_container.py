from dependency_injector import containers, providers
from app.infra.broker.producer import KafkaProducer
from app.infra.database.database_client import DatabaseClient
from app.infra.sms.sms_client import SmsClient
from app.settings import DatabaseSettings


class GatewaysContainer(containers.DeclarativeContainer):
    """
    Dependency Injector container for Gateway services or 3rd party services used in the application
    """
    config = providers.Configuration()
    db_config = providers.Configuration(pydantic_settings=[DatabaseSettings()])

    kafka_producer_client = providers.Singleton(KafkaProducer)

    database_client = providers.Singleton(DatabaseClient, db_config.url, db_config.logging_enabled)

    sms_client = providers.Singleton(SmsClient)
