import unittest
from faker import Faker

from app.domain.entities.sms import Sms
from app.database.sms_model import Sms as SmsModel
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.message import Message

from app.database.sms_repository import SmsDatabaseRepository
from . import BaseIntegrationTestCases

fake = Faker()


class SmsIntegrationTestCases(BaseIntegrationTestCases):
    def setUp(self) -> None:
        self.sms_repository = SmsDatabaseRepository(self.client)

    def test_persists_a_valid_sms(self):
        """Test that a valid SMS can be persisted"""
        sender_phone_number = "+254722222222"
        recipient_phone_number = "+254733333333"
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
            actual = session.query(SmsModel).filter_by(sender=sender_phone_number).first()

            self.assertEqual(sender_phone_number, actual.sender)
            self.assertEqual(recipient_phone_number, actual.recipient)
            self.assertEqual("system", actual.updated_by)
            self.assertEqual(message_text, actual.message)

    def test_fails_to_persist_duplicate_valid_sms(self):
        """Test that 2 valid duplicate SMSes can not be persisted"""
        sender_phone_number = "+254700000000"
        recipient_phone_number = "+254711111111"
        message_text = fake.text()

        sender_phone = PhoneNumber(value=sender_phone_number)
        recipient_phone = PhoneNumber(value=recipient_phone_number)
        message = Message(value=message_text)

        sms_one = Sms(
            sender=sender_phone,
            recipient=recipient_phone,
            message=message
        )

        sms_two = Sms(
            sender=sender_phone,
            recipient=recipient_phone,
            message=message
        )

        with self.assertRaises(Exception):
            self.sms_repository.add(sms_one)
            self.sms_repository.add(sms_two)

    def test_persists_2_valid_smses(self):
        """Test that 2 valid SMSes can be persisted"""
        sender_phone_number_one = "+254744444444"
        sender_phone_number_two = "+254712121212"
        recipient_phone_number_one = "+254755555555"
        recipient_phone_number_two = "+254723232323"
        message_text_one = fake.text()
        message_text_two = fake.text()

        sender_phone_one = PhoneNumber(value=sender_phone_number_one)
        sender_phone_two = PhoneNumber(value=sender_phone_number_two)
        recipient_phone_one = PhoneNumber(value=recipient_phone_number_one)
        recipient_phone_two = PhoneNumber(value=recipient_phone_number_two)
        message_one = Message(value=message_text_one)
        message_two = Message(value=message_text_two)

        sms_one = Sms(
            sender=sender_phone_one,
            recipient=recipient_phone_one,
            message=message_one
        )

        sms_two = Sms(
            sender=sender_phone_two,
            recipient=recipient_phone_two,
            message=message_two
        )

        saved_sms_one = self.sms_repository.add(sms_one)
        saved_sms_two = self.sms_repository.add(sms_two)

        with self.client.session_factory() as session:
            actual_one = session.query(SmsModel).filter_by(sender=sender_phone_number_one).first()
            actual_two = session.query(SmsModel).filter_by(sender=sender_phone_number_two).first()

            self.assertEqual(sender_phone_number_one, actual_one.sender)
            self.assertEqual(recipient_phone_number_one, actual_one.recipient)
            self.assertEqual(message_text_one, actual_one.message)
            self.assertEqual("system", actual_one.updated_by)

            self.assertEqual(sender_phone_number_two, actual_two.sender)
            self.assertEqual(recipient_phone_number_two, actual_two.recipient)
            self.assertEqual(message_text_two, actual_two.message)
            self.assertEqual("system", actual_two.updated_by)


if __name__ == '__main__':
    unittest.main()
