from datetime import datetime
from dataclasses import dataclass
from app.core.domain.entities.value_object import ValueObject


@dataclass
class SmsDate(ValueObject):
    date_created: datetime
    date_sent: datetime
    date_updated: datetime
