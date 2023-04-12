import unittest
from unittest.mock import patch, Mock
import pytest
from faker import Faker
from faker.providers import lorem
from app.domain.entities.sms import Sms
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.message import Message
from app.domain.entities.sms_status import SmsDeliveryStatus
from app.infra.sms.sms_client import SmsClient, SmsClientParams, Client as TwilioRestClient
from app.infra.sms.exceptions import SmsClientException

fake = Faker()
fake.add_provider(lorem)

# mock/fake credentials
fake_account_sid = fake.uuid4()
fake_auth_token = fake.uuid4()
fake_messaging_service_sid = fake.uuid4()


@pytest.mark.unit
class SmsClientTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.sms_client = SmsClient(SmsClientParams(account_sid=fake_account_sid, auth_token=fake_auth_token,
                                                    messaging_service_sid=fake_messaging_service_sid))

    @patch.object(TwilioRestClient, "messages")
    def test_sends_sms_with_provided_sender(self, mock_twilio_client_messages: Mock):
        """SmsClient sends an SMS with provided sender"""
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

        self.sms_client.send(sms=mock_sms)

        mock_twilio_client_messages.create.assert_called_with(
            body=message_text,
            from_=sender_phone,
            to=recipient_phone
        )

    @patch.object(TwilioRestClient, "messages")
    def test_sends_sms_without_provided_sender(self, mock_twilio_client_messages: Mock):
        """SmsClient sends SMS without sender, defaulting to message_service_id"""
        recipient_phone = "+254700000000"
        recipient = PhoneNumber(value=recipient_phone)
        message_text = fake.text()
        message = Message(value=message_text)

        mock_sms = Sms(
            recipient=recipient,
            message=message,
            status=SmsDeliveryStatus.PENDING
        )

        self.sms_client.send(sms=mock_sms)

        mock_twilio_client_messages.create.assert_called_with(
            body=message_text,
            messaging_service_sid=fake_messaging_service_sid,
            to=recipient_phone
        )

    @patch.object(TwilioRestClient, "messages", side_effect=Exception)
    def test_throws_exception_when_client_fails_to_send_sms(self, mock_twilio_client_messages: Mock):
        """SmsClient throws an exception when there is a failure sending an sms"""
        recipient_phone = "+254700000000"
        recipient = PhoneNumber(value=recipient_phone)
        message_text = fake.text()
        message = Message(value=message_text)

        mock_sms = Sms(
            recipient=recipient,
            message=message,
            status=SmsDeliveryStatus.PENDING
        )

        # create a side effect to throw an exception
        mock_twilio_client_messages.create.side_effect = Exception

        with self.assertRaises(SmsClientException):
            self.sms_client.send(sms=mock_sms)

        mock_twilio_client_messages.create.assert_called_with(
            body=message_text,
            messaging_service_sid=fake_messaging_service_sid,
            to=recipient_phone
        )


if __name__ == '__main__':
    unittest.main()
