"""
Sms Received Producer to handle sending SMS Received message events to broker
"""
from tenacity import retry, stop_after_attempt, stop_after_delay, wait_exponential
from app.core.infra.producer import Producer
from app.infra.logger import log as logger
from app.domain.entities.sms import Sms
from app.infra.broker.kafka.producers import KafkaProducer
from app.infra.broker.kafka.message import ProducerMessage
import app.messages.events.v1.events_pb2 as events
import app.messages.events.v1.data_pb2 as sms_data


class SmsReceivedProducer(Producer):
    """
    SMS Received Producer handle producing SmsReceived events using a Kafka producer to Kafka Broker Cluster
    """

    def __init__(self, topic: str, kafka_producer: KafkaProducer):
        """
        Creates an instance of an sms received producer with a topic to send events to and a KafkaProducer client to
        use to send events.
        Args:
            topic (str): Topic to send message to
            kafka_producer (KafkaProducer): Kafka Producer client to use
        """
        self.topic = topic
        self.kafka_producer = kafka_producer

    @retry(reraise=True, stop=(stop_after_attempt(3) | stop_after_delay(10)),
           wait=wait_exponential(multiplier=1, min=3, max=5))
    def publish_message(self, sms: Sms):
        try:
            data = sms_data.Sms(
                id=sms.id.value,
                sender=sms.sender.value,
                recipient=sms.recipient.value,
                message=sms.message.value,
                status=sms_data.SmsStatus.PENDING
            )
            event = events.SmsReceived(sms=data)
            message = ProducerMessage(topic=self.topic, value=event)
            self.kafka_producer.produce(message=message)
        except Exception as e:
            logger.error(f"{self.producer_name}> Failed to publish message Err: {e}")
            raise e
