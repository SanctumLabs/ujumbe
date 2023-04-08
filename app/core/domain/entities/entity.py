from dataclasses import dataclass, field
from .unique_id import UniqueId


@dataclass(frozen=True, kw_only=True)
class Entity:
    id: UniqueId = field(default=UniqueId(), hash=True)

    @classmethod
    def next_id(cls) -> UniqueId:
        return UniqueId()
