import unittest
from faker import Faker

from app.domain.entities.sms import Sms
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.message import Message

from app.database.sms_repository import SmsDatabaseRepository
from . import BaseIntegrationTestCases

fake = Faker()


class SmsIntegrationTestCases(BaseIntegrationTestCases):
    def setUp(self) -> None:
        self.sms_repository = SmsDatabaseRepository(self.client)

    def test_persists_a_valid_sms(self):
        """Test that valid duplicate SMSes can not be persisted"""
        sender_phone_number = "+254700000000"
        recipient_phone_number = "+254711111111"
        message_text = fake.text()

        sender_phone = PhoneNumber(value=sender_phone_number)
        recipient_phone = PhoneNumber(value=recipient_phone_number)
        message = Message(value=message_text)

        sms = Sms(
            sender=sender_phone,
            recipient=recipient_phone,
            message=message
        )

        self.sms_repository.add(sms)

        with self.client.session_factory() as session:
            actual = session.query(Sms).filter_by(sender=sender_phone).first()

            self.assertEqual(sender_phone, actual.sender)
            self.assertEqual(recipient_phone, actual.recipient)
            self.assertEqual(message, actual.message)
            self.assertEqual("system", actual.updated_by)


if __name__ == '__main__':
    unittest.main()
