"""
Sms Received Consumer to handle consuming Submitted SMS message events from broker
"""
from typing import Optional, Any
import sanctumlabs.messageschema.events.notifications.sms.v1.data_pb2 as sms_data
from app.core.infra.consumer import Consumer
from app.infra.logger import log as logger
from app.infra.broker.kafka.consumers import KafkaConsumer
from app.core.domain.entities.unique_id import UniqueId
from app.domain.entities.sms import Sms
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.message import Message
from app.domain.entities.sms_status import SmsDeliveryStatus


class SmsReceivedConsumer(Consumer):
    """
    SMS Received Consumer handle consuming SmsReceived events using a Kafka consumer to Kafka Broker Cluster
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
        """
        Consumes sms received event message
        Returns: An (Sms) or None if there is no message
        """
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
            # TODO: if we fail to consume this message, we need to ensure we pass it a long to a dead letter topic for
            #  further processing
            raise e

    def close(self):
        """
        Attempts to close consumer connection to broker
        Raises: an (Exception) if there is a failure to close consumer connection
        """
        try:
            self.kafka_consumer.close()
        except Exception as e:
            logger.error(f"{self.consumer_name}> Failed to close connection. {e}")
            raise e

    def commit(self, message: Optional[Any] = None, *args, **kwargs) -> Any:
        return self.kafka_consumer.commit(message or self.message, args, kwargs)

    def commit_async(self, message: Optional[Any] = None, *args, **kwargs) -> Any:
        return self.kafka_consumer.commit_async(message or self.message, args, kwargs)
