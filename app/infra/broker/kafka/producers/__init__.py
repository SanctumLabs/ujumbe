import socket
from typing import Optional
from abc import abstractmethod, ABCMeta
from app.infra.broker.kafka.message import ProducerMessage
from app.infra.broker.kafka.type_aliases import DeliverReportHandler


class KafkaProducer(metaclass=ABCMeta):
    def __init__(self, bootstrap_servers, client_id: Optional[str] = None):
        self.conf = {
            "bootstrap.servers": bootstrap_servers,
            "client.id": client_id or socket.gethostname(),
            # "security.protocol": config.kafka.kafka_security_protocol,
            # "sasl.mechanisms": config.kafka.sasl_mechanisms,
            # "sasl.username": config.kafka.sasl_password,
            # "sasl.password": config.kafka.sasl_password,
        }

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
