from enum import Enum
import inflection


class MessageSchemaType(Enum):
    """
    The message schema type for the message, defaults to JSON for unknown messages
    """
    PROTO = "PROTO"
    AVRO = "AVRO"
    JSON = "JSON"

    @classmethod
    def _missing_(cls, value: str) -> "MessageSchemaType":
        value = inflection.underscore(value).upper()
        for member in cls:
            if member.value == value:
                return member
        return cls.JSON

    def __str__(self):
        return f"{self.value}"
