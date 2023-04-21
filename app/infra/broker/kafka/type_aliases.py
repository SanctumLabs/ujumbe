from typing import Callable, TypeAlias
from confluent_kafka import Message

# Delivery report handler that can be used by clients to handle deliver reports produced by Kafka producer client
DeliverReportHandler: TypeAlias = Callable[[Exception, Message], None]
