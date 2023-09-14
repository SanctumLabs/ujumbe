"""
Configurations for application. These are global variables that the app will use in its entire
lifetime
"""
from typing import Optional, AnyStr, Tuple
from functools import lru_cache
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
class TwilioSmsClientSettings(BaseSettings):
    """
    Twilio Sms Client settings

    Attributes:
        twilio_account_sid (str): Account SID
        twilio_auth_token (str): Authentication token
        twilio_messaging_service_sid (str): Messaging Service SID
        twilio_enabled (bool): Whether the system is enabled or not. Default is disabled
    """

    # twilio sms client settings
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_messaging_service_sid: str = ""
    twilio_enabled: bool = False


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
    db_dialect: str = "postgresql"
    db_driver: str = "psycopg2"
    db_logging_enabled: bool = False
    db_log_level: str = "INFO"
    db_url: Optional[
        str
    ] = f"{db_dialect}://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"


# pylint: disable=too-few-public-methods
class KafkaSettings(BaseSettings):
    """
    Kafka Settings
    """

    kafka_schema_registry: str = "http://localhost:8081"

    kafka_bootstrap_servers: str = "localhost:9091"
    kafka_security_protocol: str = "ssl"
    kafka_sasl_mechanisms: str = ""
    kafka_sasl_username: str = "ujumbe"
    kafka_sasl_password: str = "ujumbe"

    sms_received_topic: str = "sms_received_topic"
    sms_received_group_id: str = "sms_received_group_id"

    sms_submitted_topic: str = "sms_submitted_topic"
    sms_submitted_group_id: str = "sms_submitted_group_id"

    sms_sent_topic: str = "sms_sent_topic"
    sms_sent_group_id: str = "sms_sent_group_id"


# pylint: disable=too-few-public-methods
class SentrySettings(BaseSettings):
    """
    Sentry settings
    """

    sentry_dsn: str = ""
    sentry_enabled: bool = False
    sentry_traces_sample_rate: float = 0.5
    sentry_debug_enabled: bool = False
    sentry_profile_rate: float = 0.0
    sentry_sample_rate: float = 0.25


class CorsSettings(BaseSettings):
    # CORS Configuration
    cors_allow_origins: Tuple[str, ...] = [
        "http://localhost:3000",
        "http://burrito:3000",
        "http://p.yoco.co.za:3000",
        "https://portal.yoco.co.za",
    ]  # type: ignore
    cors_allow_origin_regex: Optional[str] = None
    cors_allow_credentials: bool = True
    cors_allow_headers: Tuple[str, ...] = ["x-auth-token", "userid"]  # type: ignore
    cors_allow_methods: Tuple[str, ...] = ["GET"]  # type: ignore


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

    git_branch: Optional[str] = None
    git_commit_sha: str = "dev"

    # security settings
    username: str = "ujumbe-user"
    password: str = "ujumbe-password"

    sentry: SentrySettings = SentrySettings()
    kafka: KafkaSettings = KafkaSettings()
    database: DatabaseSettings = DatabaseSettings()
    twilio_sms_client: TwilioSmsClientSettings = TwilioSmsClientSettings()
    cors: CorsSettings = CorsSettings()


config = AppSettings()
sentry = SentrySettings()
database_settings = DatabaseSettings()
kafka_settings = KafkaSettings()
twilio_sms_client_settings = TwilioSmsClientSettings()
cors_settings = CorsSettings()


@lru_cache()
def get_config():
    """
    This is wrapped with lru_cache to ensure we don't continuously read from .env file on restarts
    """
    return AppSettings()
