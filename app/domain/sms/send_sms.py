"""
Use case to send out an sms
"""
from app.domain.entities.sms import Sms
from app.core.infra.sms_service import SmsService
from .exceptions import SendSmsException
from app.core.domain.services import Service


class SendSmsService(Service):

    def __init__(self, sms_service: SmsService):
        self.sms_service = sms_service

    def execute(self, sms: Sms):
        """
        Handles persisting SMS & publishing a SEND_SMS_EVENT that will then trigger sending out SMS
        Args:
            sms: Sms
        """
        if not sms:
            raise SendSmsException("Invalid sms provided")
        try:
            self.sms_service.send(sms)
        except Exception as e:
            raise Exception('Failed to send sms')
