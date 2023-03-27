from confluent_kafka import KafkaError, KafkaException, Producer
from app.config import config

from .message import ProducerMessage


class KafkaProducer:
    def __init__(self):
        self.conf = {
            'bootstrap.servers': config.kafka_bootstrap_servers,
            'security.protocol': config.kafka_security_protocol,
            'sasl.mechanisms': config.kafka_sasl_mechanisms,
            'sasl.username': config.kafka_sasl_password,
            'sasl.password': config.kafka_sasl_password,
        }
        self._producer = Producer(self.conf)

    def produce(self, message: ProducerMessage):
        try:
            self._producer.produce(topic=message.topic, key=message.key, value=message.value)
            self._producer.flush()
        except KafkaException as exc:
            if exc.args[0].code() == KafkaError.MSG_SIZE_TOO_LARGE:
                # TODO: handle error
                pass
            else:
                raise exc