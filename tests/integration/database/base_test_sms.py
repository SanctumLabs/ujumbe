from . import BaseIntegrationTestCases
from app.domain.entities.sms_response import SmsResponse
from app.database.models.sms_response_model import SmsResponse as SmsResponseModel
from app.database.models.sms_callback_model import SmsCallback as SmsCallbackModel
from app.database.models.sms_model import Sms as SmsModel
from app.domain.entities.sms_callback import SmsCallback


class BaseSmsIntegrationTestCases(BaseIntegrationTestCases):
    """
    Base class that contains helper methods for integration tests for the sms database
    """

    def create_and_persist_sms(self, sender: str, recipient: str, message: str) -> SmsModel:
        """Convenience method to create an SMS record and persist it"""
        with self.client.session_factory() as session:
            sms = SmsModel(
                sender=sender,
                recipient=recipient,
                message=message
            )

            session.add(sms)
            session.commit()
            session.refresh(sms)
        return sms

    def create_and_persist_sms_response(self, sms_response: SmsResponse, sms_id: int) -> SmsResponseModel:
        """Convenience method to create and persist an SMS Response record"""
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
                sms_id=sms_id
            )

            session.add(sms_response_model)
            session.commit()
            session.refresh(sms_response_model)
        return sms_response_model

    def create_and_persist_sms_callback(self, sms_callback: SmsCallback, sms_id: int) -> SmsCallbackModel:
        """Convenience method to create an SMS callback record and persist it"""
        with self.client.session_factory() as session:
            sms_callback_model = SmsCallbackModel(
                identifier=sms_callback.id.value,
                account_sid=sms_callback.account_sid,
                from_=sms_callback.sender.value,
                message_sid=sms_callback.message_sid,
                message_status=sms_callback.message_status,
                sms_sid=sms_callback.sms_sid,
                sms_status=sms_callback.sms_status,
                sms_id=sms_id
            )

            session.add(sms_callback_model)
            session.commit()
            session.refresh(sms_callback_model)
        return sms_callback_model
