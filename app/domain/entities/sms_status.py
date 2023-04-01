from enum import Enum


class SmsDeliveryStatus(Enum):
    PENDING = "PENDING"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
