import unittest
import unittest.mock as mock
import pytest
from faker import Faker
from app.domain.entities.sms import Sms
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.message import Message
from app.domain.entities.sms_status import SmsDeliveryStatus
from app.domain.entities.sms_type import SmsType
from app.domain.entities.sms_response import SmsResponse
from app.domain.entities.sms_date import SmsDate
from app.domain.entities.sms_price import SmsPrice

from app.domain.sms.send_sms import SendSmsService, SendSmsException, SmsRepository, SmsService

fake = Faker()


@pytest.mark.unit
class SendSmsServiceTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_sms_service = mock.Mock(spec=SmsService)
        self.mock_sms_response_repository = mock.Mock(spec=SmsRepository)
        self.create_sms_service = SendSmsService(sms_service=self.mock_sms_service,
                                                 sms_response_repository=self.mock_sms_response_repository)

    def test_throws_exception_when_no_sms_is_provided(self):
        """Test throws an exception when no sms is provided"""
        with self.assertRaises(SendSmsException):
            self.create_sms_service.execute(None)

    def test_throws_exception_when_there_is_a_failure_sending_an_sms(self):
        """Test throws an exception when there is a failure sending an SMS"""
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

        self.mock_sms_service.send.side_effect = Exception

        with self.assertRaises(SendSmsException):
            self.create_sms_service.execute(sms=sms)

        self.mock_sms_service.send.assert_called_with(sms)
        self.mock_sms_response_repository.add.assert_not_called()

    def test_throws_exception_when_there_is_a_failure_saving_sms_response(self):
        """Test throws an exception when there is a failure saving sms response"""
        sender_phone = "+254700000000"
        sender = PhoneNumber(value=sender_phone)
        recipient_phone = "+254700000000"
        recipient = PhoneNumber(value=recipient_phone)
        message_text = fake.text()
        message = Message(value=message_text)

        date_created = fake.past_datetime()
        date_sent = fake.future_datetime()
        date_updated = fake.future_datetime()
        account_sid = fake.uuid4()
        sid = fake.uuid4()
        date_sent = date_sent
        date_updated = date_updated
        date_created = date_created
        direction = SmsType.OUTBOUND
        num_media = 0
        num_segments = 0
        price = 1.2
        currency = "USD"
        status = SmsDeliveryStatus.PENDING
        subresource_uris = {}
        uri = "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXX/Messages/SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.json"
        messaging_service_sid = fake.uuid4()
        error_code = None
        error_message = None

        sms = Sms(
            id=Sms.next_id(),
            sender=sender,
            recipient=recipient,
            message=message,
            status=SmsDeliveryStatus.PENDING
        )

        sms_date = SmsDate(
            date_sent=date_sent,
            date_updated=date_updated,
            date_created=date_created
        )

        sms_price = SmsPrice(
            price=price,
            currency=currency
        )

        sms_type = SmsType(direction)

        sms_response = SmsResponse(
            sms_id=sms.id.value,
            account_sid=account_sid,
            sid=sid,
            sms_date=sms_date,
            sms_type=sms_type,
            num_media=num_media,
            num_segments=num_segments,
            price=sms_price,
            status=status,
            subresource_uris=subresource_uris,
            uri=uri,
            messaging_service_sid=messaging_service_sid,
            error_code=error_code,
            error_message=error_message
        )

        self.mock_sms_service.send.return_value = sms_response
        self.mock_sms_response_repository.add.side_effect = Exception

        with self.assertRaises(SendSmsException):
            self.create_sms_service.execute(sms=sms)

        self.mock_sms_service.send.assert_called_with(sms)
        self.mock_sms_response_repository.add.assert_called_with(sms_response)

    def test_no_exception_is_thrown_and_sms_response_message_is_saved(self):
        """Test no exception is thrown & sms response is successfully created"""
        sender_phone = "+254700000000"
        sender = PhoneNumber(value=sender_phone)
        recipient_phone = "+254700000000"
        recipient = PhoneNumber(value=recipient_phone)
        message_text = fake.text()
        message = Message(value=message_text)

        date_created = fake.past_datetime()
        date_sent = fake.future_datetime()
        date_updated = fake.future_datetime()
        account_sid = fake.uuid4()
        sid = fake.uuid4()
        date_sent = date_sent
        date_updated = date_updated
        date_created = date_created
        direction = SmsType.OUTBOUND
        num_media = 0
        num_segments = 0
        price = 1.2
        currency = "USD"
        status = SmsDeliveryStatus.PENDING
        subresource_uris = {}
        uri = "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXX/Messages/SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.json"
        messaging_service_sid = fake.uuid4()
        error_code = None
        error_message = None

        sms = Sms(
            sender=sender,
            recipient=recipient,
            message=message,
            status=SmsDeliveryStatus.PENDING
        )

        sms_date = SmsDate(
            date_sent=date_sent,
            date_updated=date_updated,
            date_created=date_created
        )

        sms_price = SmsPrice(
            price=price,
            currency=currency
        )

        sms_type = SmsType(direction)

        sms_response = SmsResponse(
            sms_id=sms.id.value,
            account_sid=account_sid,
            sid=sid,
            sms_date=sms_date,
            sms_type=sms_type,
            num_media=num_media,
            num_segments=num_segments,
            price=sms_price,
            status=status,
            subresource_uris=subresource_uris,
            uri=uri,
            messaging_service_sid=messaging_service_sid,
            error_code=error_code,
            error_message=error_message
        )

        self.mock_sms_service.send.return_value = sms_response
        self.mock_sms_response_repository.add.return_value = sms_response

        self.create_sms_service.execute(sms=sms)

        self.mock_sms_service.send.assert_called_with(sms)
        self.mock_sms_response_repository.add.assert_called_with(sms_response)


if __name__ == '__main__':
    unittest.main()
