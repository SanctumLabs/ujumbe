"""
Configurations for application. These are global variables that the app will use in its entire
lifetime
"""
from functools import lru_cache
from typing import Optional, AnyStr
from pydantic import BaseSettings

from dotenv import load_dotenv

load_dotenv()


def load_from_file(path: str, mode: str, encoding: str) -> AnyStr:
    """
    Convenience function that reads contents of a file
    @param path file path
    @param mode file mode to use when opening file
    @param encoding file encoding
    @returns contents of the file
    """
    with open(file=path, mode=mode, encoding=encoding) as file:
        return file.read()


# pylint: disable=too-few-public-methods
class SmsClientSettings(BaseSettings):
    """
    Twilio Sms Client settings
    """

    # twilio sms client settings
    account_sid: str = ""
    auth_token: str = ""
    messaging_service_sid: str = ""


# pylint: disable=too-few-public-methods
class DatabaseSettings(BaseSettings):
    """
    Database Settings
    """

    db_username: str = "ujumbe"
    db_password: str = "password"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "ujumbedb"
    db_driver: str = "postgresql"
    db_logging_enabled: bool = False
    db_log_level: str = "INFO"


# pylint: disable=too-few-public-methods
class KafkaSettings(BaseSettings):
    """
    Kafka Settings
    """

    kafka_bootstrap_servers: str = "localhost:9091"
    kafka_security_protocol: str = "ssl"
    kafka_sasl_mechanisms: str = ""
    kafka_sasl_username: str = "ujumbe"
    kafka_sasl_password: str = "ujumbe"

    submit_sms_topic: str = "SUBMIT_SMS_TOPIC"
    send_sms_topic: str = "SEND_SMS_TOPIC"


# pylint: disable=too-few-public-methods
class SentrySettings(BaseSettings):
    """
    Sentry settings
    """

    sentry_dsn: str = ""
    sentry_enabled: bool = False
    sentry_traces_sample_rate: float = 0.5
    sentry_debug_enabled: bool = False


# pylint: disable=too-few-public-methods
class AppSettings(BaseSettings):
    """
    Application settings

    You can overwrite any of these settings by having an environment
    variable with the upper-cased version of the name
    """

    server_name: str = "Ujumbe"
    description: str = "Simple RESTful SMS Server"
    base_url: str = "/api/v1/ujumbe"
    environment: str = "development"
    docs_disabled: bool = False

    result_backend: Optional[str] = "rpc://"

    # security settings
    username: str = "ujumbe-user"
    password: str = "ujumbe-password"

    sentry: SentrySettings = SentrySettings()
    kafka: KafkaSettings = KafkaSettings()
    database: DatabaseSettings = DatabaseSettings()
    sms: SmsClientSettings = SmsClientSettings()


config = AppSettings()


@lru_cache()
def get_config():
    """
    This is wrapped with lru_cache to ensure we don't continuously read from .env file on restarts
    """
    return AppSettings()
