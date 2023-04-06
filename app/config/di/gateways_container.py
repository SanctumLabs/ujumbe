from dependency_injector import containers, providers
from app.infra.broker.producer import KafkaProducer
from app.infra.database.database_client import DatabaseClient, DatabaseClientParams
from app.infra.sms.sms_client import SmsClient, SmsClientParams
from app.settings import DatabaseSettings, SmsClientSettings


class GatewaysContainer(containers.DeclarativeContainer):
    """
    Dependency Injector container for Gateway services or 3rd party services used in the application
    """
    config = providers.Configuration()
    db_config = providers.Configuration(pydantic_settings=[DatabaseSettings()])
    sms_config = providers.Configuration(pydantic_settings=[SmsClientSettings()])

    kafka_producer_client = providers.Singleton(KafkaProducer)

    database_client = providers.Singleton(DatabaseClient, DatabaseClientParams(
        driver=db_config.driver,
        host=db_config.host,
        port=db_config.port,
        database=db_config.database,
        username=db_config.username,
        password=db_config.password,
        logging_enabled=db_config.logging_enabled
    ))

    sms_client = providers.Singleton(SmsClient,
                                     SmsClientParams(account_sid=sms_config.account_sid,
                                                     auth_token=sms_config.auth_token,
                                                     messaging_service_sid=sms_config.messaging_service_sid))
