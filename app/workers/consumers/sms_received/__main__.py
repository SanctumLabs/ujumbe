"""
Consumer Application Entry point
"""
from dependency_injector.wiring import inject, Provide
from app.domain.entities.sms import Sms
from app.infra.logger import log as logger
from app.domain.sms.create_sms import CreateSmsService
from app.infra.broker.kafka.consumer import KafkaConsumer
from app.config.di.container import ApplicationContainer


@inject
def main(
    create_sms_svc: CreateSmsService = Provide[ApplicationContainer.domain.create_sms],
    kafka_client: KafkaConsumer = Provide[ApplicationContainer.services.sms_received_kafka_consumer_client]
):
    log_prefix = "SMS Received Listener>"
    logger.info(f"{log_prefix} starting up...")
    try:
        while True:
            message = kafka_client.consume()
            if not message:
                logger.info(f"{log_prefix} Waiting for messages...")
            elif message.error():
                logger.error(f"{log_prefix} Failed to consume message {message.error()}")
            else:
                logger.info(
                    f"{log_prefix} Consumed event from topic {message.topic()}: key = {message.key().decode('utf-8')} "
                    f"value = {message.value().decode('utf-8')}"
                )
                data = message.value()
                sms = Sms.from_dict(data)
                create_sms_svc.execute(sms)
    except Exception as exc:
        logger.error(f"{log_prefix} failed to consume message: {exc}", exc)
        pass
    finally:
        kafka_client.close()


if __name__ == "__main__":
    container = ApplicationContainer()
    container.init_resources()
    container.wire(modules=[__name__])
    main()
