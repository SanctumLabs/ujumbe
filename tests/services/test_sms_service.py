import unittest
from unittest.mock import Mock
from faker import Faker
from app.domain.entities.sms import Sms
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.message import Message
from app.domain.entities.sms_status import SmsDeliveryStatus
from app.services.sms_service import UjumbeSmsService, SmsClient
from app.services.exceptions import SmsSendingException
from app.infra.sms.dto import SmsResponseDto

fake = Faker()


class UjumbeSmsServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_sms_client = Mock(spec=SmsClient)
        self.sms_service = UjumbeSmsService(sms_client=self.mock_sms_client)

    def test_throws_exception_when_client_fails(self):
        """Throws Exception when sms client fails to send SMS"""
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

        self.mock_sms_client.send.side_effect = Exception

        with self.assertRaises(SmsSendingException):
            self.sms_service.send(sms=mock_sms)

        self.mock_sms_client.send.assert_called_with(mock_sms)

    def test_returns_sms_response_when_client_succeeds(self):
        """Returns SmsResponse when there is a success in sending out SMS with client"""
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

        mock_sms_response = SmsResponseDto(account_sid=fake.uuid4(), api_version=fake.date(),
                                           body=message_text,
                                           date_created=fake.date(), date_sent=fake.date(),
                                           date_updated=fake.date(), direction="outbound-api",
                                           error_code=None, error_message=None,
                                           from_=sender_phone, messaging_service_sid=fake.uuid4(),
                                           num_media="0", num_segments="1",
                                           price=None,
                                           price_unit=None, sid=fake.uuid4(), status="sent",
                                           subresource_uris={
                                            "media": ""
                                        }, to=recipient_phone, uri="")

        self.mock_sms_client.send.return_value = mock_sms_response

        actual = self.sms_service.send(sms=mock_sms)

        self.assertEquals(mock_sms_response, actual)

        self.mock_sms_client.send.assert_called_with(mock_sms)


if __name__ == '__main__':
    unittest.main()
