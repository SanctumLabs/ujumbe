from dependency_injector import containers, providers
from .gateways_container import GatewaysContainer
from .kafka_container import KafkaContainer
from .services_container import ServicesContainer
from .repository_container import RepositoryContainer
from .domain_container import DomainContainer


class ApplicationContainer(containers.DeclarativeContainer):
    """
    Application container wiring all dependencies together
    """

    gateways = providers.Container(GatewaysContainer)

    kafka = providers.Container(KafkaContainer)

    services = providers.Container(ServicesContainer, gateways=gateways, kafka_container=kafka)

    repository = providers.Container(RepositoryContainer, gateways=gateways)

    domain = providers.Container(DomainContainer, services=services, repository=repository)
