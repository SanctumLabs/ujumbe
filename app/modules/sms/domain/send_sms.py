"""
Use case to send out sms
"""
from ..entities.sms_request import SmsRequest
from .exceptions import SendSmsException
from app.infra.tasks.sms_sending_task import sms_sending_task


def send_sms(request: SmsRequest):
    """
    Use case that sends out an SMS
    """
    if not request:
        raise SendSmsException("Invalid sms request provided")
    sms_sending_task.apply_async(kwargs=dict(data=request.dict()))
