import logging

from confluent_kafka import KafkaError, KafkaException, Consumer
from app.settings import config


class KafkaConsumer:
    def __init__(self):
        self.conf = {
            "bootstrap.servers": config.kafka.bootstrap_servers,
            "security.protocol": config.kafka.security_protocol,
            "sasl.mechanisms": config.kafka.sasl_mechanisms,
            "sasl.username": config.kafka.sasl_password,
            "sasl.password": config.kafka.sasl_password,
        }
        self._consumer = Consumer(self.conf)

    def consume(self):
        try:
            message = self._consumer.consume()
            if not message:
                logging.warning(f"Waiting for message...")
            elif message.error():
                logging.error(f"Failed to retrieve message message, {message.error()}")
            else:
                # Extract the (optional) key and value, and print.
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
        finally:
            self._consumer.close()
