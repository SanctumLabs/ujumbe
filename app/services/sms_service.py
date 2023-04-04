"""
Send sms service wrapper. This handles sending the actual sms to recipients and handles connection to an SMS client.
"""
from app.infra.logger import log as logger
from app.domain.entities.sms import Sms
from app.domain.entities.sms_response import SmsResponse
from app.domain.entities.sms_date import SmsDate
from app.domain.entities.sms_price import SmsPrice
from app.domain.entities.sms_type import SmsType
from app.domain.entities.sms_status import SmsDeliveryStatus
from app.infra.sms.sms_client import SmsClient
from app.core.infra.sms_service import SmsService
from .exceptions import SmsSendingException


class UjumbeSmsService(SmsService):
    def __init__(self, sms_client: SmsClient):
        self.sms_client = sms_client

    def send(self, sms: Sms) -> SmsResponse:
        """
        Sends a plain text message to a list of recipients with
        Args:
            sms:
        """

        try:
            response = self.sms_client.send(sms)

            sms_date = SmsDate(
                date_sent=response.date_sent,
                date_updated=response.date_updated,
                date_created=response.date_created
            )

            sms_price = SmsPrice(
                price=response.price,
                currency=response.price_unit
            )

            sms_type = SmsType(response.direction)
            status = SmsDeliveryStatus(response.status)

            return SmsResponse(
                account_sid=response.account_sid,
                sid=response.sid,
                sms_date=sms_date,
                sms_type=sms_type,
                num_media=response.num_media,
                num_segments=response.num_segments,
                price=sms_price,
                status=status,
                subresource_uris=response.subresource_uris,
                uri=response.uri,
                messaging_service_sid=response.messaging_service_sid,
                error_code=response.error_code,
                error_message=response.error_message
            )
        except Exception as e:
            logger.error(f"Failed to send sms with error {e}")
            raise SmsSendingException(f"Failed to send sms message")
