from typing import Optional
from dataclasses import dataclass
from app.core.domain.entities.value_object import ValueObject


@dataclass
class SmsPrice(ValueObject):
    price: Optional[str] = None
    currency: Optional[str] = None

    def __post_init__(self):
        if self.price:
            if not self.price.replace(".", "", 1).isdigit():
                raise ValueError(f"Price {self.price} is not valid")
