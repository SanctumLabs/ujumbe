import unittest
from faker import Faker

import pytest

from app.domain.entities.sms import Sms
from app.database.models.sms_model import Sms as SmsModel
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.message import Message
from app.domain.entities.sms_status import SmsDeliveryStatus
from app.domain.services.exceptions import SmsNotFoundError

from app.database.sms_repository import SmsDatabaseRepository

from . import BaseIntegrationTestCases

fake = Faker()


@pytest.mark.integration
class SmsIntegrationTestCases(BaseIntegrationTestCases):
    def setUp(self) -> None:
        super().setUp()
        self.sms_repository = SmsDatabaseRepository(self.client)

    def test_persists_a_valid_sms(self):
        """Test that a valid SMS can be persisted"""
        sender_phone_number = "+254722222222"
        recipient_phone_number = "+254733333333"
        message_text = fake.text()

        sender_phone = PhoneNumber(value=sender_phone_number)
        recipient_phone = PhoneNumber(value=recipient_phone_number)
        message = Message(value=message_text)

        sms = Sms(
            id=Sms.next_id(),
            sender=sender_phone,
            recipient=recipient_phone,
            message=message,
        )

        self.sms_repository.add(sms)

        with self.client.session_factory() as session:
            actual = (
                session.query(SmsModel).filter_by(sender=sender_phone_number).first()
            )

            self.assertEqual(sender_phone_number, actual.sender)
            self.assertEqual(recipient_phone_number, actual.recipient)
            self.assertEqual("system", actual.updated_by)
            self.assertEqual(message_text, actual.message)

    def test_fails_to_persist_duplicate_valid_sms(self):
        """Test that 2 valid duplicate SMSes can not be persisted"""
        sender_phone_number = "+254700000000"
        recipient_phone_number = "+254711111111"
        message_text = fake.text()

        sender_phone = PhoneNumber(value=sender_phone_number)
        recipient_phone = PhoneNumber(value=recipient_phone_number)
        message = Message(value=message_text)

        sms_one = Sms(sender=sender_phone, recipient=recipient_phone, message=message)

        sms_two = Sms(sender=sender_phone, recipient=recipient_phone, message=message)

        with self.assertRaises(Exception):
            self.sms_repository.add(sms_one)
            self.sms_repository.add(sms_two)

    def test_persists_2_valid_smses(self):
        """Test that 2 valid SMSes can be persisted"""
        sender_phone_number_one = "+254744444444"
        sender_phone_number_two = "+254712121212"
        recipient_phone_number_one = "+254755555555"
        recipient_phone_number_two = "+254723232323"
        message_text_one = fake.text()
        message_text_two = fake.text()

        sender_phone_one = PhoneNumber(value=sender_phone_number_one)
        sender_phone_two = PhoneNumber(value=sender_phone_number_two)
        recipient_phone_one = PhoneNumber(value=recipient_phone_number_one)
        recipient_phone_two = PhoneNumber(value=recipient_phone_number_two)
        message_one = Message(value=message_text_one)
        message_two = Message(value=message_text_two)

        sms_one = Sms(
            id=Sms.next_id(),
            sender=sender_phone_one,
            recipient=recipient_phone_one,
            message=message_one,
        )

        sms_two = Sms(
            id=Sms.next_id(),
            sender=sender_phone_two,
            recipient=recipient_phone_two,
            message=message_two,
        )

        self.sms_repository.add(sms_one)
        self.sms_repository.add(sms_two)

        with self.client.session_factory() as session:
            actual_one = (
                session.query(SmsModel)
                .filter_by(sender=sender_phone_number_one)
                .first()
            )
            actual_two = (
                session.query(SmsModel)
                .filter_by(sender=sender_phone_number_two)
                .first()
            )

            self.assertEqual(sender_phone_number_one, actual_one.sender)
            self.assertEqual(recipient_phone_number_one, actual_one.recipient)
            self.assertEqual(message_text_one, actual_one.message)
            self.assertEqual("system", actual_one.updated_by)

            self.assertEqual(sender_phone_number_two, actual_two.sender)
            self.assertEqual(recipient_phone_number_two, actual_two.recipient)
            self.assertEqual(message_text_two, actual_two.message)
            self.assertEqual("system", actual_two.updated_by)

    def test_get_by_id_returns_persisted_sms(self):
        """Test that repository can retrieve initially persisted SMS given its ID"""
        sender_phone_number = "+254744444444"
        recipient_phone_number = "+254755555555"
        message_text = fake.text()

        sid = Sms.next_id()
        sender_phone = PhoneNumber(value=sender_phone_number)
        recipient_phone = PhoneNumber(value=recipient_phone_number)
        message = Message(value=message_text)

        sms = Sms(
            id=sid, sender=sender_phone, recipient=recipient_phone, message=message
        )

        with self.client.session_factory() as session:
            sms_model = SmsModel(
                identifier=sms.id.value,
                sender=sms.sender.value,
                recipient=sms.recipient.value,
                message=sms.message.value,
                status=sms.status,
            )

            session.add(sms_model)
            session.commit()

        actual = self.sms_repository.get_by_id(sid.value)

        self.assertEqual(sid.value, actual.id.value)
        self.assertEqual(sender_phone_number, actual.sender.value)
        self.assertEqual(recipient_phone_number, actual.recipient.value)
        self.assertEqual(message_text, actual.message.value)

    def test_get_by_id_throws_sms_not_found_exception_when_sms_does_not_exist(self):
        """Test that repository throws SmsNotFoundError when SMS with given ID can not be found"""

        sid = Sms.next_id()

        with self.assertRaises(SmsNotFoundError):
            self.sms_repository.get_by_id(sid.value)

    def test_returns_all_persisted_valid_smses(self):
        """Should return all valid SMSes"""
        sender_phone_number_one = "+254744444444"
        sender_phone_number_two = "+254712121212"
        recipient_phone_number_one = "+254755555555"
        recipient_phone_number_two = "+254723232323"
        message_text_one = fake.text()
        message_text_two = fake.text()

        sender_phone_one = PhoneNumber(value=sender_phone_number_one)
        sender_phone_two = PhoneNumber(value=sender_phone_number_two)
        recipient_phone_one = PhoneNumber(value=recipient_phone_number_one)
        recipient_phone_two = PhoneNumber(value=recipient_phone_number_two)
        message_one = Message(value=message_text_one)
        message_two = Message(value=message_text_two)

        sms_one = Sms(
            id=Sms.next_id(),
            sender=sender_phone_one,
            recipient=recipient_phone_one,
            message=message_one,
        )

        sms_two = Sms(
            id=Sms.next_id(),
            sender=sender_phone_two,
            recipient=recipient_phone_two,
            message=message_two,
        )

        with self.client.session_factory() as session:
            sms_model_one = SmsModel(
                identifier=sms_one.id.value,
                sender=sms_one.sender.value,
                recipient=sms_one.recipient.value,
                message=sms_one.message.value,
                status=sms_one.status,
            )
            sms_model_two = SmsModel(
                identifier=sms_two.id.value,
                sender=sms_two.sender.value,
                recipient=sms_two.recipient.value,
                message=sms_two.message.value,
                status=sms_two.status,
            )

            session.add(sms_model_one)
            session.add(sms_model_two)
            session.commit()

        actual = self.sms_repository.get_all()

        self.assertEqual(len(actual), 2)
        self.assertListEqual(actual, [sms_one, sms_two])

    def test_updates_status_of_persisted_sms(self):
        """Should update the status of a persisted SMS"""
        sender_phone_number = "+254744444444"
        recipient_phone_number = "+254755555555"
        message_text = fake.text()

        sid = Sms.next_id()
        sender_phone = PhoneNumber(value=sender_phone_number)
        recipient_phone = PhoneNumber(value=recipient_phone_number)
        message = Message(value=message_text)

        sms = Sms(
            id=sid, sender=sender_phone, recipient=recipient_phone, message=message
        )

        status = SmsDeliveryStatus.SENT
        updated_sms = Sms(
            id=sid,
            sender=sender_phone,
            recipient=recipient_phone,
            message=message,
            status=status,
        )

        with self.client.session_factory() as session:
            sms_model = SmsModel(
                identifier=sms.id.value,
                sender=sms.sender.value,
                recipient=sms.recipient.value,
                message=sms.message.value,
                status=sms.status,
            )

            session.add(sms_model)
            session.commit()

        self.sms_repository.update(updated_sms)

        with self.client.session_factory() as session:
            actual = session.query(SmsModel).filter_by(identifier=sid.value).first()

            self.assertEqual(sender_phone_number, actual.sender)
            self.assertEqual(recipient_phone_number, actual.recipient)
            self.assertEqual(message_text, actual.message)
            self.assertEqual(status, actual.status)
            self.assertEqual("system", actual.updated_by)

    def test_raises_exception_when_updating_an_sms_that_does_not_exist(self):
        """Should raise SmsNotFoundException when updating the status of an SMS that does not exist"""
        sender_phone_number = "+254744444444"
        recipient_phone_number = "+254755555555"
        message_text = fake.text()

        sid = Sms.next_id()
        sender_phone = PhoneNumber(value=sender_phone_number)
        recipient_phone = PhoneNumber(value=recipient_phone_number)
        message = Message(value=message_text)

        status = SmsDeliveryStatus.SENT
        updated_sms = Sms(
            id=sid,
            sender=sender_phone,
            recipient=recipient_phone,
            message=message,
            status=status,
        )

        with self.assertRaises(SmsNotFoundError):
            self.sms_repository.update(updated_sms)

    def test_raises_exception_when_removing_an_sms_that_does_not_exist(self):
        """Should raise SmsNotFoundException when removing an SMS that does not exist"""
        sender_phone_number = "+254744444444"
        recipient_phone_number = "+254755555555"
        message_text = fake.text()

        sid = Sms.next_id()
        sender_phone = PhoneNumber(value=sender_phone_number)
        recipient_phone = PhoneNumber(value=recipient_phone_number)
        message = Message(value=message_text)
        status = SmsDeliveryStatus.SENT

        sms = Sms(
            id=sid,
            sender=sender_phone,
            recipient=recipient_phone,
            message=message,
            status=status,
        )

        with self.assertRaises(SmsNotFoundError):
            self.sms_repository.remove(sms)

    def test_removes_initially_persisted_sms(self):
        """Should remove an initially persisted SMS"""
        sender_phone_number = "+254744444444"
        recipient_phone_number = "+254755555555"
        message_text = fake.text()

        sid = Sms.next_id()
        sender_phone = PhoneNumber(value=sender_phone_number)
        recipient_phone = PhoneNumber(value=recipient_phone_number)
        message = Message(value=message_text)

        sms = Sms(
            id=sid, sender=sender_phone, recipient=recipient_phone, message=message
        )

        with self.client.session_factory() as session:
            sms_model = SmsModel(
                identifier=sms.id.value,
                sender=sms.sender.value,
                recipient=sms.recipient.value,
                message=sms.message.value,
                status=sms.status,
            )

            session.add(sms_model)
            session.commit()

        self.sms_repository.remove(sms)

        with self.client.session_factory() as session:
            actual = session.query(SmsModel).filter_by(identifier=sid.value).first()
            self.assertIsNone(actual)


if __name__ == "__main__":
    unittest.main()
