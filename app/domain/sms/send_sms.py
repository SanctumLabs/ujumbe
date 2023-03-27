"""
Use case to send out sms
"""
from app.domain.entities.sms import Sms
from .exceptions import SendSmsException
from app.infra.tasks.sms_sending_task import sms_sending_task


def send_sms(request: Sms):
    """
    Use case that sends out an SMS.
    We will first persist the SMS request, before sending it out. This will send an event to a broker
    which will then publish the event to consumers(subscribers) which will handle saving the sms
    request & then later send out the SMS
    """
    if not request:
        raise SendSmsException("Invalid sms request provided")
    # TODO: publish SEND_SMS_EVENT_RECEIVED
    # TODO: save sms request in database
    sms_sending_task.apply_async(kwargs=dict(data=request.dict()))
