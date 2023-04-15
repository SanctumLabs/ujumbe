from app.core.infra.producer import Producer
from app.domain.entities.sms import Sms
from app.infra.broker.producer import KafkaProducer
from app.infra.broker.message import ProducerMessage


class SmsProducer(Producer):
    def __init__(self, topic: str, kafka_producer: KafkaProducer):
        self.topic = topic
        self.kafka_producer = kafka_producer

    def publish_message(self, message: Sms):
        try:
            producer_message = ProducerMessage(self.topic, message)
            self.kafka_producer.produce(producer_message)
        except Exception as e:
            raise e
