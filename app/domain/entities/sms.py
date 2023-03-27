"""
SMS Entity that represents an SMS in the system
"""

from typing import Dict
from pydantic import BaseModel
from app.core.domain.entities.entity import Entity
from .message import Message
from .phone_number import PhoneNumber


class Sms(BaseModel, Entity):
    """
    SMS Entity contains the sender, recipient and message values. The Sender is optional & if not provided will default
    to the system's default
    """

    sender: PhoneNumber = None
    recipient: PhoneNumber
    message: Message

    @staticmethod
    def from_dict(data: Dict[str, str]) -> 'Sms':
        sender = data.get('sender', None)
        recipient = data.get('recipient', None)
        if not recipient:
            raise ValueError("Missing phone number")

        message_text = data.get('message', None)
        if not message_text:
            raise ValueError("Missing message text")

        sender_phone_number = PhoneNumber(value=sender) if sender else None
        recipient_phone_number = PhoneNumber(value=recipient)
        message = Message(value=message_text)
        return Sms(sender=sender_phone_number, recipient=recipient_phone_number, message=message)
