"""
SmsSubmitted Consumer Application Entry point
"""
from dependency_injector.wiring import inject, Provide
from app.infra.logger import log as logger
from app.domain.sms.send_sms import SendSmsService
from app.services.sms_submitted_consumer import SmsSubmittedConsumer
from app.services.sms_sent_producer import SmsSentProducer
from app.config.di.container import ApplicationContainer


@inject
def main(
    send_sms_svc: SendSmsService = Provide[ApplicationContainer.domain.send_sms],
    sms_submitted_consumer: SmsSubmittedConsumer = Provide[ApplicationContainer.services.sms_submitted_consumer],
    sms_sent_producer: SmsSentProducer = Provide[ApplicationContainer.services.sms_sent_producer]
):
    """
    Main entry point for the sms submitted consumer worker. This consumes SMS_SUBMITTED message events and proceeds to
    send the SMS to a 3rd part system
    Args:
        send_sms_svc (SendSmsService): service that handles sending SMS records
        sms_submitted_consumer (SmsSubmittedConsumer): consumer class that handles consumption of sms submitted events
        sms_sent_producer (SmsSentProducer): producer class that handles publishing message to Broker
    Returns:
        None
    """
    log_prefix = "SMS Submitted Consumer>"
    logger.info(f"{log_prefix} starting up...")
    while True:
        try:
            sms = sms_submitted_consumer.consume()
            if not sms:
                logger.info(f"{log_prefix} Waiting for messages...")
            else:
                logger.info(f"{log_prefix} Received sms message: {sms}")
                send_sms_svc.execute(sms)
                sms_sent_producer.publish_message(sms)
                # commit the message on success
                sms_submitted_consumer.commit()
        except Exception as exc:
            logger.error(f"{log_prefix} failed to consume message: {exc}", exc)
            # TODO: report errors to monitoring tool


if __name__ == "__main__":
    container = ApplicationContainer()
    container.init_resources()
    container.wire(modules=[__name__])
    main()
