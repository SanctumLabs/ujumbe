from typing import Any
from abc import ABCMeta, abstractmethod


class Producer(metaclass=ABCMeta):
    """A generic producer that can emits events/messages"""

    @abstractmethod
    def publish_message(self, message: Any):
        """
        Publishes a message to a broker
        Args:
            message (object): message to be sent to broker
        """
        raise NotImplementedError()
