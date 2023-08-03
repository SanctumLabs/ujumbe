from typing import Any, Optional
from abc import abstractmethod
from .mixins import BusinessRuleValidationMixin


class Service(BusinessRuleValidationMixin):
    """
    Services carry domain knowledge that does not fit naturally in entities and value objects
    """

    @abstractmethod
    def execute(self, request: Any) -> Optional[Any]:
        raise NotImplementedError("Not yet implemented")

    @property
    def name(self) -> str:
        """Used to get the service name"""
        return self.__class__.__name__
