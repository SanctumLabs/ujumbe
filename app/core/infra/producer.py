from typing import Any
from abc import ABCMeta, abstractmethod


class Producer(metaclass=ABCMeta):
    """A generic producer that can emits events/messages"""

    @abstractmethod
    async def publish_message(self, message: Any):
        """
        Publishes a message to a broker
        Args:
            message (object): message to be sent to broker
        """
        raise NotImplementedError()

    @property
    def producer_name(self):
        """
        Producer name
        Returns: Name of producer class
        """
        return self.__class__.__name__
