"""
SMS Response is the response received from a 3rd Party SMS Provider with status information about the SMS that was
delivered.
"""
from typing import Dict, Optional
from dataclasses import dataclass
from pydantic import BaseModel
from app.core.domain.entities.entity import Entity
from .sms_status import SmsDeliveryStatus
from .sms_date import SmsDate
from .sms_price import SmsPrice
from .sms_type import SmsType


@dataclass(frozen=True, kw_only=True)
class SmsResponse(BaseModel, Entity):
    """
    Entity denoting the response of an Sms. Contains information about the sms delivery status with information such as
    price, status, uri, error codes and a couple of IDs to mark the uniqueness of the response
    """

    account_sid: str
    sid: str
    sms_date: SmsDate
    sms_type: SmsType
    num_media: int
    num_segments: int
    price: SmsPrice
    status: SmsDeliveryStatus
    subresource_uris: Dict[str, str]
    uri: str
    sms_id: str
    messaging_service_sid: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        return dict(
            id=self.id.value,
            account_sid=self.account_sid,
            sid=self.sid,
            date_sent=self.sms_date.date_sent,
            date_updated=self.sms_date.date_updated,
            date_created=self.sms_date.date_created,
            type=self.sms_type,
            num_media=self.num_media,
            num_segments=self.num_segments,
            price=self.price.price,
            currency=self.price.currency,
            status=self.status,
            subresource_uris=self.subresource_uris,
            uri=self.uri,
            messaging_service_sid=self.messaging_service_sid,
            error_code=self.error_code,
            error_message=self.error_message,
            sms_id=self.sms_id,
        )
