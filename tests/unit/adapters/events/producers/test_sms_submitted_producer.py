import unittest
from unittest.mock import Mock
import pytest
from faker import Faker
from eventmsg_adaptor.event_streams import AsyncEventStream
from app.domain.entities.sms import Sms
from app.adapters.events.producers.sms_submitted_producer import SmsSubmittedProducer
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.message import Message
from app.domain.entities.sms_status import SmsDeliveryStatus

fake = Faker()


@pytest.mark.unit
class SmsSubmittedProducerTestCases(unittest.TestCase):
    def setUp(self) -> None:
        self.topic = "test_topic"
        self.mock_event_producer_client = Mock(spec=AsyncEventStream)
        self.sms_submitted_producer = SmsSubmittedProducer(
            topic=self.topic, async_event_stream=self.mock_event_producer_client
        )

    async def test_throws_exception_when_there_is_an_error_producing_message(self):
        """Should throw exception if the event producer client fails to publish a message"""
        sender_phone = "+254700000000"
        sender = PhoneNumber(value=sender_phone)
        recipient_phone = "+254700000000"
        recipient = PhoneNumber(value=recipient_phone)
        message_text = fake.text()
        message = Message(value=message_text)

        mock_sms = Sms(
            sender=sender,
            recipient=recipient,
            message=message,
            status=SmsDeliveryStatus.PENDING,
        )

        self.mock_event_producer_client.produce.side_effect = Exception(
            "Failed to publish message"
        )

        with self.assertRaises(Exception):
            await self.sms_submitted_producer.publish_message(mock_sms)

        self.mock_event_producer_client.produce.assert_called()
        self.mock_event_producer_client.produce.assert_called_once()

    async def test_successfully_publishes_message(self):
        """Should successfully produce a message with the event producer client. No exception is thrown"""
        sender_phone = "+254700000000"
        sender = PhoneNumber(value=sender_phone)
        recipient_phone = "+254700000000"
        recipient = PhoneNumber(value=recipient_phone)
        message_text = fake.text()
        message = Message(value=message_text)

        mock_sms = Sms(
            sender=sender,
            recipient=recipient,
            message=message,
            status=SmsDeliveryStatus.PENDING,
        )

        await self.sms_submitted_producer.publish_message(mock_sms)

        self.mock_event_producer_client.produce.assert_called()
        self.mock_event_producer_client.produce.assert_called_once()


if __name__ == "__main__":
    unittest.main()
