import unittest
import unittest.mock as mock
import pytest
from faker import Faker
from app.domain.entities.sms_callback import SmsCallback
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.sms_status import SmsDeliveryStatus

from app.domain.sms.submit_sms_callback import SubmitSmsCallbackService, SubmitSmsCallbackException
from app.core.infra.producer import Producer

fake = Faker()


@pytest.mark.unit
class SubmitSmsCallbackServiceTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_producer = mock.Mock(spec=Producer)
        self.submit_sms_callback_service = SubmitSmsCallbackService(producer=self.mock_producer)

    def test_throws_exception_when_no_sms_callback_is_provided(self):
        """Test throws an exception when no sms callback is provided"""
        with self.assertRaises(SubmitSmsCallbackException):
            self.submit_sms_callback_service.execute(None)

    def test_throws_exception_when_there_is_a_failure_publishing_sms_callback(self):
        """Test throws an exception when there is a failure publishing sms event"""
        phone = "+254700000000"
        account_sid = fake.uuid4()
        message_sid = fake.uuid4()
        sms_sid = fake.uuid4()
        message_status = SmsDeliveryStatus.SENT
        sms_status = SmsDeliveryStatus.SENT
        phone_number = PhoneNumber(value=phone)

        sms_callback = SmsCallback(account_sid=account_sid, sender=phone_number, message_sid=message_sid,
                                   message_status=message_status, sms_sid=sms_sid, sms_status=sms_status)

        self.mock_producer.publish_message.side_effect = Exception

        with self.assertRaises(SubmitSmsCallbackException):
            self.submit_sms_callback_service.execute(smscallback=sms_callback)

        self.mock_producer.publish_message.assert_called_with(sms_callback)

    def test_no_exception_is_thrown_and_sms_callback_is_published(self):
        """Test no exception is thrown & sms callback is successfully published"""
        phone = "+254700000000"
        account_sid = fake.uuid4()
        message_sid = fake.uuid4()
        sms_sid = fake.uuid4()
        message_status = SmsDeliveryStatus.SENT
        sms_status = SmsDeliveryStatus.SENT
        phone_number = PhoneNumber(value=phone)

        sms_callback = SmsCallback(account_sid=account_sid, sender=phone_number, message_sid=message_sid,
                                   message_status=message_status, sms_sid=sms_sid, sms_status=sms_status)

        self.mock_producer.publish_message.return_value = None

        self.submit_sms_callback_service.execute(smscallback=sms_callback)

        self.mock_producer.publish_message.assert_called_with(sms_callback)


if __name__ == '__main__':
    unittest.main()
