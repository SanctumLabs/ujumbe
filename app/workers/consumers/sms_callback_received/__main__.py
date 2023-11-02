"""
SmsCallback Consumer Application Entry point
"""
from dependency_injector.wiring import inject, Provide
from app.infra.logger import log as logger
from app.domain.services.sms.create_sms import CreateSmsService
from app.adapters.events.consumers.sms_received_consumer import SmsReceivedConsumer
from app.adapters.events.producers.sms_submitted_producer import SmsSubmittedProducer
from app.config.di.container import ApplicationContainer


@inject
def main(
    create_sms_svc: CreateSmsService = Provide[ApplicationContainer.domain.create_sms],
    sms_received_consumer: SmsReceivedConsumer = Provide[
        ApplicationContainer.services.sms_received_consumer
    ],
    sms_submitted_producer: SmsSubmittedProducer = Provide[
        ApplicationContainer.services.sms_submitted_producer
    ],
):
    """
    Main entry point for the sms callback received consumer worker. This consumes SMS_RECEIVED message events and proceeds to
    create the SMS record in the database.
    Args:
        create_sms_svc (CreateSmsService): service that handles creation of SMS records
        sms_received_consumer (SmsReceivedConsumer): consumer class that handles consumption of sms received events
        sms_submitted_producer (SmsSubmittedProducer): producer class that handles publishing message to Broker
    Returns:
        None
    """
    log_prefix = "SMS Received Consumer>"
    logger.info(f"{log_prefix} starting up...")
    while True:
        try:
            sms = sms_received_consumer.consume()
            if not sms:
                logger.info(f"{log_prefix} Waiting for messages...")
            else:
                logger.info(f"{log_prefix} Received sms message: {sms}")
                create_sms_svc.execute(sms)
                # publish SMS to be sent
                sms_submitted_producer.publish_message(sms)
                # commit only on success
                sms_received_consumer.commit()
        except Exception as exc:
            logger.error(f"{log_prefix} failed to consume message: {exc}", exc)
            # TODO: report errors to monitoring tool


if __name__ == "__main__":
    container = ApplicationContainer()
    container.init_resources()
    container.wire(modules=[__name__])
    main()
