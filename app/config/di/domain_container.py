from dependency_injector import containers, providers
from app.domain.sms.submit_sms import SubmitSmsService
from app.domain.sms.submit_sms_callback import SubmitSmsCallbackService
from app.domain.sms.create_sms import CreateSmsService
from app.domain.sms.create_sms_callback import CreateSmsCallbackService
from app.domain.sms.send_sms import SendSmsService


class DomainContainer(containers.DeclarativeContainer):
    """
    Dependency Injector Container for Domain services

    see https://github.com/ets-labs/python-dependency-injector for more details
    """

    services = providers.DependenciesContainer()
    repository = providers.DependenciesContainer()

    submit_sms = providers.Factory(
        SubmitSmsService, producer=services.sms_received_producer
    )

    submit_sms_callback = providers.Factory(
        SubmitSmsCallbackService, producer=services.sms_callback_received_producer
    )

    create_sms = providers.Factory(
        CreateSmsService,
        producer=services.sms_submitted_producer,
        repository=repository.sms_repository,
    )

    send_sms = providers.Factory(
        SendSmsService,
        sms_service=services.sms_service,
        sms_response_repository=repository.sms_response_repository,
    )

    create_sms_callback = providers.Factory(
        CreateSmsCallbackService,
        repository=repository.sms_callback_repository,
    )
