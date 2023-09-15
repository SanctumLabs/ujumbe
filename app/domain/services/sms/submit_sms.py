"""
Usecase to submit an SMS. This handles validation of the sms received, before submitting or emitting a SUBMIT_SMS_EVENT
which is then picked up by another part of the system to then handle persisting SMS & sending it out
"""
from opentelemetry import trace
from app.domain.entities.sms import Sms
from app.core.infra.producer import Producer
from app.infra.logger import log as logger
from app.domain.services.exceptions import SubmitSmsException
from app.core.domain.services import Service

tracer = trace.get_tracer("domain.services.sms.submit_sms")


class SubmitSmsService(Service):
    def __init__(self, producer: Producer):
        self.producer = producer

    @tracer.start_as_current_span("execute")
    def execute(self, sms: Sms):
        """Handles validation logic before submitting an Sms, then emits an event that is handled by another part of the
        domain
        Args:
            sms(Sms): Sms Entity
        """
        if not sms:
            raise SubmitSmsException("Invalid sms request provided")
        try:
            self.producer.publish_message(sms)
        except Exception as e:
            logger.error(f"SubmitSmsService> Failed to submit sms. Err: {e}", e)
            raise SubmitSmsException("Failed to submit sms")
