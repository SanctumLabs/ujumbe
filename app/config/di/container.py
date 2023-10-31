from dependency_injector import containers, providers
from .infra_container import InfraContainer
from .event_stream_container import EventStreamContainer
from .services_container import ServicesContainer
from .repository_container import RepositoryContainer
from .domain_container import DomainContainer


class ApplicationContainer(containers.DeclarativeContainer):
    """
    Application container wiring all dependencies together
    """

    event_stream = providers.Container(EventStreamContainer)

    infra = providers.Container(InfraContainer)

    services = providers.Container(ServicesContainer, infra=infra, event_stream=event_stream)

    repository = providers.Container(RepositoryContainer, gateways=infra)

    domain = providers.Container(DomainContainer, services=services, repository=repository)
