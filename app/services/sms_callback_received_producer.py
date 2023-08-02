"""
Sms Callback Received Producer to handle sending SMS Callback Received message events to broker
"""
from tenacity import retry, stop_after_attempt, stop_after_delay, wait_exponential
from app.core.infra.producer import Producer
from app.infra.logger import log as logger
from app.domain.entities.sms_callback import SmsCallback
from app.infra.broker.kafka.producers import KafkaProducer
from app.infra.broker.kafka.message import ProducerMessage
from sanctumlabs.messageschema.events.notifications.sms.v1.data_pb2 import SmsStatus, SmsCallback as SmsCallbackMessage
from sanctumlabs.messageschema.events.notifications.sms.v1.events_pb2 import SmsCallbackReceived
from sanctumlabs.messageschema.transport.kafka.notifications.sms.v1.events_pb2 import SmsV1


class SmsCallbackReceivedProducer(Producer):
    """
    SMS Callback Received Producer handle producing SmsReceived events using a Kafka producer to Kafka Broker Cluster
    """

    def __init__(self, topic: str, kafka_producer: KafkaProducer):
        """
        Creates an instance of an SMS callback received producer with a topic to send events to and a KafkaProducer
        client to use to send events.
        Args:
            topic (str): Topic to send message to
            kafka_producer (KafkaProducer): Kafka Producer client to use
        """
        self.topic = topic
        self.kafka_producer = kafka_producer

    @retry(reraise=True, stop=(stop_after_attempt(3) | stop_after_delay(10)),
           wait=wait_exponential(multiplier=1, min=3, max=5))
    def publish_message(self, sms_callback: SmsCallback):
        try:

            sms_status = SmsStatus.Name(sms_callback.sms_status.value)
            message_status = SmsStatus.Name(sms_callback.message_status.value)

            sms_callback_message = SmsCallbackMessage(
                id=sms_callback.id.value,
                account_sid=sms_callback.account_sid,
                sender=sms_callback.sender.value,
                sms_sid=sms_callback.sms_sid,
                sms_status=sms_status,
                message_sid=sms_callback.message_sid,
                message_status=message_status
            )

            data = SmsCallbackReceived(
                sms_callback=sms_callback_message
            )

            event = SmsV1(
                sms_callback_recevied=data
            )

            message = ProducerMessage(topic=self.topic, value=event)
            self.kafka_producer.produce(message=message)
        except Exception as e:
            logger.error(f"{self.producer_name}> Failed to publish message Err: {e}")
            raise e
