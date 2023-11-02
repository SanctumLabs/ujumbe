from dependency_injector import containers, providers
from .infra_container import InfraContainer
from .event_producer_container import EventProducerContainer
from .services_container import ServicesContainer
from .repository_container import RepositoryContainer
from .domain_container import DomainContainer


class ApplicationContainer(containers.DeclarativeContainer):
    """
    Application container wiring all dependencies together
    """

    infra = providers.Container(InfraContainer)

    repository = providers.Container(RepositoryContainer, infra=infra)

    services = providers.Container(ServicesContainer, infra=infra)

    event_producers = providers.Container(EventProducerContainer, infra=infra)

    domain = providers.Container(DomainContainer, services=services, producers=event_producers, repository=repository)
