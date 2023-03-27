from dataclasses import dataclass
from .entity import Entity
from ..mixins import BusinessRuleValidationMixin


@dataclass(frozen=True)
class AggregateRoot(BusinessRuleValidationMixin, Entity):
    """Consists of 1+ entities, Spans transaction boundaries"""
