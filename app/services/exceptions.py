from app.core.domain.exceptions import AppException


class SmsSendingException(AppException):
    def __init__(self, message=None):
        if message is None:
            self.message = "Failed to send sms message"


class ServiceIntegrationException(AppException):
    def __init__(self, message=None):
        if message is None:
            self.message = "Service Integration Error"
