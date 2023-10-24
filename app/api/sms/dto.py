"""
DTO objects for SMS endpoint
"""
from typing import List

from pydantic import field_validator, BaseModel


class SmsRequestDto(BaseModel):
    """
    SMS Request Payload DTO
    """

    sender: str | None = None
    recipient: str
    message: str

    @field_validator("message")
    @classmethod
    def message_must_be_valid(cls, m: str):
        """
        Validates message
        """
        if len(m) == 0:
            raise ValueError("must not be empty")
        return m


class SmsResponseDto(BaseModel):
    """
    SMS Response DTO
    """

    message: str


class BulkSmsRequestDto(BaseModel):
    """
    SMS Request Payload DTO
    """

    recipients: List[str]
    message: str

    @field_validator("message")
    @classmethod
    def message_must_be_valid(cls, m: str):
        """
        Validates message
        """
        if len(m) == 0:
            raise ValueError("must not be empty")
        return m


class SmsCallbackRequestDto(BaseModel):
    """
    SMS Callback Payload DTO
    """

    AccountSid: str
    From: str
    MessageSid: str
    MessageStatus: str
    SmsSid: str
    SmsStatus: str
