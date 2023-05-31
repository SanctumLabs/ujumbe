"""
Contains abstract Consumer
"""
from typing import Any
from abc import ABCMeta, abstractmethod


class Consumer(metaclass=ABCMeta):
    """A generic consumer that can consume events/messages"""

    @abstractmethod
    def consume(self) -> Any:
        """
        Consumes a message from a queue or topic
        Returns: Consumed message
        """
        raise NotImplementedError()

    @property
    def consumer_name(self):
        """
        Producer name
        Returns: Name of consumer class
        """
        return self.__class__.__name__

    def close(self):
        """
        Close connection to broker
        """
        raise NotImplementedError()
