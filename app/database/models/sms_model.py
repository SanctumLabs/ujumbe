"""
Sms represents an SMS record in a Database
"""
from __future__ import annotations
from typing import Dict, Union, Optional
from datetime import datetime

from sqlalchemy import Column, String, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship

from app.domain.entities.sms_status import SmsDeliveryStatus

from .base_model import BaseModel
from .sms_response_model import SmsResponse
from .sms_callback_model import SmsCallback


class Sms(BaseModel):
    """
    Represents an SMS record in the database
    """

    __table_args__ = (
        UniqueConstraint(
            "sender",
            "recipient",
            "message",
            name="sms_sender_recipient_message_constraint",
        ),
    )
    sender = Column(String, name="sender", nullable=False)
    recipient = Column(String, name="recipient", nullable=False)
    message = Column(String, name="message", nullable=False)
    status = Column(
        Enum(SmsDeliveryStatus),
        name="delivery_status",
        default=SmsDeliveryStatus.PENDING,
    )
    response: Mapped[Optional["SmsResponse"]] = relationship(back_populates="sms")
    callback: Mapped[Optional["SmsCallback"]] = relationship(back_populates="sms")

    def __repr__(self):
        """String Representation of an SMS record"""
        return (
            f"Sms(id={self.identifier}, identifier={self.identifier} created_on={self.created_at}, "
            f"updated_on={self.updated_at}, "
            f"updated_by={self.updated_by}, deleted_at={self.deleted_at}, sender={self.sender}, "
            f"recipient={self.recipient}, message={self.message}, status={self.status})"
        )

    def to_dict(self) -> Dict[str, Union[str, datetime, Optional[SmsResponse]]]:
        """
        Converts this record to a dictionary
        Returns: Dictionary representation of this database record
        """
        return dict(
            id=self.identifier,
            identifier=self.identifier,
            created_at=self.created_at,
            updated_at=self.updated_at,
            deleted_at=self.deleted_at,
            sender=self.sender,
            recipient=self.recipient,
            message=self.message,
            status=self.status,
            response=self.response,
            callback=self.callback,
        )
