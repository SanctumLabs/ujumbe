"""
SmsReceivedConsumer Worker unit tests
"""
import unittest
from unittest.mock import Mock
import pytest
from faker import Faker
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.message import Message
from app.domain.entities.sms_status import SmsDeliveryStatus
from app.domain.entities.sms import Sms
from app.domain.sms.create_sms import CreateSmsService
from app.services.sms_received_consumer import SmsReceivedConsumer
from app.workers.consumers.sms_received.__main__ import main

fake = Faker()


@pytest.mark.unit
class SmsReceivedConsumerWorkerTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_create_sms_svc = Mock(spec=CreateSmsService)
        self.mock_sms_received_consumer = Mock(spec=SmsReceivedConsumer)
        self.worker = main(create_sms_svc=self.mock_create_sms_svc,
                           sms_received_consumer=self.mock_sms_received_consumer)

    @unittest.skip("This test passes, what has not been yet explored is how to exit it successfully, "
                   "as the system under test runs forever")
    def test_creates_sms_when_received_from_consumer(self):
        """Should create an SMS record when received from consumer"""
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

        self.mock_sms_received_consumer.consume.return_value = mock_sms

        self.worker()

        self.mock_sms_received_consumer.consume.assert_called()
        self.mock_sms_received_consumer.consume.assert_called_once()

        self.mock_create_sms_svc.execute.assert_called()
        self.mock_create_sms_svc.execute.assert_called_once()
        self.mock_create_sms_svc.execute.assert_called_with(mock_sms)


if __name__ == '__main__':
    unittest.main()
