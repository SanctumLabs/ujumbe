import unittest
import pytest
from faker import Faker
from faker.providers import lorem
from app.domain.entities.message import Message

fake = Faker()
fake.add_provider(lorem)


@pytest.mark.unit
class MessageTestCases(unittest.TestCase):

    def test_valid_message_is_allowed(self):
        valid_message = fake.text()
        message = Message(value=valid_message)
        self.assertIsNotNone(message.value)
        self.assertEqual(message.value, valid_message)

    def test_invalid_message_is_not_allowed(self):
        invalid_message = fake.text(5000)
        with self.assertRaises(Exception):
            Message(value=invalid_message)


if __name__ == "__main__":
    unittest.main()
