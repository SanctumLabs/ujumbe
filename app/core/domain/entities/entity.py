from typing import ClassVar
from dataclasses import dataclass, field
from .unique_id import UniqueId


@dataclass(frozen=True, kw_only=True)
class Entity:
    id: ClassVar[UniqueId] = field(hash=True)

    @classmethod
    def next_id(cls) -> UniqueId:
        return UniqueId.next_id()

    def __eq__(self, other: "Entity") -> bool:
        return other.id == self.id
