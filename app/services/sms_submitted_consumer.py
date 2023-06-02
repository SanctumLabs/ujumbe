"""
Sms Submitted Consumer to handle consuming Submitted SMS message events from broker
"""
from typing import Optional, Any
from app.core.infra.consumer import Consumer
from app.infra.logger import log as logger
from app.infra.broker.kafka.consumers import KafkaConsumer
from app.core.domain.entities.unique_id import UniqueId
from app.domain.entities.sms import Sms
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.message import Message
from app.domain.entities.sms_status import SmsDeliveryStatus
import app.messages.events.v1.data_pb2 as sms_data


class SmsSubmittedConsumer(Consumer):
    """
    SMS Submitted Consumer handle consuming SmsSubmitted events using a Kafka consumer to Kafka Broker Cluster
    """

    def __init__(self, kafka_consumer: KafkaConsumer):
        """
        Creates an instance of sms consumer with a topic to send events to and a KafkaProducer client to use to send
        events.
        Args:
            kafka_consumer (KafkaConsumer): Kafka Producer client to use
        """
        self.message = None
        self.kafka_consumer = kafka_consumer

    def consume(self) -> Optional[Sms]:
        try:
            self.message = self.kafka_consumer.consume()

            if self.message:
                data = self.message.sms

                sms_id = UniqueId(data.id)
                sender = PhoneNumber(data.sender)
                recipient = PhoneNumber(data.recipient)
                message = Message(data.message)

                sms_status = sms_data.SmsStatus.Name(data.status)
                status = SmsDeliveryStatus(sms_status)

                sms = Sms(
                    id=sms_id,
                    sender=sender,
                    recipient=recipient,
                    message=message,
                    status=status
                )
                return sms
            return None
        except Exception as e:
            logger.error(f"{self.consumer_name}> Failed to consume message. {e}")
            raise e

    def close(self):
        try:
            self.kafka_consumer.close()
        except Exception as e:
            logger.error(f"{self.consumer_name}> Failed to close connection. {e}")
            raise e

    def commit(self, *args, **kwargs) -> Any:
        return self.kafka_consumer.commit(self.message)

    def commit_async(self, *args, **kwargs) -> Any:
        return self.kafka_consumer.commit_async(self.message)
