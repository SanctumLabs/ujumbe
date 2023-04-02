import unittest
from app.domain.entities.phone_number import PhoneNumber


class PhoneNumberTestCases(unittest.TestCase):
    def test_valid_phone_number_is_allowed(self):
        valid_number = "+254700000000"
        phone_number = PhoneNumber(value=valid_number)
        self.assertIsNotNone(phone_number.value)
        self.assertEqual(phone_number.value, valid_number)

    def test_invalid_phone_number_is_not_allowed(self):
        invalid_number = "+254700000"
        with self.assertRaises(Exception):
            PhoneNumber(value=invalid_number)


if __name__ == "__main__":
    unittest.main()
