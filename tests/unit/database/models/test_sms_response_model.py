import unittest
from faker import Faker
import pytest
from app.database.models.sms_response_model import SmsResponse
from app.domain.entities.sms_type import SmsType
from app.domain.entities.sms_status import SmsDeliveryStatus
from . import BaseModelTestCases

fake = Faker()


@pytest.mark.unit
class SmsResponseModelTestCases(BaseModelTestCases):

    def test_valid_sms_response_is_persisted(self):
        """Test that a valid SMS Response can be persisted"""
        with self.session() as session:
            date_created = fake.past_datetime()
            date_sent = fake.future_datetime()
            date_updated = fake.future_datetime()
            sms_id = fake.uuid4()
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

            sms_response = SmsResponse(
                sms_id=sms_id,
                account_sid=account_sid,
                sid=sid,
                date_sent=date_sent,
                date_updated=date_updated,
                date_created=date_created,
                direction=direction,
                num_media=num_media,
                num_segments=num_segments,
                price=price,
                currency=currency,
                status=status,
                subresource_uris=subresource_uris,
                uri=uri,
                messaging_service_sid=messaging_service_sid,
                error_code=error_code,
                error_message=error_message
            )

            session.add(sms_response)
            session.commit()

            actual = session.query(SmsResponse).filter_by(sid=sid).first()

            self.assertEqual(account_sid, actual.account_sid)
            self.assertEqual(sid, actual.sid)
            self.assertEqual(date_sent, actual.date_sent)
            self.assertEqual(date_updated, actual.date_updated)
            self.assertEqual(direction, actual.direction)
            self.assertEqual(num_media, actual.num_media)
            self.assertEqual(num_segments, actual.num_segments)
            self.assertEqual(price, actual.price)
            self.assertEqual(currency, actual.currency)
            self.assertEqual(status, actual.status)
            self.assertEqual(subresource_uris, actual.subresource_uris)
            self.assertEqual(uri, actual.uri)
            self.assertEqual(messaging_service_sid, actual.messaging_service_sid)
            self.assertEqual(error_code, actual.error_code)
            self.assertEqual(error_message, actual.error_message)
            self.assertEqual("system", actual.updated_by)


if __name__ == '__main__':
    unittest.main()
