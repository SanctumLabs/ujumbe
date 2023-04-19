from typing import Any
from abc import ABCMeta, abstractmethod


class Consumer(metaclass=ABCMeta):
    """A generic consumer that can consume events/messages"""

    @abstractmethod
    def consume(self) -> Any:
        raise NotImplementedError()
