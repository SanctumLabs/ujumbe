"""
Sms Submitted Producer to handle sending SMS Submitted message events to broker
"""

from sanctumlabs.messageschema.messages.notifications.sms.v1.events_pb2 import SmsV1 as SmsV1EventBody
from sanctumlabs.messageschema.events.notifications.sms.v1.events_pb2 import SmsSubmitted as SmsSubmittedEvent
from sanctumlabs.messageschema.events.notifications.sms.v1.data_pb2 import SmsStatus, Sms as SmsPayload

from eventmsg_adaptor.event_streams import AsyncEventStream

from app.core.infra.producer import Producer
from app.infra.logger import log as logger
from app.domain.entities.sms import Sms as SmsEntity


class SmsSubmittedProducer(Producer):
    """
    SMS Submitted Producer handle producing SmsSubmitted events using a Kafka producer to Kafka Broker Cluster
    """

    def __init__(self, topic: str, async_event_stream: AsyncEventStream):
        """
        Creates an instance of an sms submitted producer with a topic to send events to and a KafkaProducer client to
        use to send events.
        Args:
            topic (str): Topic to send the message to.
            async_event_stream (AsyncEventStream): Event Producer client to use
        """
        self.topic = topic
        self.event_client = async_event_stream

    async def publish_message(self, sms: SmsEntity):
        try:
            event = SmsSubmittedEvent(
                sms=SmsPayload(
                    id=sms.id.value,
                    sender=sms.sender.value,
                    recipient=sms.recipient.value,
                    message=sms.message.value,
                    status=SmsStatus.PENDING
                )
            )
            event_body = SmsV1EventBody(sms_submitted=event)
            await self.event_client.publish(self.topic, event_body=event_body)
        except Exception as e:
            logger.error(f"{self.producer_name}> Failed to publish message Err: {e}")
            raise e
