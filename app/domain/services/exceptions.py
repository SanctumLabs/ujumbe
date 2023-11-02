from app.core.domain.exceptions import EntityNotFoundException


class SendSmsException(Exception):
    """Send SMS Exception"""


class CreateSmsException(Exception):
    """Create SMS Exception"""


class CreateSmsCallbackException(Exception):
    """Create SMS Callback Exception"""


class SubmitSmsException(Exception):
    """Submit SMS Exception"""


class SubmitSmsCallbackException(Exception):
    """Submit SMS Callback Exception"""


class SmsNotFoundError(EntityNotFoundException):
    entity_name: str = "Sms"


class SmsResponseNotFoundError(EntityNotFoundException):
    entity_name: str = "SmsResponse"


class SmsCallbackNotFoundError(EntityNotFoundException):
    entity_name: str = "SmsCallback"