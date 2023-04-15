from typing import Optional
from dataclasses import dataclass, field
from nanoid import generate


@dataclass(frozen=True)
class UniqueId:
    value: str = field(default_factory=generate, hash=True)

    @classmethod
    def next_id(
        cls, token: Optional[str] = None, size: Optional[int] = None
    ) -> "UniqueId":
        """
        Generates the next id
        Args:
            token: Token is optional and is the characters used to generate a unique ID
            size: is optional and is the size of the id to generate

        Returns:
            A unique generated id
        """
        if token and not size:
            return UniqueId(value=generate(token))
        if token and size:
            return UniqueId(value=generate(alphabet=token, size=size))
        return UniqueId(value=generate())

    def __len__(self) -> int:
        return len(self.value)

    def __eq__(self, other: "UniqueId") -> bool:
        return self.value == other.value
