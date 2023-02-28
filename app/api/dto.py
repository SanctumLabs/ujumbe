"""
Base Data Transfer Objects
"""
from typing import Generic, TypeVar, Optional
from pydantic.generics import GenericModel

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
class ApiResponse(GenericModel, Generic[DataT]):
    """
    Represents a successful ApiResponse sent back to a client
    """

    status: int = 200
    data: Optional[DataT]
    message: Optional[str] = None

    class Config:
        """
        ApiResponse Config
        """

        schema_extra = {"example": {"status": 200}}


# pylint: disable=too-few-public-methods
class BadRequest(ApiResponse):
    """
    Represents a BadRequest response
    """

    status: int = 400

    class Config:
        """
        BadRequest Config
        """

        schema_extra = {"example": {"status": 400, "message": "Invalid JSON"}}