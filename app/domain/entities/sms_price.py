from dataclasses import dataclass
from app.core.domain.entities.value_object import ValueObject


@dataclass
class SmsPrice(ValueObject):
    price: str
    price_unit: str
