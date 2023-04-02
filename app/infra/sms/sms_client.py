from twilio.rest import Client
from app.infra.logger import log as logger
from app.domain.entities.sms import Sms
from .exceptions import SmsClientException
from .dto import SmsResponse


class SmsClient:
    def __init__(self, account_sid: str, auth_token: str, messaging_service_sid: str):
        self.messaging_service_sid = messaging_service_sid
        self.twilio_client = Client(account_sid, auth_token)

    def send(self, sms: Sms) -> SmsResponse:
        """
        Sends a plain text message to a list of recipients with

        Args:
            sms: Sms to send out
        """

        try:
            logger.info(f"Sending sms {sms}")

            if sms.sender:
                response = self.twilio_client.messages.create(
                    body=sms.message.value,
                    from_=sms.sender.value,
                    to=sms.recipient.value
                )
            else:
                response = self.twilio_client.messages.create(
                    messaging_service_sid=self.messaging_service_sid,
                    body=sms.message.value,
                    to=sms.recipient.value
                )

            return SmsResponse(account_sid=response.account_sid, api_version=response.api_version, body=response.body,
                               date_created=response.date_created, date_sent=response.date_sent,
                               date_updated=response.date_updated, direction=response.direction,
                               error_code=response.error_code, error_message=response.error_message,
                               from_=response.from_, messaging_service_sid=response.messaging_service_sid,
                               num_media=response.num_media, num_segments=response.num_segments, price=response.price,
                               price_unit=response.price_unit, sid=response.sid, status=response.status,
                               subresource_uris=response.subresource_uris, to=response.to, uri=response.uri)
        except Exception as e:
            logger.error(f"Failed to send sms with error {e}")
            raise SmsClientException(f"Failed to send sms message")
