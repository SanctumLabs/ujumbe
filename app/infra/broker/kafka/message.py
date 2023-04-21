"""
Wrapper for a Producer message to be used by producers when sending messages to a broker
"""
from typing import Any, Optional
import json
from uuid import uuid4
from confluent_kafka.serialization import StringSerializer


class ProducerMessage:
    """
    Producer message
    """

    def __init__(self, topic: str, value: Any, key: Optional[str] = None) -> None:
        """
        Creates an instance of a producer message
        Args:
            topic (str): Topic this message belongs to
            value (dict): Value of the message as a dictionary
            key (str): Optional Key of the message
        """
        string_serializer = StringSerializer('utf_8')
        self.topic = topic
        self.key = key or string_serializer(str(uuid4()))
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
