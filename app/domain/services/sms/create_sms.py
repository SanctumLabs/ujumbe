"""
Use case to create an sms
"""
from app.domain.entities.sms import Sms
from app.core.infra.producer import Producer
from app.domain.repositories.sms_repository import SmsRepository
from app.domain.services.exceptions import CreateSmsException
from app.core.domain.services import Service


class CreateSmsService(Service):
    def __init__(self, repository: SmsRepository, producer: Producer):
        self.producer = producer
        self.repository = repository

    def execute(self, sms: Sms):
        """
        Handles persisting SMS & publishing a SEND_SMS_EVENT that will then trigger sending out SMS
        Args:
            sms: Sms
        """
        if not sms:
            raise CreateSmsException("Invalid sms provided")
        try:
            self.repository.add(sms)
            self.producer.publish_message(sms)
        except Exception as e:
            raise CreateSmsException("Failed to submit sms")
