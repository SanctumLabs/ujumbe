from enum import Enum
import inflection


class SmsDeliveryStatus(Enum):
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
    READ = "READ"
    PENDING = "PENDING"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: str) -> 'SmsDeliveryStatus':
        value = inflection.underscore(value).upper()
        for member in cls:
            if member.value == value:
                return member
        return cls.UNKNOWN
