import unittest
import pytest
from faker import Faker
from app.database.models.sms_model import Sms
from . import BaseModelTestCases

fake = Faker()


@pytest.mark.unit
class SmsModelTestCases(BaseModelTestCases):

    def test_valid_sms_is_persisted(self):
        """Test that a valid SMS can be persisted"""
        with self.session() as session:
            sender_phone = "+254700000000"
            recipient_phone = "+254711111111"
            message = fake.text()

            sms = Sms(
                sender=sender_phone,
                recipient=recipient_phone,
                message=message
            )

            session.add(sms)
            session.commit()

            actual = session.query(Sms).filter_by(sender=sender_phone).first()

            self.assertEqual(sender_phone, actual.sender)
            self.assertEqual(recipient_phone, actual.recipient)
            self.assertEqual(message, actual.message)
            self.assertEqual("system", actual.updated_by)

    def test_2_valid_SMSes_can_be_persisted(self):
        """Test that 2 valid SMSes can be persisted"""
        with self.session() as session:
            sender_phone_one = f"{fake.country_calling_code()} {fake.msisdn()}"
            sender_phone_two = f"{fake.country_calling_code()} {fake.msisdn()}"
            recipient_phone_one = f"{fake.country_calling_code()} {fake.msisdn()}"
            recipient_phone_two = f"{fake.country_calling_code()} {fake.msisdn()}"
            message_one = fake.text()
            message_two = fake.text()

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

            session.add(sms_one)
            session.add(sms_two)
            session.commit()

            actual_one = session.query(Sms).filter_by(sender=sender_phone_one).first()
            actual_two = session.query(Sms).filter_by(sender=sender_phone_two).first()

            self.assertEqual(sender_phone_one, actual_one.sender)
            self.assertEqual(recipient_phone_one, actual_one.recipient)
            self.assertEqual(message_one, actual_one.message)

            self.assertEqual(sender_phone_two, actual_two.sender)
            self.assertEqual(recipient_phone_two, actual_two.recipient)
            self.assertEqual(message_two, actual_two.message)

    def test_2_valid_duplicate_SMSes_can_not_be_persisted(self):
        """Test that 2 valid duplicate SMSes can not be persisted"""
        with self.session() as session:
            sender_phone = f"{fake.country_calling_code()} {fake.msisdn()}"
            recipient_phone = f"{fake.country_calling_code()} {fake.msisdn()}"
            message = fake.text()

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

            session.add(sms_one)
            session.add(sms_two)

            with self.assertRaises(Exception):
                session.commit()


if __name__ == '__main__':
    unittest.main()
