"""
Contains Generic Repository that is used to handle CRUD operations against a data source.
"""
from typing import Iterator
from abc import ABCMeta, abstractmethod
from .entities.unique_id import UniqueId
from .entities.entity import Entity


class Repository(metaclass=ABCMeta):
    """A generic repository"""

    @abstractmethod
    def add(self, entity: Entity) -> Entity:
        """
        Adds records to a datasource
        Args:
            entity (Entity): Entity to persist or add to a datasource
        Returns:
            entity (Entity)
        """
        raise NotImplementedError()

    @abstractmethod
    def remove(self, entity: Entity):
        """
        Removed entity record from datasource. Depending on the implementation this could raise a NotFoundException if
        the entity does not exist in the datasource.
        Args:
            entity (Entity): Entity to remove
        Returns:
            None
        """
        raise NotImplementedError()

    @abstractmethod
    def get_by_id(self, id: str) -> Entity:
        """
        Retrieves a record from a datasource given its ID
        Args:
            id (str): unique identifier for the entity
        Returns:
            Entity if found
        """
        raise NotImplementedError()

    @abstractmethod
    def get_all(self) -> Iterator[Entity]:
        """
        Retrieves all records from a given data source
        Returns:
            Collection of Entity records
        """
        raise NotImplementedError()

    @abstractmethod
    def update(self, entity: Entity):
        """
        Updates a given entity record at the datasource. Note that this does not perform an upsert if the record does
        not exist. If the record is non-existent a NotFoundException will be raised. The caller will need to handle this
        exception appropriately.
        Args:
            entity (Entity): Entity to update
        Returns:
            None
        """
        raise NotImplementedError()

    def __getitem__(self, index) -> Entity:
        return self.get_by_id(index)

    @staticmethod
    def next_id() -> UniqueId:
        """
        Convenience function that can be used to get a newly generated unique ID
        Returns: UniqueId
        """
        return UniqueId()

    @property
    def name(self) -> str:
        """Name of the class, can be used as a log prefix or for tracing"""
        return self.__class__.__name__
