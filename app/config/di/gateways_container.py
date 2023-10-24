from dependency_injector import containers, providers
from app.infra.database.database_client import DatabaseClient, DatabaseClientParams
from app.infra.sms.sms_client import SmsClient, SmsClientParams
from app.settings import DatabaseSettings, TwilioSmsClientSettings


class GatewaysContainer(containers.DeclarativeContainer):
    """
    Dependency Injector container for Gateway services or 3rd party services used in the application
    """

    db_config = providers.Configuration(pydantic_settings=[DatabaseSettings()])
    # TODO: load settings from env directly
    # db_config.from_pydantic(settings=DatabaseSettings())

    twilio_sms_config = providers.Configuration(pydantic_settings=[TwilioSmsClientSettings()])
    # TODO: load settings from env directly
    # twilio_sms_config.from_pydantic(TwilioSmsClientSettings())

    database_client = providers.Singleton(
        DatabaseClient,
        DatabaseClientParams(
            dialect=db_config.db_dialect(),
            driver=db_config.db_driver(),
            host=db_config.db_host(),
            port=db_config.db_port(),
            database=db_config.db_name(),
            username=db_config.db_username(),
            password=db_config.db_password(),
            logging_enabled=db_config.db_logging_enabled(),
        ),
    )

    sms_client = providers.Singleton(
        SmsClient,
        SmsClientParams(
            account_sid=twilio_sms_config.twilio_account_sid(),
            auth_token=twilio_sms_config.twilio_auth_token(),
            messaging_service_sid=twilio_sms_config.twilio_messaging_service_sid(),
            enabled=twilio_sms_config.twilio_enabled()
        ),
    )
