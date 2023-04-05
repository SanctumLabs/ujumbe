import unittest
from faker import Faker
from app.domain.entities.sms_price import SmsPrice

fake = Faker()


class SmsPriceTestCases(unittest.TestCase):

    def test_new_sms_price_returns_valid_values(self):
        price = "2.3"
        currency = fake.currency_code()
        sms_price = SmsPrice(price=price, currency=currency)

        self.assertIsNotNone(sms_price)
        self.assertEqual(price, sms_price.price)
        self.assertEqual(currency, sms_price.currency)

    def test_new_sms_price_returns_valid_amount(self):
        price = "2.3"
        currency = fake.currency_code()
        sms_price = SmsPrice(price=price, currency=currency)

        self.assertIsNotNone(sms_price)
        self.assertEqual(price, sms_price.price)
        self.assertEqual(currency, sms_price.currency)
        self.assertEqual(2.3, sms_price.amount)

    def test_new_sms_price_throws_exception_for_invalid_price(self):
        price = "abc"
        currency = fake.currency_code()
        with self.assertRaises(ValueError):
            SmsPrice(price=price, currency=currency)


if __name__ == "__main__":
    unittest.main()
