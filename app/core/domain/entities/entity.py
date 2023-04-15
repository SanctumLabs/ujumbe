from dataclasses import dataclass, field
from .unique_id import UniqueId


@dataclass(frozen=True, kw_only=True)
class Entity:
    id: UniqueId = field(hash=True, default_factory=UniqueId.next_id)

    @classmethod
    def next_id(cls) -> UniqueId:
        return UniqueId.next_id()

    def __eq__(self, other: "Entity") -> bool:
        return other.id == self.id
