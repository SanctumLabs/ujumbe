import unittest
import unittest.mock as mock
import pytest
from faker import Faker
from app.domain.entities.sms import Sms
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.message import Message
from app.domain.entities.sms_status import SmsDeliveryStatus

from app.domain.services.sms.submit_sms import SubmitSmsService, SubmitSmsException
from app.core.infra.producer import Producer

fake = Faker()


@pytest.mark.unit
class SubmitSmsServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_producer = mock.Mock(spec=Producer)
        self.submit_sms_service = SubmitSmsService(producer=self.mock_producer)

    def test_throws_exception_when_no_sms_is_provided(self):
        """Test throws an exception when no sms is provided"""
        with self.assertRaises(SubmitSmsException):
            self.submit_sms_service.execute(None)

    def test_throws_exception_when_there_is_a_failure_publishing_sms(self):
        """Test throws an exception when there is a failure publishing sms event"""
        sender_phone = "+254700000000"
        sender = PhoneNumber(value=sender_phone)
        recipient_phone = "+254700000000"
        recipient = PhoneNumber(value=recipient_phone)
        message_text = fake.text()
        message = Message(value=message_text)

        sms = Sms(
            sender=sender,
            recipient=recipient,
            message=message,
            status=SmsDeliveryStatus.PENDING,
        )

        self.mock_producer.publish_message.side_effect = Exception

        with self.assertRaises(SubmitSmsException):
            self.submit_sms_service.execute(sms=sms)

        self.mock_producer.publish_message.assert_called_with(sms)

    def test_no_exception_is_thrown_and_sms_message_is_published(self):
        """Test no exception is thrown & sms is successfully published"""
        sender_phone = "+254700000000"
        sender = PhoneNumber(value=sender_phone)
        recipient_phone = "+254700000000"
        recipient = PhoneNumber(value=recipient_phone)
        message_text = fake.text()
        message = Message(value=message_text)

        sms = Sms(
            sender=sender,
            recipient=recipient,
            message=message,
            status=SmsDeliveryStatus.PENDING,
        )

        self.mock_producer.publish_message.return_value = None

        self.submit_sms_service.execute(sms=sms)

        self.mock_producer.publish_message.assert_called_with(sms)


if __name__ == "__main__":
    unittest.main()
