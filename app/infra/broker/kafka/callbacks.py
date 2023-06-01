from confluent_kafka import KafkaError, Message
from app.infra.logger import log as logger


def delivery_report(err: KafkaError, message: Message):
    """
    Reports the failure or success of a message delivery. This is the default provided in the event the call site
    does not pass in a delivery report handler
    Args:
        err (KafkaError): The error that occurred on None on success.
        message (Message): The message that was produced or failed.
    """

    if err is not None:
        logger.error(f"Delivery failed for record {message.key}: Error: {err}")
        return
    logger.info(f"Record with key {message.key()} successfully produced to topic {message.topic()} "
                f"on partition: [{message.partition()}] at offset {message.offset()}")
