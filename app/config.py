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
class Config(BaseSettings):
    """
    Application settings

    You can overwrite any of these settings by having an environment
    variable with the upper cased version of the name
    """

    server_name: str = "Ujumbe"
    description: str = "Simple RESTful SMS Server"
    base_url: str = "/api/v1/ujumbe"
    environment: str = "development"
    docs_disabled: bool = False

    sms_api_username: str = ""
    sms_api_token: str = ""
    sms_sender_id: str = "ujumbe"
    sms_api_url: str = ""

    result_backend: Optional[str] = "rpc://"

    # sentry settings
    sentry_dsn: str = ""
    sentry_enabled: bool = False
    sentry_traces_sample_rate: float = 0.5
    sentry_debug_enabled: bool = False

    # security settings
    username: str = "ujumbe-user"
    password: str = "ujumbe-password"


config = Config()


@lru_cache()
def get_config():
    """
    Gets configuration This is wrapped with lru_cache to ensure we don't continuously read from .env file on restarts
    """
    return Config()
