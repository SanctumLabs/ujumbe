from dataclasses import dataclass
from .unique_id import UniqueId


@dataclass(frozen=True)
class Entity:
    id: UniqueId = UniqueId()

    @classmethod
    def next_id(cls) -> UniqueId:
        return UniqueId()
