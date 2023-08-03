import unittest
from unittest.mock import Mock
import pytest
from faker import Faker
import sanctumlabs.messageschema.events.notifications.sms.v1.events_pb2 as events
import sanctumlabs.messageschema.events.notifications.sms.v1.data_pb2 as sms_data
from app.domain.entities.sms import Sms
from app.services.sms_submitted_consumer import SmsSubmittedConsumer
from app.infra.broker.kafka.consumers import KafkaConsumer
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.message import Message
from app.domain.entities.sms_status import SmsDeliveryStatus

fake = Faker()


@pytest.mark.unit
class SmsSubmittedConsumerTestCases(unittest.TestCase):

    def setUp(self) -> None:
        self.topic = "test_topic"
        self.mock_kafka_consumer = Mock(spec=KafkaConsumer)
        self.sms_submitted_consumer = SmsSubmittedConsumer(kafka_consumer=self.mock_kafka_consumer)

    def test_throws_exception_when_there_is_an_error_consuming_message(self):
        """Should throw exception if kafka client fails to consume message"""
        self.mock_kafka_consumer.consume.side_effect = Exception("Failed to consume message")

        with self.assertRaises(Exception):
            self.sms_submitted_consumer.consume()

        self.mock_kafka_consumer.consume.assert_called()
        self.mock_kafka_consumer.consume.assert_called_once()

    def test_successfully_consume_message_if_message_exists(self):
        """Should successfully consume message with Kafka client. No exception is thrown"""
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
            status=SmsDeliveryStatus.PENDING
        )

        data = sms_data.Sms(
            id=mock_sms.id.value,
            sender=mock_sms.sender.value,
            recipient=mock_sms.recipient.value,
            message=mock_sms.message.value,
            status=sms_data.SmsStatus.PENDING
        )

        event = events.SmsReceived(sms=data)

        self.mock_kafka_consumer.consume.return_value = event

        actual = self.sms_submitted_consumer.consume()

        self.assertEqual(mock_sms, actual)

        self.mock_kafka_consumer.consume.assert_called()
        self.mock_kafka_consumer.consume.assert_called_once()

    def test_successfully_consume_message_and_return_none_if_no_message_is_available(self):
        """Should successfully return None if no message exists using with Kafka client with no exception thrown"""
        self.mock_kafka_consumer.consume.return_value = None

        actual = self.sms_submitted_consumer.consume()

        self.assertIsNone(actual)

        self.mock_kafka_consumer.consume.assert_called()
        self.mock_kafka_consumer.consume.assert_called_once()

    def test_successfully_call_close_consumer_exception_(self):
        """Should successfully close kafka consumer client without exceptions"""
        self.mock_kafka_consumer.close.return_value = None

        self.sms_submitted_consumer.close()

        self.mock_kafka_consumer.close.assert_called()
        self.mock_kafka_consumer.close.assert_called_once()

    def test_throw_exception_when_calling_close_raises_exception_(self):
        """Should throw exception when calling close on kafka consumer client raises an exception"""
        self.mock_kafka_consumer.close.side_effect = Exception("failed to close consumer connection")

        with self.assertRaises(Exception):
            self.sms_submitted_consumer.close()

        self.mock_kafka_consumer.close.assert_called()
        self.mock_kafka_consumer.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
