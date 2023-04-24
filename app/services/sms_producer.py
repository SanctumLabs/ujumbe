"""
Sms Producer to handle sending SMS message events to broker
"""
from app.core.infra.producer import Producer
from app.infra.logger import log as logger
from app.domain.entities.sms import Sms
from app.infra.broker.kafka.producers import KafkaProducer
from app.infra.broker.kafka.message import ProducerMessage


class SmsProducer(Producer):
    """
    SMS Producer contains Kafka producer & registry clients to handle sending messages to Kafka Broker Cluster
    """

    def __init__(self, topic: str, kafka_producer: KafkaProducer):
        """
        Creates an instance of sms producer with a topic to send events to and a KafkaProducer client to use to send
        events.
        Args:
            topic (str): Topic to send message to
            kafka_producer (KafkaSimpleProducer): Kafka Producer client to use
        """
        self.topic = topic
        self.kafka_producer = kafka_producer

    def publish_message(self, sms: Sms):
        try:
            message = ProducerMessage(topic=self.topic, value=sms.to_dict())
            self.kafka_producer.produce(message=message)
        except Exception as e:
            logger.error(f"SmsProducer> Failed to publish message Err: {e}", e)
            raise e
