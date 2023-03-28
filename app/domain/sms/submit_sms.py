"""
Use case to send out sms
"""
from app.domain.entities.sms import Sms
from app.core.infra.producer import Producer
from .exceptions import SendSmsException
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
            raise SendSmsException("Invalid sms request provided")
        try:
            self.producer.publish_message(sms)
        except Exception as e:
            raise Exception('Failed to submit sms')
