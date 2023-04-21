from dependency_injector import containers, providers
from .gateways_container import GatewaysContainer
from .services_container import ServicesContainer
from .repository_container import RepositoryContainer
from .domain_container import DomainContainer


class ApplicationContainer(containers.DeclarativeContainer):
    """
    Application container wiring all dependencies together
    """

    gateways = providers.Container(GatewaysContainer)

    services = providers.Container(ServicesContainer, gateways=gateways)

    repository = providers.Container(RepositoryContainer, gateways=gateways)

    domain = providers.Container(DomainContainer, services=services, repository=repository)
