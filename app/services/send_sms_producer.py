"""
Send Sms Producer to handle sending SMS message events to broker
"""
from app.core.infra.producer import Producer
from app.infra.logger import log as logger
from app.domain.entities.sms import Sms
from app.infra.broker.kafka.producers import KafkaProducer
from app.infra.broker.kafka.message import ProducerMessage
import app.messages.events.v1.events_pb2 as sms_submitted_event
import app.messages.events.v1.data_pb2 as sms_data


class SendSmsProducer(Producer):
    """
    Send SMS Producer handle producing SendSms events using a Kafka producer to Kafka Broker Cluster
    """

    def __init__(self, topic: str, kafka_producer: KafkaProducer):
        """
        Creates an instance of send sms producer with a topic to send events to and a KafkaProducer client to use to
        send events.
        Args:
            topic (str): Topic to send message to
            kafka_producer (KafkaProducer): Kafka Producer client to use
        """
        self.topic = topic
        self.kafka_producer = kafka_producer

    def publish_message(self, sms: Sms):
        try:
            data = sms_data.Sms(
                id=sms.id.value,
                sender=sms.sender.value,
                recipient=sms.recipient.value,
                message=sms.message.value,
                status=sms_data.SmsStatus.PENDING
            )
            event = sms_submitted_event.SmsSubmitted(sms=data)
            message = ProducerMessage(topic=self.topic, value=event)
            self.kafka_producer.produce(message=message)
        except Exception as e:
            logger.error(f"{self.producer_name}> Failed to publish message Err: {e}")
            raise e
