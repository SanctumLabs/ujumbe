from typing import Dict
from sqlalchemy import Column, String, Enum
from .base_model import BaseModel
from app.domain.entities.sms_status import SmsDeliveryStatus


class Sms(BaseModel):
    sender = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    message = Column(String, nullable=False)
    status = Column(Enum(SmsDeliveryStatus), name="delivery_status", default=SmsDeliveryStatus.PENDING)

    def __repr__(self):
        return f"User(id={self.id}, created_on={self.created_at}, updated_on={self.updated_at}, " \
               f"updated_by={self.updated_by}, deleted_at={self.deleted_at}, sender={self.sender}, " \
               f"recipient={self.recipient}, message={self.message}, status={self.status})"

    def to_dict(self) -> Dict[str, str]:
        return dict(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            deleted_at=self.deleted_at,
            sender=self.sender,
            recipient=self.recipient,
            message=self.message,
            status=self.status
        )
