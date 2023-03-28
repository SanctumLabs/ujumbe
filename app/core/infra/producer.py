from abc import ABCMeta, abstractmethod


class Producer(metaclass=ABCMeta):
    """A generic producer that can emits events/messages"""

    @abstractmethod
    def publish_message(self, message):
        raise NotImplementedError()
