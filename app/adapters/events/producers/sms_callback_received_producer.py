"""
Sms Callback Received Producer to handle sending SMS Callback Received message events to broker
"""
from tenacity import retry, stop_after_attempt, stop_after_delay, wait_exponential
from eventmsg_adaptor.event_streams import AsyncEventStream
from sanctumlabs.messageschema.events.notifications.sms.v1.data_pb2 import SmsCallback as SmsCallbackMessage
from sanctumlabs.messageschema.events.notifications.sms.v1.events_pb2 import SmsCallbackReceived
from sanctumlabs.messageschema.messages.notifications.sms.v1.events_pb2 import SmsV1

from app.core.infra.producer import Producer
from app.infra.logger import log as logger
from app.domain.entities.sms_callback import SmsCallback


class SmsCallbackReceivedProducer(Producer):
    """
    SMS Callback Received Producer handles producing SmsReceived events using a Kafka producer to Kafka Broker Cluster
    """

    def __init__(self, topic: str, async_event_stream: AsyncEventStream):
        """
        Creates an instance of an SMS callback received producer with a topic to send events to and a KafkaProducer
        client to use to send events.
        Args:
            topic (str): Topic to send message to
            async_event_stream (AsyncEventStream): Event Producer client to use
        """
        self.topic = topic
        self.async_event_producer = async_event_stream

    @retry(reraise=True, stop=(stop_after_attempt(3) | stop_after_delay(10)),
           wait=wait_exponential(multiplier=1, min=3, max=5))
    async def publish_message(self, sms_callback: SmsCallback):
        try:

            sms_status = sms_callback.sms_status.to_proto()
            message_status = sms_callback.message_status.to_proto()

            sms_callback_message = SmsCallbackMessage(
                account_sid=sms_callback.account_sid,
                sender=sms_callback.sender.value,
                sms_id=sms_callback.id.value,
                sms_status=sms_status,
                message_sid=sms_callback.message_sid,
                message_status=message_status
            )

            data = SmsCallbackReceived(
                sms_callback=sms_callback_message
            )

            event = SmsV1(
                sms_callback_received=data
            )

            await self.async_event_producer.publish(destination=self.topic, event_body=event)
        except Exception as e:
            logger.error(f"{self.producer_name}> Failed to publish message Err: {e}")
            raise e
