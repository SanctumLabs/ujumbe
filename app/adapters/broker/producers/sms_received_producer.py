"""
Sms Received Producer to handle sending SMS Received message events to broker
"""
from tenacity import retry, stop_after_attempt, stop_after_delay, wait_exponential
from sanctumlabs.messageschema.events.notifications.sms.v1.data_pb2 import Sms as SmsData
from sanctumlabs.messageschema.events.notifications.sms.v1.events_pb2 import SmsReceived
from sanctumlabs.messageschema.messages.notifications.sms.v1.events_pb2 import SmsV1
from eventmsg_adaptor.event_streams import AsyncEventStream

from app.core.infra.producer import Producer
from app.infra.logger import log as logger
from app.domain.entities.sms import Sms as SmsEntity


class SmsReceivedProducer(Producer):
    """
    SMS Received Producer handle producing SmsReceived events using a Kafka producer to Kafka Broker Cluster
    """

    def __init__(self, topic: str, event_stream: AsyncEventStream):
        """
        Creates an instance of an SMS received producer with a topic to send events to and a KafkaProducer client to
        use to send events.
        Args:
            topic (str): Topic to send messages to.
            event_stream (AsyncEventStream): Kafka Producer client to use
        """
        self.topic = topic
        self.event_stream = event_stream

    @retry(
        reraise=True,
        stop=(stop_after_attempt(3) | stop_after_delay(10)),
        wait=wait_exponential(multiplier=1, min=3, max=5),
    )
    async def publish_message(self, sms: SmsEntity):
        try:
            event = SmsReceived(
                sms=SmsData(
                    id=sms.id.value,
                    sender=sms.sender.value,
                    recipient=sms.recipient.value,
                    message=sms.message.value
                )
            )
            data = SmsV1(
                sms_received=event
            )
            await self.event_stream.publish(destination=self.topic, event_body=data)
        except Exception as e:
            logger.error(f"{self.producer_name}> Failed to publish message Err: {e}")
            raise e
