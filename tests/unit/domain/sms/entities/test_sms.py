import unittest
import pytest
from faker import Faker
from app.domain.entities.sms import Sms
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.message import Message

fake = Faker()


@pytest.mark.unit
class SmsTestCases(unittest.TestCase):

    def test_new_sms_always_has_unique_id(self):
        phone = "+254700000000"
        phone_number = PhoneNumber(value=phone)
        message_text = fake.text()
        message = Message(value=message_text)

        sms = Sms(recipient=phone_number, message=message)

        self.assertIsNotNone(sms.id)
        self.assertEqual(phone, sms.recipient.value)
        self.assertEqual(message_text, sms.message.value)
        self.assertIsNone(sms.sender)

    def test_2_new_sms_always_have_unique_ids(self):
        """Test that 2 new Sms always have unique ids"""
        phone_one = "+254700000000"
        phone_two = "+254711111111"
        phone_number_one = PhoneNumber(value=phone_one)
        phone_number_two = PhoneNumber(value=phone_two)
        message_text_one = fake.text()
        message_text_two = fake.text()
        message_one = Message(value=message_text_one)
        message_two = Message(value=message_text_two)

        sms_one = Sms(id=Sms.next_id(), recipient=phone_number_one, message=message_one)
        sms_two = Sms(id=Sms.next_id(), recipient=phone_number_two, message=message_two)

        self.assertEqual(phone_one, sms_one.recipient.value)
        self.assertEqual(phone_two, sms_two.recipient.value)
        self.assertEqual(message_text_one, sms_one.message.value)
        self.assertEqual(message_text_two, sms_two.message.value)
        self.assertIsNone(sms_one.sender)
        self.assertIsNone(sms_two.sender)

        self.assertIsNotNone(sms_one.id)
        self.assertIsNotNone(sms_two.id)
        self.assertNotEqual(sms_one.id, sms_two.id)

    def test_new_sms_can_be_created_from_dictionary(self):
        phone = "+254700000000"
        message_text = fake.text()
        data = {
            'recipient': phone,
            'message': message_text
        }

        sms = Sms.from_dict(data)

        phone_number = PhoneNumber(value=phone)
        message = Message(value=message_text)

        self.assertEqual(sms.message, message)
        self.assertEqual(sms.recipient, phone_number)


if __name__ == "__main__":
    unittest.main()
