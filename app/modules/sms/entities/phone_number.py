from dataclasses import dataclass
from pydantic import Field
from app.core.domain.entities.value_object import ValueObject
from app.utils.validators import is_valid_phone_number


@dataclass(frozen=True)
class PhoneNumber(ValueObject):
    value: str = Field(title="Phone number value")

    def __post_init__(self):
        """Validate phone number"""
        if not is_valid_phone_number(self.value):
            raise ValueError(f"Invalid phone number {self.value} provided")
