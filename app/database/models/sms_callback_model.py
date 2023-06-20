"""
Sms Callback Model represents a sms callback record in a database
"""
from __future__ import annotations
from typing import Dict, Union, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Column, String, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.sms_status import SmsDeliveryStatus

from .base_model import BaseModel

if TYPE_CHECKING:
    from .sms_model import Sms


class SmsCallback(BaseModel):
    account_sid = Column(
        String, nullable=False, comment="SID of the account that sent the message"
    )
    from_ = Column(
        String,
        nullable=False,
        comment="Sender of the message",
        unique=False,
    )
    message_sid = Column(
        String,
        nullable=True,
        comment="SID of the messaging service used",
    )
    message_status = Column(
        Enum(SmsDeliveryStatus),
        name="message_status",
        default=SmsDeliveryStatus.UNKNOWN,
        comment="Message status",
    )
    sms_sid = Column(
        String,
        comment="Sms SID of the messaging service used. Null if not used",
    )
    sms_status = Column(
        Enum(SmsDeliveryStatus),
        name="delivery_status",
        default=SmsDeliveryStatus.UNKNOWN,
        comment="Status of the sms",
    )
    sms_id: Mapped[int] = mapped_column(ForeignKey("sms.id"), comment="SMS ID")
    sms: Mapped["Sms"] = relationship(back_populates="callback")

    def __repr__(self):
        return (
            f"SmsCallback(id={self.identifier}, created_on={self.created_at}, updated_on={self.updated_at}, "
            f"updated_by={self.updated_by}, deleted_at={self.deleted_at}, sms_id={self.sms_id} "
            f"account_sid={self.account_sid}, "
            f"from={self.from_}, message_sid={self.message_sid}, message_status={self.message_status}, "
            f"sms_sid={self.sms_sid}, sms_status={self.sms_status})"
        )

    def to_dict(self) -> Dict[str, Union[str, datetime, float, int, Dict]]:
        return dict(
            id=self.identifier,
            created_at=self.created_at,
            updated_at=self.updated_at,
            deleted_at=self.deleted_at,
            sms_id=self.sms_id,
            from_=self.from_,
            account_sid=self.account_sid,
            message_sid=self.message_sid,
            message_status=self.message_status,
            sms_status=self.sms_status,
            sms_sid=self.sms_sid,
        )
