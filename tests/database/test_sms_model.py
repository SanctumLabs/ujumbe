import unittest
from faker import Faker
from app.infra.database.models import Base
from app.database.sms_model import Sms
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

fake = Faker()


class SmsModelTestCases(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)
        cls.session = sessionmaker(bind=cls.engine)

    @classmethod
    def tearDownClass(cls) -> None:
        with cls.session() as session:
            session.rollback()
            session.close()

    def tearDown(self) -> None:
        Base.metadata.drop_all(self.engine)

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


if __name__ == '__main__':
    unittest.main()
