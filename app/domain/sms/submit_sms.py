"""
Use case to submit an sms. This handles validation of the sms received, before submitting or emitting a SUBMIT_SMS_EVENT
which is then picked up by another part of the system to then handle persisting SMS & sending it out
"""
from app.domain.entities.sms import Sms
from app.core.infra.producer import Producer
from .exceptions import SubmitSmsException
from app.core.domain.services import Service


class SubmitSmsService(Service):
    def __init__(self, producer: Producer):
        self.producer = producer

    def execute(self, sms: Sms):
        """
        Handles validation logic before submitting an Sms, then emits an event that is handled by another part of the
        domain
        Args:
            sms: Sms Request
        Returns:
        """
        if not sms:
            raise SubmitSmsException("Invalid sms request provided")
        try:
            self.producer.publish_message(sms)
        except Exception as e:
            raise SubmitSmsException("Failed to submit sms")
