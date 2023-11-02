"""
Sms Sent Producer to handle sending SMS message events to broker
"""
import sanctumlabs.messageschema.events.notifications.sms.v1.data_pb2 as sms_data
from sanctumlabs.messageschema.messages.notifications.sms.v1.events_pb2 import SmsV1 as SmsV1EventBody
from sanctumlabs.messageschema.events.notifications.sms.v1.events_pb2 import SmsSent as SmsSentEvent
from sanctumlabs.messageschema.events.notifications.sms.v1.data_pb2 import Sms as SmsPayload
from eventmsg_adaptor.event_streams import AsyncEventStream

from app.core.infra.producer import Producer
from app.infra.logger import log as logger
from app.domain.entities.sms import Sms as SmsEntity


class SmsSentProducer(Producer):
    """
    SMS Sent Producer handle producing SendSms events using a Kafka producer to Kafka Broker Cluster
    """

    def __init__(self, topic: str, async_event_stream: AsyncEventStream):
        """
        Creates an instance of sms sent producer with a topic to send events to and a KafkaProducer client to use to
        send events.
        Args:
            topic (str): Topic to send message to
            async_event_stream (AsyncEventStream): Event Producer client to use
        """
        self.topic = topic
        self.event_client = async_event_stream

    async def publish_message(self, sms: SmsEntity):
        try:
            sms_sent_event = SmsSentEvent(
                sms=SmsPayload(
                    id=sms.id.value,
                    sender=sms.sender.value,
                    recipient=sms.recipient.value,
                    message=sms.message.value,
                    status=sms_data.SmsStatus.SENT
                )
            )
            event_body = SmsV1EventBody(sms_sent=sms_sent_event)
            await self.event_client.publish(destination=self.topic, event_body=event_body)
        except Exception as e:
            logger.error(f"{self.producer_name}> Failed to publish message {sms}. Err: {e}")
            raise e
