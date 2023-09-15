"""
Use case to send out an SMS
"""
from app.domain.entities.sms import Sms
from app.core.infra.sms_service import SmsService
from app.domain.repositories.sms_repository import SmsRepository
from app.domain.services.exceptions import SendSmsException
from app.core.domain.services import Service


class SendSmsService(Service):
    def __init__(self, sms_service: SmsService, sms_response_repository: SmsRepository):
        self.sms_service = sms_service
        self.sms_response_repository = sms_response_repository

    def execute(self, sms: Sms):
        """
        Handles sending out an SMS & saving the subsequent response
        Args:
            sms: Sms message to send
        """
        if not sms:
            raise SendSmsException("Invalid sms provided")
        try:
            sms_response = self.sms_service.send(sms)
            self.sms_response_repository.add(sms_response)
        except Exception as e:
            raise SendSmsException(f"Failed to send sms {sms}, {e}")
