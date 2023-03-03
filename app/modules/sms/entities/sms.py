"""
SMS Request
"""

from typing import Dict
from pydantic import BaseModel, validator
from app.core.domain.entities.entity import Entity
from .message import Message
from .phone_number import PhoneNumber


class Sms(BaseModel, Entity):
    """
    SMS Entity
    """

    phone_number: PhoneNumber
    message: Message

    @staticmethod
    def from_dict(data: Dict[str, str]) -> 'Sms':
        phone = data.get('phone_number', None) or data.get("phone", None)
        if not phone:
            raise ValueError("Missing phone number")
        
        message_text = data.get('message', None)
        if not message_text:
            raise ValueError("Missing message text")
        
        phone_number = PhoneNumber(value=phone)
        message = Message(value=message_text)
        return Sms(phone_number=phone_number, message=message)
