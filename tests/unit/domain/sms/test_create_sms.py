import unittest
import unittest.mock as mock
import pytest
from faker import Faker
from app.domain.entities.sms import Sms
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.message import Message
from app.domain.entities.sms_status import SmsDeliveryStatus

from app.domain.sms.create_sms import CreateSmsService, CreateSmsException, SmsRepository
from app.core.infra.producer import Producer

fake = Faker()


@pytest.mark.unit
class CreateSmsServiceTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_producer = mock.Mock(spec=Producer)
        self.mock_sms_repository = mock.Mock(spec=SmsRepository)
        self.create_sms_service = CreateSmsService(producer=self.mock_producer, repository=self.mock_sms_repository)

    def test_throws_exception_when_no_sms_is_provided(self):
        """Test throws an exception when no sms is provided"""
        with self.assertRaises(CreateSmsException):
            self.create_sms_service.execute(None)

    def test_throws_exception_when_there_is_a_failure_creating_sms(self):
        """Test throws an exception when there is a failure creating sms"""
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
            status=SmsDeliveryStatus.PENDING
        )

        self.mock_sms_repository.add.side_effect = Exception

        with self.assertRaises(CreateSmsException):
            self.create_sms_service.execute(sms=sms)

        self.mock_sms_repository.add.assert_called_with(sms)
        self.mock_producer.publish_message.assert_not_called()

    def test_throws_exception_when_there_is_a_failure_publishing_created_sms(self):
        """Test throws an exception when there is a failure publishing created sms event"""
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
            status=SmsDeliveryStatus.PENDING
        )

        self.mock_sms_repository.add.return_value = sms
        self.mock_producer.publish_message.side_effect = Exception

        with self.assertRaises(CreateSmsException):
            self.create_sms_service.execute(sms=sms)

        self.mock_sms_repository.add.assert_called_with(sms)
        self.mock_producer.publish_message.assert_called_with(sms)

    def test_no_exception_is_thrown_and_sms_message_is_published(self):
        """Test no exception is thrown & sms is successfully created & published"""
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
            status=SmsDeliveryStatus.PENDING
        )

        self.mock_sms_repository.add.return_value = sms
        self.mock_producer.publish_message.return_value = None

        self.create_sms_service.execute(sms=sms)

        self.mock_sms_repository.add.assert_called_with(sms)
        self.mock_producer.publish_message.assert_called_with(sms)


if __name__ == '__main__':
    unittest.main()
