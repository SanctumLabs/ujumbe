import unittest
from datetime import datetime
import pytest
from faker import Faker

from app.domain.entities.sms_date import SmsDate

fake = Faker()


@pytest.mark.unit
class SmsDateTestCase(unittest.TestCase):
    def test_correct_dates_can_be_used_to_create_sms_date(self):
        date_created = fake.past_datetime()
        date_sent = fake.future_datetime()
        date_updated = fake.future_datetime()

        sms_date = SmsDate(date_created=date_created, date_sent=date_sent, date_updated=date_updated)

        self.assertEqual(date_created, sms_date.date_created)
        self.assertEqual(date_updated, sms_date.date_updated)
        self.assertEqual(date_sent, sms_date.date_sent)

    def test_correct_dates_strings_can_be_used_to_create_sms_date(self):
        pattern = "%d, %B %Y %H:%M:%S +0000"
        date_created = datetime(year=2022, month=1, day=1, hour=1, minute=1, second=1).strftime(pattern)
        date_sent = datetime(year=2023, month=2, day=1, hour=1, minute=1, second=1).strftime(pattern)
        date_updated = datetime(year=2023, month=2, day=1, hour=1, minute=1, second=1).strftime(pattern)

        sms_date = SmsDate(date_created=date_created, date_sent=date_sent, date_updated=date_updated)

        self.assertEqual(date_created, sms_date.date_created)
        self.assertEqual(date_updated, sms_date.date_updated)
        self.assertEqual(date_sent, sms_date.date_sent)

    def test_invalid_dates_throw_error_when_creating_sms_date(self):
        pattern = "%d, %B %Y %H:%M:%S +0000"
        date_created = datetime(year=2023, month=3, day=1, hour=1, minute=1, second=1).strftime(pattern)
        date_sent = datetime(year=2023, month=2, day=1, hour=1, minute=1, second=1).strftime(pattern)
        date_updated = datetime(year=2023, month=2, day=1, hour=1, minute=1, second=1).strftime(pattern)

        with self.assertRaises(ValueError):
            SmsDate(date_created=date_created, date_sent=date_sent, date_updated=date_updated)


if __name__ == '__main__':
    unittest.main()
