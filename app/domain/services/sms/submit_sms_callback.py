"""
Use case to submit sms callback. This handles validation of the sms callback received, before submitting or emitting
an SMS_CALLBACK_RECEIVED_EVENT which is then picked up by another part of the system to then handle persisting the SMS
callback
"""
from opentelemetry import trace

from app.domain.entities.sms_callback import SmsCallback
from app.core.infra.producer import Producer
from app.infra.logger import log as logger
from app.domain.services.exceptions import SubmitSmsCallbackException
from app.core.domain.services import Service

tracer = trace.get_tracer("domain.services.sms.submit_sms_callback")


class SubmitSmsCallbackService(Service):
    def __init__(self, producer: Producer):
        self.producer = producer

    @tracer.start_as_current_span("execute")
    async def execute(self, callback: SmsCallback):
        """
        Handles validation logic before submitting Sms callback, then emits an event that is handled by another part of
        the domain
        Args:
            callback: Sms callback Request
        Returns:
        """
        if not callback:
            raise SubmitSmsCallbackException("Invalid sms callback request provided")
        try:
            # TODO: add retry to handle failures. max of 3
            await self.producer.publish_message(callback)
        except Exception as e:
            logger.error(
                f"{self.name}> Failed to submit sms callback because of {e}", e
            )
            raise SubmitSmsCallbackException("Failed to submit sms callback")
