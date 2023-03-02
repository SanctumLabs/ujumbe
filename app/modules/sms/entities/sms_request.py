"""
SMS Request
"""

import re
from pydantic import BaseModel, validator


class SmsRequest(BaseModel):
    """
    SMS Request Payload DTO
    """

    phone_number: str
    message: str

    @validator("message")
    def message_must_be_valid(cls, m: str):
        """
        Validates message
        """
        if len(m) == 0:
            raise ValueError("must not be empty")
        return m

    @validator("phone_number")
    def phone_number_must_be_valid(cls, phone: str):
        """
        Validates message
        """
        pattern = r"^\+\d{1,3}\d{3,}$"
        match = re.match(pattern, phone)

        if not match:
            raise ValueError("phone number is not valid")
        return phone
