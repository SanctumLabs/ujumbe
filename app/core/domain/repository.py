from typing import Iterator
from abc import ABCMeta, abstractmethod
from .entities.unique_id import UniqueId
from .entities.entity import Entity


class Repository(metaclass=ABCMeta):
    """A generic repository"""

    @abstractmethod
    def add(self, entity: Entity):
        raise NotImplementedError()

    @abstractmethod
    def remove(self, entity: Entity):
        raise NotImplementedError()

    @abstractmethod
    def get_by_id(self, id: str) -> Entity:
        raise NotImplementedError()

    @abstractmethod
    def get_all(self) -> Iterator[Entity]:
        raise NotImplementedError()

    def __getitem__(self, index) -> Entity:
        return self.get_by_id(index)

    @staticmethod
    def next_id() -> UniqueId:
        return UniqueId()
