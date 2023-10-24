from dependency_injector import containers, providers
from .gateways_container import GatewaysContainer
from .event_stream_container import EventStreamContainer
from .services_container import ServicesContainer
from .repository_container import RepositoryContainer
from .domain_container import DomainContainer


class ApplicationContainer(containers.DeclarativeContainer):
    """
    Application container wiring all dependencies together
    """

    kafka = providers.Container(EventStreamContainer)

    gateways = providers.Container(GatewaysContainer)

    services = providers.Container(ServicesContainer, gateways=gateways, kafka_container=kafka)

    repository = providers.Container(RepositoryContainer, gateways=gateways)

    domain = providers.Container(DomainContainer, services=services, repository=repository)
