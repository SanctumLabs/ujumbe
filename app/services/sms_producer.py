from app.core.infra.producer import Producer
from app.infra.logger import log as logger
from app.domain.entities.sms import Sms
from app.infra.broker.kafka.producer import KafkaProducer
from app.infra.broker.kafka.message import ProducerMessage


class SmsProducer(Producer):
    def __init__(self, topic: str, kafka_producer: KafkaProducer):
        self.topic = topic
        self.kafka_producer = kafka_producer

    def publish_message(self, message: Sms):
        try:
            producer_message = ProducerMessage(self.topic, message.to_dict())
            self.kafka_producer.produce(producer_message)
        except Exception as e:
            logger.error(f"SmsProducer> Failed to publish message Err: {e}", e)
            raise e
