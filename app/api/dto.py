"""
Base Data Transfer Objects
"""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, ConfigDict

DataT = TypeVar("DataT")


# pylint: disable=too-few-public-methods
class ApiError(Exception):
    """
    Represents an ApiError that is sent back to a requesting client
    """

    def __init__(
        self, status: int, message: Optional[str] = None, data: Optional[any] = None
    ):
        super().__init__(message)
        self.status = status
        self.message = message
        self.data = data


# pylint: disable=too-few-public-methods
class ApiResponse(BaseModel, Generic[DataT]):
    """
    Represents a successful ApiResponse sent back to a client
    """

    status: int = 200
    data: Optional[DataT] = None
    message: Optional[str] = None
    model_config = ConfigDict(json_schema_extra={"example": {"status": 200}})


# pylint: disable=too-few-public-methods
class BadRequest(ApiResponse):
    """
    Represents a BadRequest response
    """

    status: int = 400
    model_config = ConfigDict(json_schema_extra={"example": {"status": 400, "message": "Invalid JSON"}})
