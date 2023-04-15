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


class SmsClientSettings(BaseSettings):
    """
    Twilio Sms Client settings
    """

    # twilio sms client settings
    account_sid: str = ""
    auth_token: str = ""
    messaging_service_sid: str = ""


class DatabaseSettings(BaseSettings):
    """
    Database Settings
    """

    username: str = "ujumbe-user"
    password: str = "ujumbe-password"
    host: str = "localhost"
    port: int = 5432
    database: str = "ujumbe"
    driver: str = "postgresql"
    logging_enabled: bool = False


class KafkaSettings(BaseSettings):
    """
    Kafka Settings
    """

    bootstrap_servers: str = "http://localhost:9091"
    security_protocol: str = "ssl"
    sasl_mechanisms: str = ""
    sasl_username: str = "ujumbe"
    sasl_password: str = "ujumbe"

    submit_sms_topic: str = "SUBMIT_SMS_TOPIC"
    send_sms_topic: str = "SEND_SMS_TOPIC"


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

    # sentry settings
    sentry_dsn: str = ""
    sentry_enabled: bool = False
    sentry_traces_sample_rate: float = 0.5
    sentry_debug_enabled: bool = False

    # security settings
    username: str = "ujumbe-user"
    password: str = "ujumbe-password"

    # kafka settings
    kafka: KafkaSettings = KafkaSettings()
    database: DatabaseSettings = DatabaseSettings()
    sms: SmsClientSettings = SmsClientSettings()


config = AppSettings()


@lru_cache()
def get_config():
    """
    Gets configuration This is wrapped with lru_cache to ensure we don't continuously read from .env file on restarts
    """
    return AppSettings()
