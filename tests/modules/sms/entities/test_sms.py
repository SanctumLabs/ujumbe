import unittest
from faker import Faker
from app.domain.entities.sms import Sms
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.message import Message

fake = Faker()


class SmsTestCases(unittest.TestCase):

    def test_new_sms_always_has_unique_id(self):
        phone = "+254700000000"
        phone_number = PhoneNumber(value=phone)
        message_text = fake.text()
        message = Message(value=message_text)

        sms = Sms(recipient=phone_number, message=message)

        self.assertIsNotNone(sms.id.value)
        self.assertEqual(phone, sms.recipient.value)
        self.assertEqual(message_text, sms.message.value)
        self.assertIsNone(sms.sender)

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
