"""
Use case to submit sms callback. This handles validation of the sms callback received, before submitting or emitting
an SMS_CALLBACK_RECEIVED_EVENT which is then picked up by another part of the system to then handle persisting the SMS
callback
"""
from app.domain.entities.sms_callback import SmsCallback
from app.core.infra.producer import Producer
from app.infra.logger import log as logger
from .exceptions import SubmitSmsCallbackException
from app.core.domain.services import Service


class SubmitSmsCallbackService(Service):
    def __init__(self, producer: Producer):
        self.producer = producer

    def execute(self, smscallback: SmsCallback):
        """
        Handles validation logic before submitting Sms callback, then emits an event that is handled by another part of
        the domain
        Args:
            smscallback: Sms callback Request
        Returns:
        """
        if not smscallback:
            raise SubmitSmsCallbackException("Invalid sms callback request provided")
        try:
            self.producer.publish_message(smscallback)
        except Exception as e:
            logger.error(f"{self.name}> Failed to submit sms callback because of {e}", e)
            raise SubmitSmsCallbackException("Failed to submit sms callback")
