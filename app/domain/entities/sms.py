"""
SMS Entity that represents an SMS in the system.
"""

from typing import Dict, Optional
from pydantic import BaseModel
from app.core.domain.entities.entity import Entity
from .message import Message
from .phone_number import PhoneNumber
from .sms_status import SmsDeliveryStatus
from .sms_response import SmsResponse


class Sms(BaseModel, Entity):
    """
    SMS Entity contains the sender, recipient and message values. The Sender is optional & if not provided will default
    to the system's default
    """
    id = Entity.next_id()
    recipient: PhoneNumber
    message: Message
    sender: Optional[PhoneNumber] = None
    status: SmsDeliveryStatus = SmsDeliveryStatus.PENDING
    response: Optional[SmsResponse] = None

    @staticmethod
    def from_dict(data: Dict[str, str]) -> 'Sms':
        sender = data.get('sender', None)
        recipient = data.get('recipient', None)
        status = data.get("status", None)

        if not recipient:
            raise ValueError("Missing recipient phone number")

        message_text = data.get('message', None)
        if not message_text:
            raise ValueError("Missing message text")

        sender_phone_number = PhoneNumber(value=sender) if sender else None
        recipient_phone_number = PhoneNumber(value=recipient)
        message = Message(value=message_text)
        sms_status = SmsDeliveryStatus(status or SmsDeliveryStatus.UNKNOWN)
        return Sms(sender=sender_phone_number, recipient=recipient_phone_number, message=message, status=sms_status)

    def to_dict(self) -> Dict[str, str]:
        return dict(
            id=self.id.value,
            sender=self.sender.value,
            recipient=self.recipient.value or None,
            message=self.message.value,
            status=self.status,
            response=self.response.to_dict(),
        )
