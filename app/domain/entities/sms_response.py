"""
SMS Response is the response received from a 3rd Party SMS Provider with status information about the SMS that was
delivered.
"""
from typing import Dict, Optional
from pydantic import BaseModel
from app.core.domain.entities.entity import Entity
from .sms_status import SmsDeliveryStatus
from .sms_date import SmsDate
from .sms_price import SmsPrice
from .sms_type import SmsType


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
    messaging_service_sid: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
