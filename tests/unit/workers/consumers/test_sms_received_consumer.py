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
from app.workers.consumers.sms_received.__main__ import create_submitted_sms

fake = Faker()


@pytest.mark.unit
class SmsReceivedConsumerWorkerTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_create_sms_svc = Mock(spec=CreateSmsService)

    def test_creates_and_submits_sms_once(self):
        """The worker delegates submission exactly once to the use case."""
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

        create_submitted_sms(mock_sms, self.mock_create_sms_svc)

        self.mock_create_sms_svc.execute.assert_called_once_with(mock_sms)


if __name__ == '__main__':
    unittest.main()
