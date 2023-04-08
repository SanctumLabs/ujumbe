from app.core.domain.entities.unique_id import UniqueId
from app.domain.entities.sms import Sms
from app.domain.entities.message import Message
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.sms_status import SmsDeliveryStatus
from .sms_model import Sms as SmsModel


def sms_model_to_entity(model: SmsModel) -> Sms:
    sms_id = UniqueId(value=model.identifier)
    sender_phone_number = model.sender
    sender = PhoneNumber(value=sender_phone_number)

    recipient_phone_number = model.recipient
    recipient = PhoneNumber(value=recipient_phone_number)

    message_text = model.message
    message = Message(value=message_text)

    status = model.status
    delivery_status = SmsDeliveryStatus(value=status)

    return Sms(id=sms_id, sender=sender, recipient=recipient, message=message, status=delivery_status)


def sms_entity_to_model(entity: Sms) -> SmsModel:
    return SmsModel(identifier=entity.id.value, sender=entity.sender.value, recipient=entity.recipient.value,
                    message=entity.message.value,
                    status=entity.status)
