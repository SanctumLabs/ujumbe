"""
Sms Response Model represents a record in a database
"""
from __future__ import annotations
from typing import Dict, Union, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Column, String, Enum, DateTime, Float, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.sms_status import SmsDeliveryStatus
from app.domain.entities.sms_type import SmsType

from .base_model import BaseModel

if TYPE_CHECKING:
    from .sms_model import Sms


class SmsResponse(BaseModel):
    account_sid = Column(String, nullable=False, comment="SID of the account that sent the message")
    sid = Column(String, nullable=False, comment="Unique string that was created to identifier the message",
                 unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False,
                          comment="Date and time in GMT that resource was created")
    date_sent = Column(DateTime(timezone=True), nullable=False, comment="Date and time in GMT that resource was sent")
    date_updated = Column(DateTime(timezone=True), nullable=False,
                          comment="Date and time in GMT that resource was last updated")
    direction = Column(Enum(SmsType), name="sms_direction", default=SmsType.UNKNOWN,
                       comment="Direction of the message")
    num_media = Column(Integer, nullable=False, comment="Number of media files associated with the message")
    num_segments = Column(Integer, nullable=False, comment="Number of segments to make up a complete message")
    price = Column(Float, nullable=True, comment="Amount billed for each message, priced per segment")
    currency = Column(String, nullable=True, comment="Currency in which price is measured in ISO 4127 format")
    subresource_uris = Column(JSON)
    uri = Column(String, nullable=False, comment="URI of resource, relative to https://api.twilio.com")
    messaging_service_sid = Column(String, nullable=True, comment="SID of the messaging service used. Null if not used")
    error_code = Column(String, nullable=True, comment="Code returned if message status is failed or undelivered")
    error_message = Column(String, nullable=True, comment="Description of error code if available")
    status = Column(Enum(SmsDeliveryStatus), name="delivery_status", default=SmsDeliveryStatus.UNKNOWN,
                    comment="Status of the message")
    sms_id: Mapped[int] = mapped_column(ForeignKey("sms.id"))
    sms: Mapped["Sms"] = relationship(back_populates="response")

    def __repr__(self):
        return f"SmsResponse(id={self.id}, created_on={self.created_at}, updated_on={self.updated_at}, " \
               f"updated_by={self.updated_by}, deleted_at={self.deleted_at}, sms_id={self.sms_id} " \
               f"account_sid={self.account_sid}, " \
               f"sid={self.sid}, date_created={self.date_created}, date_sent={self.date_sent}, " \
               f"date_update={self.date_updated}), direction={self.direction}, num_media={self.num_media}, " \
               f"num_segments={self.num_segments}, price={self.price}, currency={self.currency}, " \
               f"subresource_uris={self.subresource_uris}, uri={self.uri}, " \
               f"messaging_service_sid={self.messaging_service_sid}, error_code={self.error_code}, " \
               f"error_message={self.error_message}, status={self.status})"

    def to_dict(self) -> Dict[str, Union[str, datetime, float, int, Dict]]:
        return dict(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            deleted_at=self.deleted_at,
            account_sid=self.account_sid,
            sid=self.sid,
            date_created=self.date_created,
            date_sent=self.date_sent,
            date_update=self.date_updated,
            direction=self.direction,
            num_media=self.num_media,
            num_segments=self.num_segments,
            price=self.price,
            currency=self.currency,
            subresource_uris=self.subresource_uris,
            uri=self.uri,
            messaging_service_sid=self.messaging_service_sid,
            error_code=self.error_code,
            error_message=self.error_message,
            status=self.status,
            sms_id=self.sms_id
        )
