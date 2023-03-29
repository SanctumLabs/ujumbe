from dependency_injector import containers, providers
from app.settings import KafkaSettings


class ConfigContainer(containers.DeclarativeContainer):
    """
    Dependency Injector container for Gateway services or 3rd party services used in the application
    """
    config = providers.Configuration(pydantic_settings=[KafkaSettings()])
