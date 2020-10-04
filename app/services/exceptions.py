from app.exceptions import SmsGatewayError


class SmsSendingException(SmsGatewayError):
    def __init__(self, message=None):
        if message is None:
            self.message = "Failed to send sms message"


class ServiceIntegrationException(SmsGatewayError):
    def __init__(self, message=None):
        if message is None:
            self.message = "Service Integration Error"
