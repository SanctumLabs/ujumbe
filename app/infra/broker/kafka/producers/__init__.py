import socket
from typing import Optional
from abc import abstractmethod, ABCMeta
from app.infra.broker.kafka.message import ProducerMessage
from app.infra.broker.kafka.type_aliases import DeliverReportHandler
from ..config import KafkaProducerConfig


class KafkaProducer(metaclass=ABCMeta):
    def __init__(self, config: KafkaProducerConfig):
        security_config = config.security

        self.conf = {
            "bootstrap.servers": config.bootstrap_servers,
            "client.id": config.client_id or socket.gethostname(),
        }

        if security_config:
            if security_config.security_protocol:
                self.conf["security.protocol"] = security_config.security_protocol
            if security_config.sasl_password and security_config.sasl_mechanisms and security_config.sasl_username:
                self.conf["sasl.mechanisms"] = security_config.sasl_mechanisms
                self.conf["sasl.username"] = security_config.sasl_password
                self.conf["sasl.password"] = security_config.sasl_password

    @abstractmethod
    def produce(self,
                message: ProducerMessage,
                report_callback: Optional[DeliverReportHandler] = None,
                **kwargs):
        """
        Produces a message to a topic on the cluster
        Args:
            message (ProducerMessage): message to be sent to topic on cluster
            **kwargs:
                serializer (Serializer): optional serializer to use when sending message
            report_callback (DeliverReportHandler): optional callable to handle deliver reports

        Returns:
            None
        """
        raise NotImplementedError("")

    @property
    def log_prefix(self):
        return self.__class__.__name__
