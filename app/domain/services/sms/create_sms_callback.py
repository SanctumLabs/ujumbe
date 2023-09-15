"""
Use case to create an SMS callback
"""
from app.domain.entities.sms_callback import SmsCallback
from app.domain.repositories.sms_repository import SmsRepository
from app.domain.services.exceptions import CreateSmsCallbackException
from app.core.domain.services import Service


class CreateSmsCallbackService(Service):
    """
    Service that handles creating an SMS callback message
    """

    def __init__(self, repository: SmsRepository):
        self.repository = repository

    def execute(self, sms_callback: SmsCallback):
        """
        Handles persisting SMS Callback
        Args:
            sms_callback: SMS callback message
        """
        if not sms_callback:
            raise CreateSmsCallbackException("Invalid sms callback provided")
        try:
            self.repository.add(sms_callback)
        except Exception as e:
            raise CreateSmsCallbackException(f"Failed to submit sms callback {e}")
