from dependency_injector import containers, providers
from app.domain.sms.submit_sms import SubmitSmsService


class DomainContainer(containers.DeclarativeContainer):
    """
    Dependency Injector Container

    see https://github.com/ets-labs/python-dependency-injector for more details
    """

    services = providers.DependenciesContainer()

    submit_sms = providers.Factory(
        SubmitSmsService,
        producer=services.submit_sms_producer
    )
