from typing import Any
import json


class ProducerMessage:
    def __init__(self, topic: str, value: Any, key=None) -> None:
        self.topic = topic
        self.key = key
        self.value = self.convert_value_to_bytes(value)

    @classmethod
    def convert_value_to_bytes(cls, value: Any):
        if isinstance(value, dict):
            return cls.from_json(value)

        if isinstance(value, str):
            return cls.from_string(value)

        if isinstance(value, bytes):
            return cls.from_bytes(value)

        raise ValueError(f"Wrong message value type: {type(value)}")

    @classmethod
    def from_json(cls, value: Any):
        return json.dumps(
            value, indent=None, sort_keys=True, default=str, ensure_ascii=False
        )

    @classmethod
    def from_string(cls, value: Any):
        return value.encode("utf-8")

    @classmethod
    def from_bytes(cls, value: Any):
        return value
