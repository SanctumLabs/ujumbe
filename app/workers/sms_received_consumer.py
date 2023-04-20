"""
Consumer Application Entry point
"""
from app.consumer_app import consumer_app
from dependency_injector.wiring import inject
from app.infra.logger import log as logger
from app.domain.sms.create_sms import CreateSmsService
from app.config.di.dependency import dependency
from app.infra.broker.kafka.consumer import KafkaConsumer
from app.config.di.container import ApplicationContainer


@inject
async def consume_sms_received_event(create_sms: CreateSmsService = dependency(ApplicationContainer.domain.create_sms)):
    logger.info(f"Consumer application starting up...")
    try:
        consumer.consume("SUBMIT_SMS_TOPIC")
    except Exception as exc:
        logger.error(f"failed to consume message: {exc}", exc)


async def consume_sms_send_event():
    """
    Callback that is triggered on teardown of application
    """
    logger.info(f"Consumer application tearing down...")
    try:
        consumer.close()
    except Exception as exc:
        logger.error(f"failed to consume message", exc)
