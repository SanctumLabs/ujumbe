from dependency_injector import containers, providers
from app.adapters.sms_svc.sms_service import UjumbeSmsService


class ServicesContainer(containers.DeclarativeContainer):
    """
    Dependency Injector Container for wrapper for 3rd Party services or external services

    see https://github.com/ets-labs/python-dependency-injector for more details
    """
    infra = providers.DependenciesContainer()

    sms_service = providers.Factory(UjumbeSmsService, sms_client=infra.sms_client)
