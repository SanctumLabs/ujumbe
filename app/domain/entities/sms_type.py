from enum import Enum
import inflection


class SmsType(Enum):
    OUTBOUND = "OUTBOUND"
    INBOUND = "INBOUND"
    OUTBOUND_API = "OUTBOUND_API"
    OUTBOUND_REPLY = "OUTBOUND_REPLY"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: str) -> "SmsType":
        value = inflection.underscore(value).upper()
        for member in cls:
            if member.value == value:
                return member
        return cls.UNKNOWN
