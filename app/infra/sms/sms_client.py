"""
Contains SMS client wrapper for interacting with a 3rd Party SMS Client system.
"""
from dataclasses import dataclass
from twilio.rest import Client
from faker import Faker
from app.infra.logger import log as logger
from app.domain.entities.sms import Sms
from .exceptions import SmsClientException
from .dto import SmsResponseDto


@dataclass
class SmsClientParams:
    """
    Args:
        account_sid (str): Account SID
        auth_token (str): Authentication token
        messaging_service_sid (str): Messaging Service SID
        enabled (bool): Whether the SMS client has been enabled or not
    """
    account_sid: str
    auth_token: str
    messaging_service_sid: str
    enabled: bool = False


class SmsClient:
    """SmsClient is a wrapper around a 3rd Party Sms client"""

    def __init__(self, params: SmsClientParams):
        """
        Initializes an SMS Client
        Args:
            params (SmsClientParams): Parameters to initialize client with
        """
        self.enabled = params.enabled
        self._messaging_service_sid = params.messaging_service_sid
        self._account_sid = params.account_sid
        self._auth_token = params.auth_token
        self.twilio_client = Client(params.account_sid, params.auth_token)

    def send(self, sms: Sms) -> SmsResponseDto:
        """
        Sends a plain text SMS message to a recipient and returns back the response as received. This has an enabled or
        disabled property. If enabled, the 3rd Party system is interacted with, if disabled, the system will return a
        stubbed out version of the sms response object.

        Args:
            sms: Sms to send out
        Returns:
            Sms Response object as received from 3rd Party system
        Raises:
            Exception is raised if there is an error sending out SMS.
        """

        if self.enabled:
            try:
                logger.info(f"{self.name}> Sending sms {sms}")

                if sms.sender:
                    response = self.twilio_client.messages.create(
                        body=sms.message.value,
                        from_=sms.sender.value,
                        to=sms.recipient.value,
                    )
                else:
                    response = self.twilio_client.messages.create(
                        messaging_service_sid=self._messaging_service_sid,
                        body=sms.message.value,
                        to=sms.recipient.value,
                    )

                return SmsResponseDto(
                    account_sid=response.account_sid,
                    api_version=response.api_version,
                    body=response.body,
                    date_created=response.date_created,
                    date_sent=response.date_sent,
                    date_updated=response.date_updated,
                    direction=response.direction,
                    error_code=response.error_code,
                    error_message=response.error_message,
                    from_=response.from_,
                    messaging_service_sid=response.messaging_service_sid,
                    num_media=response.num_media,
                    num_segments=response.num_segments,
                    price=response.price,
                    price_unit=response.price_unit,
                    sid=response.sid,
                    status=response.status,
                    subresource_uris=response.subresource_uris,
                    to=response.to,
                    uri=response.uri,
                )
            except Exception as e:
                logger.error(f"{self.name}> Failed to send sms {sms} with error {e}", e)
                raise SmsClientException(f"Failed to send sms message {sms} with exception: {e}")
        else:
            logger.info(f"{self.name}> client has been disabled. Not sending sms {sms}")

            fake = Faker()
            fake_sid = fake.uuid4()

            api_version = "2023-04-01"
            fake_uri = f"{api_version}/Accounts/{self._account_sid}/Messages/{fake_sid}.json"

            fake_date_created = fake.past_datetime()
            fake_date_sent = fake.future_datetime()
            fake_date_updated = fake.future_datetime()

            return SmsResponseDto(
                account_sid=self._account_sid,
                api_version="2023-04-01",
                body=sms.message.value,
                date_created=fake_date_created,
                date_sent=fake_date_sent,
                date_updated=fake_date_updated,
                direction="outbound-api",
                error_code=None,
                error_message=None,
                from_=sms.sender.value if sms.sender is not None else None,
                messaging_service_sid=self._messaging_service_sid,
                num_media="0",
                num_segments="1",
                price=None,
                price_unit=None,
                sid=fake_sid,
                status="sent",
                subresource_uris={},
                to=sms.recipient.value,
                uri=fake_uri,
            )

    @property
    def name(self) -> str:
        """
        Name of the sms client class
        Returns: class name
        """
        return self.__class__.__name__
