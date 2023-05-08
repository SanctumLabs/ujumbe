"""
Consumer Application Entry point
"""
from dependency_injector.wiring import inject, Provide
from app.infra.logger import log as logger
from app.domain.sms.create_sms import CreateSmsService
from app.services.sms_submitted_consumer import SmsSubmittedConsumer
from app.config.di.container import ApplicationContainer


@inject
def main(
    create_sms_svc: CreateSmsService = Provide[ApplicationContainer.domain.create_sms],
    sms_submitted_consumer: SmsSubmittedConsumer = Provide[ApplicationContainer.services.sms_submitted_consumer]
):
    log_prefix = "SMS Received Listener>"
    logger.info(f"{log_prefix} starting up...")
    while True:
        try:
            sms = sms_submitted_consumer.consume()
            if not sms:
                logger.info(f"{log_prefix} Waiting for messages...")
            else:
                create_sms_svc.execute(sms)
        except Exception as exc:
            logger.error(f"{log_prefix} failed to consume message: {exc}", exc)
            # TODO: report errors to monitoring tool


if __name__ == "__main__":
    container = ApplicationContainer()
    container.init_resources()
    container.wire(modules=[__name__])
    main()
