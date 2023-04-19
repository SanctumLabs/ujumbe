from typing import List

from confluent_kafka import KafkaError, KafkaException, Consumer, OFFSET_BEGINNING, TopicPartition, Message
from app.settings import config
from app.infra.logger import log as logging


class KafkaConsumer:
    def __init__(self):
        self.conf = {
            "bootstrap.servers": config.kafka.kafka_bootstrap_servers,
            "group.id": "submit_sms_group_id"
            # "security.protocol": config.kafka.security_protocol,
            # "sasl.mechanisms": config.kafka.sasl_mechanisms,
            # "sasl.username": config.kafka.sasl_password,
            # "sasl.password": config.kafka.sasl_password,
        }
        self._consumer = Consumer(self.conf)

    def consume(self, topic: str) -> Message:
        try:
            self._consumer.subscribe([topic])
            while True:
                message = self._consumer.poll(1.0)
                if not message:
                    logging.info(f"Waiting for messages...")
                elif message.error():
                    logging.error(f"Failed to consume message {message}", message.error())
                else:
                    logging.info(
                        f"Consumed event from topic {message.topic()}: key = {message.key().decode('utf-8')} "
                        f"value = {message.value().decode('utf-8')}"
                    )
                    return message

        except KafkaException as exc:
            if exc.args[0].code() == KafkaError.MSG_SIZE_TOO_LARGE:
                # TODO: handle error
                pass
            else:
                raise exc

    def close(self):
        try:
            self._consumer.close()
        except Exception as exc:
            logging.error(f"failed to close consumer", exc)

    @staticmethod
    def reset_offset(consumer: Consumer, partitions: List[TopicPartition]):
        """
        Callback to reset the offset on a consumer
        Args:
            consumer: Consumer application
            partitions: list of topic partitions
        """
        logging.warning(f"Resetting offset on consumer for partitions: {partitions} ...")
        for p in partitions:
            p.offset = OFFSET_BEGINNING
        consumer.assign(partitions)
