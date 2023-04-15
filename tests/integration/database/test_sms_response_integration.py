import unittest
from dataclasses import replace
from faker import Faker

import pytest

from app.domain.entities.sms_response import SmsResponse
from app.database.models.sms_model import Sms as SmsModel
from app.database.models.sms_response_model import SmsResponse as SmsResponseModel
from app.domain.entities.sms_status import SmsDeliveryStatus
from app.domain.sms.exceptions import SmsNotFoundError

from app.database.sms_response_repository import SmsResponseDatabaseRepository

from . import BaseIntegrationTestCases
from ...mocks.mock_data import create_mock_sms_response

fake = Faker()


@pytest.mark.integration
class SmsResponseIntegrationTestCases(BaseIntegrationTestCases):
    def setUp(self) -> None:
        super().setUp()
        self.sms_response_repository = SmsResponseDatabaseRepository(self.client)

    def test_persists_a_valid_sms_response(self):
        """Test that a valid SMS Response can be persisted"""
        sender_phone_number = "+254722222222"
        recipient_phone_number = "+254733333333"
        message_text = fake.text()

        # create an existing SMS record first
        with self.client.session_factory() as session:
            sms = SmsModel(
                sender=sender_phone_number,
                recipient=recipient_phone_number,
                message=message_text
            )
            session.add(sms)
            session.commit()
            session.refresh(sms)
            session.close()

        sms_response = create_mock_sms_response(sms_identifier=sms.identifier)

        self.sms_response_repository.add(sms_response)

    def test_fails_to_persist_duplicate_valid_sms_response(self):
        """Test that 2 valid duplicate SMS Responses can not be persisted"""
        sender_phone_number = "+254700000000"
        recipient_phone_number = "+254711111111"
        message_text = fake.text()

        # create an existing SMS record first
        with self.client.session_factory() as session:
            sms = SmsModel(
                sender=sender_phone_number,
                recipient=recipient_phone_number,
                message=message_text
            )
            session.add(sms)
            session.commit()
            session.refresh(sms)
            session.close()

        sms_response_one = create_mock_sms_response(sms_identifier=sms.identifier)

        with self.assertRaises(Exception):
            self.sms_response_repository.add(sms_response_one)
            self.sms_response_repository.add(sms_response_one)

    def test_persists_2_valid_sms_responses(self):
        """Test that 2 valid SMS Responses can be persisted"""
        sender_phone_number_one = "+254744444444"
        sender_phone_number_two = "+254712121212"
        recipient_phone_number_one = "+254755555555"
        recipient_phone_number_two = "+254723232323"
        message_text_one = fake.text()
        message_text_two = fake.text()

        with self.client.session_factory() as session:
            sms_one = SmsModel(
                sender=sender_phone_number_one,
                recipient=recipient_phone_number_one,
                message=message_text_one
            )
            sms_two = SmsModel(
                sender=sender_phone_number_two,
                recipient=recipient_phone_number_two,
                message=message_text_two
            )

            session.add(sms_one)
            session.add(sms_two)
            session.commit()
            session.refresh(sms_one)
            session.refresh(sms_two)
            session.close()

        sms_response_one = create_mock_sms_response(sms_identifier=sms_one.identifier)
        sms_response_two = create_mock_sms_response(sms_identifier=sms_two.identifier)

        self.sms_response_repository.add(sms_response_one)
        self.sms_response_repository.add(sms_response_two)

        with self.client.session_factory() as session:
            actual_one = session.query(SmsResponseModel).filter_by(sid=sms_response_one.sid).first()
            actual_two = session.query(SmsResponseModel).filter_by(sid=sms_response_two.sid).first()

            self.assertEqual(sms_response_one.account_sid, actual_one.account_sid)
            self.assertEqual(sms_response_one.sid, actual_one.sid)
            self.assertEqual(sms_response_one.sms_type, actual_one.direction)
            self.assertEqual(sms_response_one.num_media, actual_one.num_media)
            self.assertEqual(sms_response_one.num_segments, actual_one.num_segments)
            self.assertEqual(sms_response_one.price.price, actual_one.price)
            self.assertEqual(sms_response_one.price.currency, actual_one.currency)
            self.assertEqual(sms_response_one.status, actual_one.status)
            self.assertEqual(sms_response_one.subresource_uris, actual_one.subresource_uris)
            self.assertEqual(sms_response_one.uri, actual_one.uri)
            self.assertEqual(sms_response_one.messaging_service_sid, actual_one.messaging_service_sid)
            self.assertEqual(sms_response_one.error_code, actual_one.error_code)
            self.assertEqual(sms_response_one.error_message, actual_one.error_message)
            self.assertEqual("system", actual_one.updated_by)
            self.assertEqual(sms_response_one.sms_date.date_created, actual_one.date_created)
            self.assertEqual(sms_response_one.sms_date.date_sent, actual_one.date_sent)
            self.assertEqual(sms_response_one.sms_date.date_updated, actual_one.date_updated)

            self.assertEqual(sms_response_two.account_sid, actual_two.account_sid)
            self.assertEqual(sms_response_two.sid, actual_two.sid)
            self.assertEqual(sms_response_two.sms_type, actual_two.direction)
            self.assertEqual(sms_response_two.num_media, actual_two.num_media)
            self.assertEqual(sms_response_two.num_segments, actual_two.num_segments)
            self.assertEqual(sms_response_two.price.price, actual_two.price)
            self.assertEqual(sms_response_two.price.currency, actual_two.currency)
            self.assertEqual(sms_response_two.status, actual_two.status)
            self.assertEqual(sms_response_two.subresource_uris, actual_two.subresource_uris)
            self.assertEqual(sms_response_two.uri, actual_two.uri)
            self.assertEqual(sms_response_two.messaging_service_sid, actual_two.messaging_service_sid)
            self.assertEqual(sms_response_two.error_code, actual_two.error_code)
            self.assertEqual(sms_response_two.error_message, actual_two.error_message)
            self.assertEqual("system", actual_two.updated_by)
            self.assertEqual(sms_response_two.sms_date.date_created, actual_two.date_created)
            self.assertEqual(sms_response_two.sms_date.date_sent, actual_two.date_sent)
            self.assertEqual(sms_response_two.sms_date.date_updated, actual_two.date_updated)

    def test_get_by_id_returns_persisted_sms_response(self):
        """Test that repository can retrieve initially persisted SMS Response given its ID"""
        sender_phone_number = "+254744444444"
        recipient_phone_number = "+254755555555"
        message_text = fake.text()

        # persist an SMS
        with self.client.session_factory() as session:
            sms = SmsModel(
                sender=sender_phone_number,
                recipient=recipient_phone_number,
                message=message_text
            )

            session.add(sms)
            session.commit()
            session.refresh(sms)

        # time elapses
        sms_response = create_mock_sms_response(sms_identifier=sms.identifier)

        # Persist an sms response
        with self.client.session_factory() as session:
            sms_response_model = SmsResponseModel(
                identifier=sms_response.id.value,
                account_sid=sms_response.account_sid,
                sid=sms_response.sid,
                date_sent=sms_response.sms_date.date_sent,
                date_updated=sms_response.sms_date.date_updated,
                date_created=sms_response.sms_date.date_created,
                direction=sms_response.sms_type,
                num_media=sms_response.num_media,
                num_segments=sms_response.num_segments,
                price=sms_response.price.price,
                currency=sms_response.price.currency,
                status=sms_response.status,
                subresource_uris=sms_response.subresource_uris,
                uri=sms_response.uri,
                messaging_service_sid=sms_response.messaging_service_sid,
                error_code=sms_response.error_code,
                error_message=sms_response.error_message,
                sms_id=sms.id
            )

            session.add(sms_response_model)
            session.commit()
            session.refresh(sms_response_model)

        actual = self.sms_response_repository.get_by_id(sms_response.id.value)

        self.assertEqual(sms_response.account_sid, actual.account_sid)
        self.assertEqual(sms_response.sid, actual.sid)
        self.assertEqual(sms_response.sms_type, actual.sms_type)
        self.assertEqual(sms_response.num_media, actual.num_media)
        self.assertEqual(sms_response.num_segments, actual.num_segments)
        self.assertEqual(sms_response.price.price, actual.price.price)
        self.assertEqual(sms_response.price.currency, actual.price.currency)
        self.assertEqual(sms_response.status, actual.status)
        self.assertEqual(sms_response.subresource_uris, actual.subresource_uris)
        self.assertEqual(sms_response.uri, actual.uri)
        self.assertEqual(sms_response.messaging_service_sid, actual.messaging_service_sid)
        self.assertEqual(sms_response.error_code, actual.error_code)
        self.assertEqual(sms_response.error_message, actual.error_message)
        self.assertEqual(sms_response.sms_date.date_created, actual.sms_date.date_created)
        self.assertEqual(sms_response.sms_date.date_sent, actual.sms_date.date_sent)
        self.assertEqual(sms_response.sms_date.date_updated, actual.sms_date.date_updated)

    def test_get_by_id_throws_sms_not_found_exception_when_sms_response_does_not_exist(self):
        """Test that repository throws SmsNotFoundError when SMS response with given ID can not be found"""

        sid = SmsResponse.next_id()

        with self.assertRaises(SmsNotFoundError):
            self.sms_response_repository.get_by_id(sid.value)

    def test_returns_all_persisted_valid_sms_responses(self):
        """Should return all valid SMS responses"""
        self.maxDiff = None
        sender_phone_number_one = "+254744444444"
        sender_phone_number_two = "+254712121212"
        recipient_phone_number_one = "+254755555555"
        recipient_phone_number_two = "+254723232323"
        message_text_one = fake.text()
        message_text_two = fake.text()

        with self.client.session_factory() as session:
            sms_one = SmsModel(
                sender=sender_phone_number_one,
                recipient=recipient_phone_number_one,
                message=message_text_one
            )
            sms_two = SmsModel(
                sender=sender_phone_number_two,
                recipient=recipient_phone_number_two,
                message=message_text_two
            )

            session.add(sms_one)
            session.add(sms_two)
            session.commit()
            session.refresh(sms_one)
            session.refresh(sms_two)
            session.close()

        sms_response_one = create_mock_sms_response(sms_identifier=sms_one.identifier)
        sms_response_two = create_mock_sms_response(sms_identifier=sms_two.identifier)

        with self.client.session_factory() as session:
            sms_response_one_model = SmsResponseModel(
                identifier=sms_response_one.id.value,
                account_sid=sms_response_one.account_sid,
                sid=sms_response_one.sid,
                date_sent=sms_response_one.sms_date.date_sent,
                date_updated=sms_response_one.sms_date.date_updated,
                date_created=sms_response_one.sms_date.date_created,
                direction=sms_response_one.sms_type,
                num_media=sms_response_one.num_media,
                num_segments=sms_response_one.num_segments,
                price=sms_response_one.price.price,
                currency=sms_response_one.price.currency,
                status=sms_response_one.status,
                subresource_uris=sms_response_one.subresource_uris,
                uri=sms_response_one.uri,
                messaging_service_sid=sms_response_one.messaging_service_sid,
                error_code=sms_response_one.error_code,
                error_message=sms_response_one.error_message,
                sms_id=sms_one.id
            )

            sms_response_two_model = SmsResponseModel(
                identifier=sms_response_two.id.value,
                account_sid=sms_response_two.account_sid,
                sid=sms_response_two.sid,
                date_sent=sms_response_two.sms_date.date_sent,
                date_updated=sms_response_two.sms_date.date_updated,
                date_created=sms_response_two.sms_date.date_created,
                direction=sms_response_two.sms_type,
                num_media=sms_response_two.num_media,
                num_segments=sms_response_two.num_segments,
                price=sms_response_two.price.price,
                currency=sms_response_two.price.currency,
                status=sms_response_two.status,
                subresource_uris=sms_response_two.subresource_uris,
                uri=sms_response_two.uri,
                messaging_service_sid=sms_response_two.messaging_service_sid,
                error_code=sms_response_two.error_code,
                error_message=sms_response_two.error_message,
                sms_id=sms_two.id
            )

            session.add(sms_response_one_model)
            session.add(sms_response_two_model)
            session.commit()
            session.refresh(sms_response_one_model)
            session.refresh(sms_response_two_model)

        actual = self.sms_response_repository.get_all()

        self.assertEqual(len(actual), 2)
        self.assertListEqual(actual, [sms_response_one, sms_response_two])

    def test_updates_status_of_persisted_sms_response(self):
        """Should update the status of a persisted SMS Response"""
        sender_phone_number = "+254744444444"
        recipient_phone_number = "+254755555555"
        message_text = fake.text()

        # persist an SMS
        with self.client.session_factory() as session:
            sms = SmsModel(
                sender=sender_phone_number,
                recipient=recipient_phone_number,
                message=message_text
            )

            session.add(sms)
            session.commit()
            session.refresh(sms)
            session.close()

        # time elapses & an SMS response is created from the SMS
        sms_response = create_mock_sms_response(sms_identifier=sms.identifier)

        # we persist that SMS response
        with self.client.session_factory() as session:
            sms_response_model = SmsResponseModel(
                identifier=sms_response.id.value,
                account_sid=sms_response.account_sid,
                sid=sms_response.sid,
                date_sent=sms_response.sms_date.date_sent,
                date_updated=sms_response.sms_date.date_updated,
                date_created=sms_response.sms_date.date_created,
                direction=sms_response.sms_type,
                num_media=sms_response.num_media,
                num_segments=sms_response.num_segments,
                price=sms_response.price.price,
                currency=sms_response.price.currency,
                status=sms_response.status,
                subresource_uris=sms_response.subresource_uris,
                uri=sms_response.uri,
                messaging_service_sid=sms_response.messaging_service_sid,
                error_code=sms_response.error_code,
                error_message=sms_response.error_message,
                sms_id=sms.id
            )

            session.add(sms_response_model)
            session.commit()
            session.refresh(sms_response_model)
            session.close()

        status = SmsDeliveryStatus.SENT
        updated_sms_response = replace(sms_response, status=status)

        self.sms_response_repository.update(updated_sms_response)

        with self.client.session_factory() as session:
            actual = session.query(SmsResponseModel).filter_by(identifier=sms_response.id.value).first()

            self.assertEqual(status, actual.status)

    def test_raises_exception_when_updating_an_sms_response_that_does_not_exist(self):
        """Should raise SmsNotFoundException when updating the status of an SMS Response that does not exist"""
        sms_response = create_mock_sms_response()

        with self.assertRaises(SmsNotFoundError):
            self.sms_response_repository.update(sms_response)

    def test_raises_exception_when_removing_an_sms_response_that_does_not_exist(self):
        """Should raise SmsNotFoundException when removing an SMS Response that does not exist"""
        sms_response = create_mock_sms_response()

        with self.assertRaises(SmsNotFoundError):
            self.sms_response_repository.remove(sms_response)

    def test_removes_initially_persisted_sms_response(self):
        """Should remove an initially persisted SMS Response"""
        sender_phone_number = "+254744444444"
        recipient_phone_number = "+254755555555"
        message_text = fake.text()

        # persist an SMS
        with self.client.session_factory() as session:
            sms = SmsModel(
                sender=sender_phone_number,
                recipient=recipient_phone_number,
                message=message_text
            )

            session.add(sms)
            session.commit()
            session.refresh(sms)
            session.close()

        # time elapses & an SMS response is created from the SMS
        sms_response = create_mock_sms_response(sms_identifier=sms.identifier)

        # we persist that SMS response
        with self.client.session_factory() as session:
            sms_response_model = SmsResponseModel(
                identifier=sms_response.id.value,
                account_sid=sms_response.account_sid,
                sid=sms_response.sid,
                date_sent=sms_response.sms_date.date_sent,
                date_updated=sms_response.sms_date.date_updated,
                date_created=sms_response.sms_date.date_created,
                direction=sms_response.sms_type,
                num_media=sms_response.num_media,
                num_segments=sms_response.num_segments,
                price=sms_response.price.price,
                currency=sms_response.price.currency,
                status=sms_response.status,
                subresource_uris=sms_response.subresource_uris,
                uri=sms_response.uri,
                messaging_service_sid=sms_response.messaging_service_sid,
                error_code=sms_response.error_code,
                error_message=sms_response.error_message,
                sms_id=sms.id
            )

            session.add(sms_response_model)
            session.commit()
            session.refresh(sms_response_model)
            session.close()

        self.sms_response_repository.remove(sms_response)

        with self.client.session_factory() as session:
            actual = session.query(SmsResponseModel).filter_by(identifier=sms_response.id.value).first()
            self.assertIsNone(actual)


if __name__ == '__main__':
    unittest.main()
