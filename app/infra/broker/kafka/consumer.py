from typing import List, Union
from dataclasses import dataclass
from confluent_kafka import KafkaError, KafkaException, Consumer, OFFSET_BEGINNING, TopicPartition, Message
from app.infra.logger import log as logging


@dataclass
class KafkaConsumerParams:
    """
    bootstrap_servers: Kafka bootstrap servers to listen on
    topic: Either a single topic or a list of topics for this consumer to listen to
    group_id: Group ID this consumer belongs to
    """
    bootstrap_servers: str
    topic: Union[str, List[str]]
    group_id: str

    @property
    def topics(self) -> Union[str, List[str]]:
        if isinstance(self.topic, str):
            return [self.topic]
        else:
            return self.topic


class KafkaConsumer:
    def __init__(self, params: KafkaConsumerParams):
        """
        Creates an instance of a Kafka consumer
        Args:
            params: KafkaConsumerParams to initialize a Kafka Consumer
        """
        conf = {
            "bootstrap.servers": params.bootstrap_servers,
            "group.id": params.group_id
            # "security.protocol": config.kafka.security_protocol,
            # "sasl.mechanisms": config.kafka.sasl_mechanisms,
            # "sasl.username": config.kafka.sasl_password,
            # "sasl.password": config.kafka.sasl_password,
        }
        self._consumer = Consumer(conf)
        self._consumer.subscribe(topics=params.topics)

    def consume(self):
        while True:
            try:
                message = self._consumer.poll()
                if not message:
                    logging.info(f"Waiting for messages...")
                    continue
                elif message.error():
                    logging.error(f"Failed to consume message {message.error()}")
                else:
                    logging.info(
                        f"Consumed event from topic {message.topic()}: key = {message.key().decode('utf-8')} "
                        f"value = {message.value().decode('utf-8')}"
                    )

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
