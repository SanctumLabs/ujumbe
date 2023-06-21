"""
Sms Repository handling CRUD operations on an SMS & SMS Response
"""
from abc import ABCMeta
from app.core.domain.repository import Repository


class SmsRepository(Repository, metaclass=ABCMeta):
    """Sms Repository"""

    @property
    def name(self) -> str:
        """Name of the class, can be used as a log prefix or for tracing"""
        return self.__class__.__name__
