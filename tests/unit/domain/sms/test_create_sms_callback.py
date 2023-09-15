import unittest
import unittest.mock as mock
import pytest
from faker import Faker
from app.domain.entities.sms_callback import SmsCallback
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.sms_status import SmsDeliveryStatus

from app.domain.services.sms.create_sms_callback import (
    CreateSmsCallbackService,
    CreateSmsCallbackException,
)
from app.domain.repositories.sms_repository import SmsRepository

fake = Faker()


@pytest.mark.unit
class CreateSmsCallbackServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_repository = mock.Mock(spec=SmsRepository)
        self.create_sms_callback_service = CreateSmsCallbackService(
            repository=self.mock_repository
        )

    def test_throws_exception_when_no_sms_callback_is_provided(self):
        """Test throws an exception when no sms callback is provided"""
        with self.assertRaises(CreateSmsCallbackException):
            self.create_sms_callback_service.execute(None)

    def test_throws_exception_when_there_is_a_creating_sms_callback(self):
        """Test throws an exception when there is a failure creating sms callback"""
        phone = "+254700000000"
        account_sid = fake.uuid4()
        message_sid = fake.uuid4()
        sms_sid = fake.uuid4()
        message_status = SmsDeliveryStatus.SENT
        sms_status = SmsDeliveryStatus.SENT
        phone_number = PhoneNumber(value=phone)

        sms_callback = SmsCallback(
            account_sid=account_sid,
            sender=phone_number,
            message_sid=message_sid,
            message_status=message_status,
            sms_sid=sms_sid,
            sms_status=sms_status,
        )

        self.mock_repository.add.side_effect = Exception

        with self.assertRaises(CreateSmsCallbackException):
            self.create_sms_callback_service.execute(sms_callback=sms_callback)

        self.mock_repository.add.assert_called_with(sms_callback)

    def test_no_exception_is_thrown_and_sms_callback_is_created(self):
        """Test no exception is thrown & sms callback is successfully created"""
        phone = "+254700000000"
        account_sid = fake.uuid4()
        message_sid = fake.uuid4()
        sms_sid = fake.uuid4()
        message_status = SmsDeliveryStatus.SENT
        sms_status = SmsDeliveryStatus.SENT
        phone_number = PhoneNumber(value=phone)

        sms_callback = SmsCallback(
            account_sid=account_sid,
            sender=phone_number,
            message_sid=message_sid,
            message_status=message_status,
            sms_sid=sms_sid,
            sms_status=sms_status,
        )

        self.mock_repository.add.return_value = None

        self.create_sms_callback_service.execute(sms_callback=sms_callback)

        self.mock_repository.add.assert_called_with(sms_callback)


if __name__ == "__main__":
    unittest.main()
