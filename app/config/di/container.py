from dependency_injector import containers, providers
from app.settings import KafkaSettings
from .gateways_container import GatewaysContainer
from .services_container import ServicesContainer
from .domain_container import DomainContainer


class ApplicationContainer(containers.DeclarativeContainer):
    """
    Application container wiring all dependencies together
    """

    config = providers.Configuration(pydantic_settings=[KafkaSettings()])

    gateways = providers.Container(GatewaysContainer, config=config)

    services = providers.Container(ServicesContainer, gateways=gateways)

    domain = providers.Container(DomainContainer, services=services)
