import unittest
from faker import Faker
import pytest
from app.database.models.sms_model import Sms
from app.database.models.sms_callback_model import SmsCallback
from app.domain.entities.sms_status import SmsDeliveryStatus
from . import BaseModelTestCases

fake = Faker()


@pytest.mark.unit
class SmsCallbackModelTestCases(BaseModelTestCases):

    def test_valid_sms_callback_is_persisted(self):
        """Test that a valid SMS Callback can be persisted"""
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

            saved_sms = session.query(Sms).filter_by(id=sms.id).first()

            account_sid = fake.uuid4()
            sms_sid = fake.uuid4()
            sms_status = SmsDeliveryStatus.PENDING
            message_sid = fake.uuid4()
            message_status = SmsDeliveryStatus.PENDING

            sms_callback = SmsCallback(
                sms_id=saved_sms.id,
                account_sid=account_sid,
                from_=sender_phone,
                sms_sid=sms_sid,
                sms_status=sms_status,
                message_sid=message_sid,
                message_status=message_status,
            )

            session.add(sms_callback)
            session.commit()

            actual = session.query(SmsCallback).filter_by(sms_sid=sms_sid).first()

            self.assertEqual(account_sid, actual.account_sid)
            self.assertEqual(sms_sid, actual.sms_sid)
            self.assertEqual(sms_status, actual.sms_status)
            self.assertEqual(message_sid, actual.message_sid)
            self.assertEqual(message_status, actual.message_status)
            self.assertEqual("system", actual.updated_by)


if __name__ == '__main__':
    unittest.main()
