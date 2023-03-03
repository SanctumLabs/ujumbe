from dataclasses import dataclass, field
from nanoid import generate


@dataclass(frozen=True)
class UniqueId:
    value: str = field(default_factory=generate)
