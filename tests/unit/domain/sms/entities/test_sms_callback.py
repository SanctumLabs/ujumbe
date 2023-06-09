import unittest
import pytest
from faker import Faker
from app.domain.entities.sms_callback import SmsCallback
from app.domain.entities.sms_status import SmsDeliveryStatus
from app.domain.entities.phone_number import PhoneNumber

fake = Faker()


@pytest.mark.unit
class SmsCallbackTestCases(unittest.TestCase):

    def test_new_sms_callback_always_has_unique_id(self):
        phone = "+254700000000"
        account_sid = fake.uuid4()
        message_sid = fake.uuid4()
        sms_sid = fake.uuid4()
        message_status = SmsDeliveryStatus.SENT
        sms_status = SmsDeliveryStatus.SENT
        phone_number = PhoneNumber(value=phone)

        sms_callback = SmsCallback(account_sid=account_sid, sender=phone_number, message_sid=message_sid,
                                   message_status=message_status, sms_sid=sms_sid, sms_status=sms_status)

        self.assertIsNotNone(sms_callback.id)
        self.assertEqual(phone, sms_callback.sender.value)
        self.assertEqual(account_sid, sms_callback.account_sid)
        self.assertEqual(message_sid, sms_callback.message_sid)
        self.assertEqual(message_status, sms_callback.message_status)
        self.assertEqual(sms_status, sms_callback.sms_status)
        self.assertEqual(sms_sid, sms_callback.sms_sid)

    def test_2_new_sms_callbacks_always_have_unique_ids(self):
        """Test that 2 new Sms Callbacks always have unique ids"""
        phone_one = "+254700000000"
        phone_two = "+254711111111"
        phone_number_one = PhoneNumber(value=phone_one)
        phone_number_two = PhoneNumber(value=phone_two)

        account_sid_one = fake.uuid4()
        account_sid_two = fake.uuid4()

        message_sid_one = fake.uuid4()
        message_sid_two = fake.uuid4()

        sms_sid_one = fake.uuid4()
        sms_sid_two = fake.uuid4()

        message_status_one = SmsDeliveryStatus.SENT
        message_status_two = SmsDeliveryStatus.SENT

        sms_status_one = SmsDeliveryStatus.SENT
        sms_status_two = SmsDeliveryStatus.SENT

        sms_callback_one = SmsCallback(account_sid=account_sid_one, sender=phone_number_one,
                                       message_sid=message_sid_one,
                                       message_status=message_status_one, sms_sid=sms_sid_one,
                                       sms_status=sms_status_one)

        sms_callback_two = SmsCallback(account_sid=account_sid_two, sender=phone_number_two,
                                       message_sid=message_sid_two,
                                       message_status=message_status_two, sms_sid=sms_sid_two,
                                       sms_status=sms_status_two)

        self.assertIsNotNone(sms_callback_one.id)
        self.assertEqual(phone_one, sms_callback_one.sender.value)
        self.assertEqual(account_sid_one, sms_callback_one.account_sid)
        self.assertEqual(message_sid_one, sms_callback_one.message_sid)
        self.assertEqual(message_status_one, sms_callback_one.message_status)
        self.assertEqual(sms_status_one, sms_callback_one.sms_status)
        self.assertEqual(sms_sid_one, sms_callback_one.sms_sid)

        self.assertIsNotNone(sms_callback_two.id)
        self.assertEqual(phone_two, sms_callback_two.sender.value)
        self.assertEqual(account_sid_two, sms_callback_two.account_sid)
        self.assertEqual(message_sid_two, sms_callback_two.message_sid)
        self.assertEqual(message_status_two, sms_callback_two.message_status)
        self.assertEqual(sms_status_two, sms_callback_two.sms_status)
        self.assertEqual(sms_sid_two, sms_callback_two.sms_sid)

        self.assertNotEqual(sms_callback_one.id, sms_callback_two.id)

    def test_new_sms_callback_can_be_created_from_dictionary(self):
        phone = "+254700000000"
        account_sid = fake.uuid4()
        message_sid = fake.uuid4()
        sms_sid = fake.uuid4()
        msg_status = "sent"
        status = "sent"

        data = {
            'AccountSid': account_sid,
            'From': phone,
            'MessageSid': message_sid,
            'MessageStatus': msg_status,
            'SmsSid': sms_sid,
            'SmsStatus': status,
        }

        sms_callback = SmsCallback.from_dict(data)

        phone_number = PhoneNumber(value=phone)
        message_status = SmsDeliveryStatus.SENT
        sms_status = SmsDeliveryStatus.SENT

        self.assertEqual(sms_callback.account_sid, account_sid)
        self.assertEqual(sms_callback.sender, phone_number)
        self.assertEqual(sms_callback.message_sid, message_sid)
        self.assertEqual(sms_callback.message_status, message_status)
        self.assertEqual(sms_callback.sms_sid, sms_sid)
        self.assertEqual(sms_callback.sms_status, sms_status)


if __name__ == "__main__":
    unittest.main()
