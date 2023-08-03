"""
SMS Callback is the response received from a 3rd Party SMS Provider with status information about the SMS that was
delivered.
"""
from typing import Dict
from dataclasses import dataclass
from pydantic import BaseModel
from app.core.domain.entities.entity import Entity
from .sms_status import SmsDeliveryStatus
from .phone_number import PhoneNumber


@dataclass(frozen=True, kw_only=True)
class SmsCallback(BaseModel, Entity):
    """
    Entity denoting the callback response of an initially sent Sms.
    """

    account_sid: str
    sender: PhoneNumber
    message_sid: str
    message_status: SmsDeliveryStatus
    sms_sid: str
    sms_status: SmsDeliveryStatus

    def to_dict(self) -> Dict[str, str]:
        """
        Converts an SmsCallback to a dictionary
        Returns: Dictionary
        """
        return dict(
            id=self.id.value,
            account_sid=self.account_sid,
            message_sid=self.message_sid,
            message_status=self.message_status,
            sms_sid=self.sms_sid,
            sms_status=self.sms_status
        )

    @staticmethod
    def from_dict(data: Dict[str, str]) -> "SmsCallback":
        """
        Factory method to create an SmsCallback from a dictionary
        Args:
            data (dict): Dictionary with keys as strings and values as strings. If the specified keys are missing, they
            will be defaulted to None, required keys defaulted to None will raise ValueError exceptions during validation
        Returns:
            SmsCallback
        """
        account_sid = data.get("AccountSid", None)
        sender = data.get("From", None)
        message_sid = data.get("MessageSid", None)
        message_status = data.get("MessageStatus", SmsDeliveryStatus.UNKNOWN)
        sms_sid = data.get("SmsSid", None)
        sms_status = data.get("SmsStatus", SmsDeliveryStatus.UNKNOWN)

        if not account_sid:
            raise ValueError("Missing account sid")

        if not sender:
            raise ValueError("Missing sender")

        if not message_sid:
            raise ValueError("Missing message sid")

        if not sms_sid:
            raise ValueError("Missing sms sid")

        sender_phone_number = PhoneNumber(value=sender)
        msg_status = SmsDeliveryStatus(message_status)
        status = SmsDeliveryStatus(sms_status)

        return SmsCallback(
            account_sid=account_sid,
            sender=sender_phone_number,
            message_sid=message_sid,
            sms_sid=sms_sid,
            message_status=msg_status,
            sms_status=status
        )
