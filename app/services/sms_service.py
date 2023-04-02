"""
Send sms service wrapper. This handles sending the actual sms to recipients and handles connection to an SMS client.
"""
from app.infra.logger import log as logger
from app.domain.entities.sms import Sms
from app.infra.sms.sms_client import SmsClient
from .exceptions import SmsSendingException
from app.core.infra.sms_service import SmsService


class UjumbeSmsService(SmsService):
    def __init__(self, sms_client: SmsClient):
        self.sms_client = sms_client

    def send(self, sms: Sms):
        """
        Sends a plain text message to a list of recipients with
        Args:
            sms:
        """

        try:
            response = self.sms_client.send(sms)
            return response
        except Exception as e:
            logger.error(f"Failed to send sms with error {e}")
            raise SmsSendingException(f"Failed to send sms message")
