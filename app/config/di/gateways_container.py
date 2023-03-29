from dependency_injector import containers, providers
from app.infra.broker.producer import KafkaProducer


class GatewaysContainer(containers.DeclarativeContainer):
    """
    Dependency Injector container for Gateway services or 3rd party services used in the application
    """
    config = providers.Configuration()

    kafka_producer_client = providers.Singleton(KafkaProducer)
