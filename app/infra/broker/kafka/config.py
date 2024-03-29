"""
Configuration dataclasses for setting up Kafka
"""
from typing import Optional, Union, List
from dataclasses import dataclass
from enum import Enum


class SecurityProtocol(Enum):
    """
    Security Protocol types to connect to brokers
    Args:
        PLAINTEXT (str): Plain text security protocol
        SASL_PLAINTEXT (str): sasl plain text
        SASL_SSL (str): sasl ssl
    """
    PLAINTEXT = "plaintext"
    SASL_PLAINTEXT = "sasl_plaintext"
    SASL_SSL = "sasl_ssl"


@dataclass
class KafkaSchemaRegistryConfig:
    """
    Kafka Schema Registry configuration class

    Args:
        url (str): URL is either the schema registry URL or the list of bootstrap servers to connect to
    """
    url: str


@dataclass
class KafkaSecurityProtocolConfig:
    """
    Security protocol configuration. This is used for setting up security settings to use while connecting to Kafka
    Args:
        security_protocol (SecurityProtocol): Security protocol to use
        sasl_mechanisms: (str): sasl mechanism to use
        sasl_username: (str): sasl username to use
        sasl_password: (str): sasl password to use
    """
    security_protocol: Optional[SecurityProtocol] = None
    sasl_mechanisms: Optional[str] = None
    sasl_username: Optional[str] = None
    sasl_password: Optional[str] = None


@dataclass
class KafkaProducerConfig:
    """
    Producer configuration
    Args:
        client_id (str): client ID
        security (KafkaSecurityProtocolConfig): Optional security configuration
    """
    bootstrap_servers: str
    client_id: Optional[str] = None
    security: Optional[KafkaSecurityProtocolConfig] = None


@dataclass
class KafkaConsumerConfig:
    """
    Args:
        bootstrap_servers (str): Kafka bootstrap servers to listen on
        topic (str): Either a single topic or a list of topics for this consumer to listen to
        group_id (str) : Group ID this consumer belongs to
        client_id (str): client ID
        security (KafkaSecurityProtocolConfig): Optional security configuration
        auto_offset_reset (str): Auto offset reset
    """
    bootstrap_servers: str
    topic: Union[str, List[str]]
    group_id: str
    client_id: Optional[str] = None
    security: Optional[KafkaSecurityProtocolConfig] = None
    auto_offset_reset: Optional[str] = "earliest"

    @property
    def topics(self) -> Union[str, List[str]]:
        if isinstance(self.topic, str):
            return [self.topic]
        else:
            return self.topic
