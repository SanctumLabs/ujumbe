from dataclasses import dataclass
from pydantic import Field
from app.core.domain.entities.value_object import ValueObject

VALID_MESSAGE_LENGTH = 435


@dataclass(frozen=True)
class Message(ValueObject):
    value: str = Field(title="SMS message value")

    def __post_init__(self):
        """Validate message string"""
        if len(self.value) >= VALID_MESSAGE_LENGTH:
            raise ValueError(f"Invalid SMS message {self.value} provided")
