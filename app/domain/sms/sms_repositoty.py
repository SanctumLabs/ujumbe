"""
Sms Repository handling CRUD operations on an SMS
"""
from abc import ABCMeta, abstractmethod
from app.core.domain.repository import Repository
from ..entities.sms import Sms


class SmsRepository(Repository, metaclass=ABCMeta):

    @abstractmethod
    def update(self, sms: Sms):
        """
        Updates the status of an SMS
        Args:
            sms: SMS entity
        """
        raise NotImplementedError()
