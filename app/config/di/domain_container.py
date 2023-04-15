from dependency_injector import containers, providers
from app.domain.sms.submit_sms import SubmitSmsService
from app.domain.sms.create_sms import CreateSmsService
from app.domain.sms.send_sms import SendSmsService


class DomainContainer(containers.DeclarativeContainer):
    """
    Dependency Injector Container for Domain services

    see https://github.com/ets-labs/python-dependency-injector for more details
    """

    services = providers.DependenciesContainer()
    database = providers.DependenciesContainer()

    submit_sms = providers.Factory(
        SubmitSmsService, producer=services.submit_sms_producer
    )

    create_sms = providers.Factory(
        CreateSmsService,
        producer=services.send_sms_producer,
        repository=database.sms_repository,
    )

    send_sms = providers.Factory(
        SendSmsService,
        sms_service=services.sms_service,
        sms_response_repository=database.sms_response_repository,
    )
