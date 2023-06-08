from __future__ import annotations
from abc import ABCMeta, abstractmethod


class SmsService(metaclass=ABCMeta):
    """A generic sms service that handle sending out SMSes via 3rd Party services"""

    @abstractmethod
    def send(self, sms):
        raise NotImplementedError()

    @property
    def name(self) -> str:
        """
        Convenience method to retrieve the class name
        Returns: Class name
        """
        return self.__class__.__name__
