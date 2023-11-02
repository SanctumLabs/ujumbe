"""
Sms Delivery status contains the state of the sms delivery
"""
from enum import Enum
import inflection
from sanctumlabs.messageschema.events.notifications.sms.v1.data_pb2 import SmsStatus


class SmsDeliveryStatus(Enum):
    """
    Enum with the statuses of the sms delivery. This will default to UNKNOWN if the status can not be found.
    """

    ACCEPTED = "ACCEPTED"
    SCHEDULED = "SCHEDULED"
    CANCELED = "CANCELED"
    QUEUED = "QUEUED"
    SENDING = "SENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    DELIVERED = "DELIVERED"
    UNDELIVERED = "UNDELIVERED"
    RECEIVING = "RECEIVING"
    RECEIVED = "RECEIVED"
    READ = "READ"
    PENDING = "PENDING"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: str) -> "SmsDeliveryStatus":
        value = inflection.underscore(value).upper()
        for member in cls:
            if member.value == value:
                return member
        return cls.UNKNOWN

    def to_proto(self) -> SmsStatus:
        """Converts this enum to protobuf enum
        Returns:
            SmsStatus: protobuf enum
        """
        descriptor = SmsStatus.DESCRIPTOR
        proto_value = descriptor.values_by_name[self.value]
        return proto_value
