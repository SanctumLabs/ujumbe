"""
Wrapper for a Producer message to be used by producers when sending messages to a broker
"""
from typing import Any, Optional, Dict
import json


class ProducerMessage:
    """
    Producer message
    """

    def __init__(self, topic: str, value: Any, key: Optional[str] = None) -> None:
        """
        Creates an instance of a producer message
        Args:
            topic (str): Topic this message belongs to
            value (object): Value of the message as a dictionary
            key (str): Optional Key of the message
        """
        self.topic = topic
        self.key = key
        self.value = value

    @classmethod
    def convert_value_to_bytes(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return cls.from_json(value)

        if isinstance(value, str):
            return cls.from_string(value)

        if isinstance(value, bytes):
            return cls.from_bytes(value)

        return value

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

    def __repr__(self):
        return f"ProducerMessage(topic: {self.topic}, key: {self.key}, value: {self.value})"

    def to_dict(self) -> Dict[str, Any]:
        return dict(
            topic=self.topic,
            key=self.key,
            value=self.value
        )
