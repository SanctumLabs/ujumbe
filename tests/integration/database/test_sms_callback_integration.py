import unittest
from dataclasses import replace
from faker import Faker

import pytest

from app.domain.entities.sms_callback import SmsCallback
from app.database.models.sms_callback_model import SmsCallback as SmsCallbackModel
from app.domain.entities.sms_status import SmsDeliveryStatus

from app.database.sms_callback_repository import SmsCallbackDatabaseRepository, SmsCallbackNotFoundError
from .base_test_sms import BaseSmsIntegrationTestCases
from ...mocks.mock_data import create_mock_sms_response, create_mock_sms_callback

fake = Faker()


@pytest.mark.integration
class SmsCallbackIntegrationTestCases(BaseSmsIntegrationTestCases):
    def setUp(self) -> None:
        super().setUp()
        self.sms_callback_repository = SmsCallbackDatabaseRepository(self.client)

    def test_persists_a_valid_sms_callback(self):
        """Test that a valid SMS Callback can be persisted"""
        sender_phone_number = "+254722222222"
        recipient_phone_number = "+254733333333"
        message_text = fake.text()

        # create an existing SMS record first
        sms = self.create_and_persist_sms(sender=sender_phone_number, recipient=recipient_phone_number,
                                          message=message_text)

        mock_sms_response = create_mock_sms_response(sms_identifier=sms.identifier)

        # create an existing SMS response record as well
        self.create_and_persist_sms_response(sms_response=mock_sms_response, sms_id=sms.id)

        sms_sid = mock_sms_response.sid
        message_sid = mock_sms_response.messaging_service_sid

        # create sms callback
        sms_callback = create_mock_sms_callback(
            sender_phone_number=sender_phone_number,
            message_sid=message_sid,
            sms_sid=sms_sid
        )

        self.sms_callback_repository.add(sms_callback)

        # check the sms callback was persisted correctly
        with self.client.session_factory() as session:
            actual = session.query(SmsCallbackModel).filter_by(sms_sid=sms_callback.sms_sid).first()

            self.assertEqual(sms_callback.account_sid, actual.account_sid)
            self.assertEqual(sms_callback.sender.value, actual.from_)
            self.assertEqual(sms_callback.message_sid, actual.message_sid)
            self.assertEqual(sms_callback.message_status, actual.message_status)
            self.assertEqual(sms_callback.sms_sid, actual.sms_sid)
            self.assertEqual(sms_callback.sms_status, actual.sms_status)

            # was this callback persisted with the correct SMS record?
            self.assertEqual(sms.id, actual.sms.id)

    def test_persists_duplicate_valid_sms_callback(self):
        """Test that 2 valid duplicate SMS Callbacks can not be persisted. This is in the case of the callback having a
        different message status"""
        sender_phone_number = "+254700000000"
        recipient_phone_number = "+254711111111"
        message_text = fake.text()

        # create an existing SMS record first
        sms = self.create_and_persist_sms(sender=sender_phone_number, recipient=recipient_phone_number,
                                          message=message_text)

        mock_sms_response = create_mock_sms_response(sms_identifier=sms.identifier)

        # create an existing SMS response record as well
        self.create_and_persist_sms_response(sms_response=mock_sms_response, sms_id=sms.id)

        initial_sms_callback = create_mock_sms_callback(
            sender_phone_number=sender_phone_number,
            sms_sid=mock_sms_response.sid,
            message_sid=mock_sms_response.messaging_service_sid
        )

        # create an existing SMS callback record
        self.create_and_persist_sms_callback(sms_callback=initial_sms_callback, sms_id=sms.id)

        second_message_status = SmsDeliveryStatus.DELIVERED

        second_sms_callback = create_mock_sms_callback(
            sender_phone_number=sender_phone_number,
            message_sid=mock_sms_response.messaging_service_sid,
            message_status=second_message_status,
            sms_sid=mock_sms_response.sid,
        )

        self.sms_callback_repository.add(second_sms_callback)

        # check the second sms callback was persisted correctly by updating the initial sms callback
        with self.client.session_factory() as session:
            actual = session.query(SmsCallbackModel).filter_by(sms_sid=second_sms_callback.sms_sid).first()

            self.assertEqual(second_sms_callback.account_sid, actual.account_sid)
            self.assertEqual(second_sms_callback.sender.value, actual.from_)
            self.assertEqual(second_sms_callback.message_sid, actual.message_sid)
            self.assertEqual(second_sms_callback.message_status, actual.message_status)
            self.assertEqual(second_sms_callback.sms_sid, actual.sms_sid)
            self.assertEqual(second_sms_callback.sms_status, actual.sms_status)

            # was this second callback persisted with the correct SMS record?
            self.assertEqual(sms.id, actual.sms.id)

    def test_persists_2_valid_sms_callbacks(self):
        """Test that 2 valid SMS Callbacks can be persisted"""
        sender_phone_number_one = "+254744444444"
        sender_phone_number_two = "+254712121212"
        recipient_phone_number_one = "+254755555555"
        recipient_phone_number_two = "+254723232323"
        message_text_one = fake.text()
        message_text_two = fake.text()

        # create sms records
        sms_one = self.create_and_persist_sms(sender=sender_phone_number_one, recipient=recipient_phone_number_one,
                                              message=message_text_one)
        sms_two = self.create_and_persist_sms(sender=sender_phone_number_two,
                                              recipient=recipient_phone_number_two,
                                              message=message_text_two)

        mock_sms_response_one = create_mock_sms_response(sms_identifier=sms_one.identifier)
        mock_sms_response_two = create_mock_sms_response(sms_identifier=sms_two.identifier)

        # create sms responses for above sms records
        self.create_and_persist_sms_response(sms_response=mock_sms_response_one, sms_id=sms_one.id)
        self.create_and_persist_sms_response(sms_response=mock_sms_response_two, sms_id=sms_two.id)

        # create sms callbacks for above sms records
        sms_callback_one = create_mock_sms_callback(
            sender_phone_number=sender_phone_number_one,
            message_sid=mock_sms_response_one.messaging_service_sid,
            sms_sid=mock_sms_response_one.sid,
        )

        sms_callback_two = create_mock_sms_callback(
            sender_phone_number=sender_phone_number_two,
            message_sid=mock_sms_response_two.messaging_service_sid,
            sms_sid=mock_sms_response_two.sid,
        )

        # add the sms callbacks
        self.sms_callback_repository.add(sms_callback_one)
        self.sms_callback_repository.add(sms_callback_two)

        # check that both have been persisted correctly
        with self.client.session_factory() as session:
            actual_one = session.query(SmsCallbackModel).filter_by(sms_sid=sms_callback_one.sms_sid).first()
            actual_two = session.query(SmsCallbackModel).filter_by(sms_sid=sms_callback_two.sms_sid).first()

            self.assertEqual(sms_callback_one.account_sid, actual_one.account_sid)
            self.assertEqual(sms_callback_one.sms_sid, actual_one.sms_sid)
            self.assertEqual(sms_callback_one.sms_status, actual_one.sms_status)
            self.assertEqual(sms_callback_one.message_sid, actual_one.message_sid)
            self.assertEqual(sms_callback_one.message_status, actual_one.message_status)
            self.assertEqual(sms_callback_one.sender.value, actual_one.from_)
            self.assertEqual("system", actual_one.updated_by)

            self.assertEqual(sms_callback_two.account_sid, actual_two.account_sid)
            self.assertEqual(sms_callback_two.sms_sid, actual_two.sms_sid)
            self.assertEqual(sms_callback_two.sms_status, actual_two.sms_status)
            self.assertEqual(sms_callback_two.message_sid, actual_two.message_sid)
            self.assertEqual(sms_callback_two.message_status, actual_two.message_status)
            self.assertEqual(sms_callback_two.sender.value, actual_two.from_)
            self.assertEqual("system", actual_two.updated_by)

    def test_get_by_id_returns_persisted_sms_callback(self):
        """Test that repository can retrieve initially persisted SMS Callback given its ID"""
        sender_phone_number = "+254744444444"
        recipient_phone_number = "+254755555555"
        message_text = fake.text()

        # persist an SMS
        sms = self.create_and_persist_sms(sender=sender_phone_number, recipient=recipient_phone_number,
                                          message=message_text)

        mock_sms_response = create_mock_sms_response(sms_identifier=sms.identifier)

        # Persist an SMS response
        self.create_and_persist_sms_response(mock_sms_response, sms_id=sms.id)

        sms_sid = mock_sms_response.sid
        message_sid = mock_sms_response.messaging_service_sid

        mock_sms_callback = create_mock_sms_callback(
            sender_phone_number=sender_phone_number,
            message_sid=message_sid,
            sms_sid=sms_sid
        )

        # create an existing SMS callback record
        self.create_and_persist_sms_callback(mock_sms_callback, sms.id)

        actual = self.sms_callback_repository.get_by_id(mock_sms_callback.id.value)

        self.assertEqual(mock_sms_callback.account_sid, actual.account_sid)
        self.assertEqual(mock_sms_callback.sms_sid, actual.sms_sid)
        self.assertEqual(mock_sms_callback.sms_status, actual.sms_status)
        self.assertEqual(mock_sms_callback.message_status, actual.message_status)
        self.assertEqual(mock_sms_callback.message_sid, actual.message_sid)
        self.assertEqual(mock_sms_callback.sender.value, actual.sender.value)

    def test_get_by_id_throws_sms_not_found_exception_when_sms_callback_does_not_exist(self):
        """Test that repository throws SmsCallbackNotFoundError when SMS callback with given ID can not be found"""

        sid = SmsCallback.next_id()

        with self.assertRaises(SmsCallbackNotFoundError):
            self.sms_callback_repository.get_by_id(sid.value)

    def test_returns_all_persisted_valid_sms_callbacks(self):
        """Should return all valid SMS callbacks"""
        self.maxDiff = None
        sender_phone_number_one = "+254744444444"
        sender_phone_number_two = "+254712121212"
        recipient_phone_number_one = "+254755555555"
        recipient_phone_number_two = "+254723232323"
        message_text_one = fake.text()
        message_text_two = fake.text()

        sms_one = self.create_and_persist_sms(sender=sender_phone_number_one, recipient=recipient_phone_number_one,
                                              message=message_text_one)

        sms_two = self.create_and_persist_sms(sender=sender_phone_number_two,
                                              recipient=recipient_phone_number_two,
                                              message=message_text_two)

        sms_response_one = create_mock_sms_response(sms_identifier=sms_one.identifier)
        sms_response_two = create_mock_sms_response(sms_identifier=sms_two.identifier)

        self.create_and_persist_sms_response(sms_response=sms_response_one, sms_id=sms_one.id)
        self.create_and_persist_sms_response(sms_response=sms_response_two, sms_id=sms_two.id)

        sms_callback_one = create_mock_sms_callback(
            sender_phone_number=sender_phone_number_one,
            sms_sid=sms_response_one.sid,
            message_sid=sms_response_one.messaging_service_sid
        )

        sms_callback_two = create_mock_sms_callback(
            sender_phone_number=sender_phone_number_two,
            sms_sid=sms_response_two.sid,
            message_sid=sms_response_two.messaging_service_sid
        )

        # create an existing SMS callback records
        self.create_and_persist_sms_callback(sms_callback=sms_callback_one, sms_id=sms_one.id)
        self.create_and_persist_sms_callback(sms_callback=sms_callback_two, sms_id=sms_two.id)

        actual = self.sms_callback_repository.get_all()

        self.assertEqual(len(actual), 2)
        self.assertListEqual(actual, [sms_callback_one, sms_callback_two])

    def test_updates_status_of_persisted_sms_callback(self):
        """Should update the status of a persisted SMS Callback"""
        sender_phone_number = "+254744444444"
        recipient_phone_number = "+254755555555"
        message_text = fake.text()

        sms = self.create_and_persist_sms(sender=sender_phone_number, recipient=recipient_phone_number,
                                          message=message_text)

        # time elapses & an SMS response is created from the SMS
        sms_response = create_mock_sms_response(sms_identifier=sms.identifier)

        # we persist that SMS response
        self.create_and_persist_sms_response(sms_response=sms_response, sms_id=sms.id)

        # create an sms callback
        sms_callback = create_mock_sms_callback(
            sender_phone_number=sender_phone_number,
            sms_sid=sms_response.sid,
            message_sid=sms_response.messaging_service_sid
        )

        # persist sms callback
        self.create_and_persist_sms_callback(sms_callback=sms_callback, sms_id=sms.id)

        # update the statuses of sms callback
        sms_status = SmsDeliveryStatus.DELIVERED
        updated_sms_callback = replace(sms_callback, sms_status=sms_status)

        # perform
        self.sms_callback_repository.update(updated_sms_callback)

        with self.client.session_factory() as session:
            actual = session.query(SmsCallbackModel).filter_by(identifier=sms_callback.id.value).first()

            self.assertEqual(sms_status, actual.sms_status)

    def test_raises_exception_when_updating_an_sms_callback_that_does_not_exist(self):
        """Should raise SmsCallbackNotFoundError when updating the status of an SMS Callback that does not exist"""
        sms_callback = create_mock_sms_callback()

        with self.assertRaises(SmsCallbackNotFoundError):
            self.sms_callback_repository.update(sms_callback)

    def test_raises_exception_when_removing_an_sms_callback_that_does_not_exist(self):
        """Should raise SmsCallbackNotFoundError when removing an SMS Callback that does not exist"""
        sms_callback = create_mock_sms_callback()

        with self.assertRaises(SmsCallbackNotFoundError):
            self.sms_callback_repository.remove(sms_callback)

    def test_removes_initially_persisted_sms_callback(self):
        """Should remove an initially persisted SMS Callback"""
        sender_phone_number = "+254744444444"
        recipient_phone_number = "+254755555555"
        message_text = fake.text()

        # persist an SMS
        sms = self.create_and_persist_sms(sender=sender_phone_number, recipient=recipient_phone_number,
                                          message=message_text)

        # time elapses & an SMS response is created from the SMS
        sms_response = create_mock_sms_response(sms_identifier=sms.identifier)

        self.create_and_persist_sms_response(sms_response=sms_response, sms_id=sms.id)

        # create an sms callback
        sms_callback = create_mock_sms_callback(
            sender_phone_number=sender_phone_number,
            sms_sid=sms_response.sid,
            message_sid=sms_response.messaging_service_sid
        )

        # persist SMS callback
        self.create_and_persist_sms_callback(sms_callback=sms_callback, sms_id=sms.id)

        self.sms_callback_repository.remove(sms_callback)

        with self.client.session_factory() as session:
            actual = session.query(SmsCallbackModel).filter_by(identifier=sms_callback.id.value).first()
            self.assertIsNone(actual)


if __name__ == '__main__':
    unittest.main()
