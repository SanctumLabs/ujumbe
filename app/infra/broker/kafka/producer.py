from confluent_kafka import KafkaError, KafkaException, Producer
from app.settings import config
from app.infra.logger import log as logger
from .message import ProducerMessage


class KafkaProducer:
    def __init__(self):
        self.conf = {
            "bootstrap.servers": config.kafka.kafka_bootstrap_servers,
            # "security.protocol": config.kafka.kafka_security_protocol,
            # "sasl.mechanisms": config.kafka.sasl_mechanisms,
            # "sasl.username": config.kafka.sasl_password,
            # "sasl.password": config.kafka.sasl_password,
        }
        self._producer = Producer(self.conf)

    def produce(self, message: ProducerMessage):
        try:
            self._producer.produce(
                topic=message.topic, key=message.key, value=message.value
            )
            self._producer.flush()
        except KafkaException as exc:
            logger.error(f"KafkaProducer> Failed to produce message. Err: {e}", e)
            if exc.args[0].code() == KafkaError.MSG_SIZE_TOO_LARGE:
                # TODO: handle error
                pass
            else:
                raise exc
