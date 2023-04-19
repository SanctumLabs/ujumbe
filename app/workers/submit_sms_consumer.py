"""
Consumer Application Entry point
"""
from app.infra.logger import log as logger
from app.infra.broker.kafka.consumer import KafkaConsumer
from fastapi import FastAPI
from app.config.di.container import ApplicationContainer
from app.infra.handlers.exception_handlers import attach_exception_handlers
from app.settings import config

container = ApplicationContainer()
consumer = KafkaConsumer()


async def on_startup():
    """
    Callback that is triggered on start application
    """
    logger.info(f"Consumer application starting up...")
    try:
        consumer.consume("SUBMIT_SMS_TOPIC")
    except Exception as exc:
        logger.error(f"failed to consume message: {exc}", exc)


async def on_teardown():
    """
    Callback that is triggered on teardown of application
    """
    logger.info(f"Consumer application tearing down...")
    try:
        consumer.close()
    except Exception as exc:
        logger.error(f"failed to consume message", exc)


consumer_app = FastAPI(
    title=f"{config.server_name} Consumer",
    description='Ujumbe consumer application',
    version="1.0.0",
    on_startup=[on_startup],
    on_shutdown=[on_teardown]
)

consumer_app.container = container
attach_exception_handlers(app=consumer_app)
