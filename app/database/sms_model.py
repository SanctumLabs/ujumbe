"""
Sms represents an SMS record in a Database
"""
from __future__ import annotations
from typing import Dict, Union, Optional
from datetime import datetime

from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import Mapped, relationship

from app.domain.entities.sms_status import SmsDeliveryStatus

from .base_model import BaseModel
from .sms_response_model import SmsResponse


class Sms(BaseModel):
    sender = Column(String, name="sender", nullable=False)
    recipient = Column(String, name="recipient", nullable=False)
    message = Column(String, name="message", nullable=False)
    status = Column(Enum(SmsDeliveryStatus), name="delivery_status", default=SmsDeliveryStatus.PENDING)
    response: Mapped[Optional["SmsResponse"]] = relationship(back_populates="sms")

    def __repr__(self):
        return f"Sms(id={self.id}, created_on={self.created_at}, updated_on={self.updated_at}, " \
               f"updated_by={self.updated_by}, deleted_at={self.deleted_at}, sender={self.sender}, " \
               f"recipient={self.recipient}, message={self.message}, status={self.status})"

    def to_dict(self) -> Dict[str, Union[str, datetime, Optional[SmsResponse]]]:
        return dict(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            deleted_at=self.deleted_at,
            sender=self.sender,
            recipient=self.recipient,
            message=self.message,
            status=self.status,
            response=self.response
        )
