import unittest
import pytest
from faker import Faker
from app.domain.entities.sms import Sms
from app.services.sms_received_producer import SmsReceivedProducer
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.message import Message
from app.domain.entities.sms_status import SmsDeliveryStatus
import app.messages.events.v1.events_pb2 as events
from app.infra.broker.kafka.serializers.protobuf_serializer import KafkaProtobufSerializer
from app.infra.broker.kafka.deserializers.protobuf_deserializer import KafkaProtobufDeserializer
from app.infra.broker.kafka.producers.proto_producer import KafkaProtoProducer
from app.infra.broker.kafka.consumers.proto_consumer import KafkaProtoConsumer
from app.infra.broker.kafka.config import KafkaConsumerConfig

from . import BaseKafkaIntegrationTestCase

fake = Faker()


@pytest.mark.integration
class SmsReceivedProducerIntegrationTestCase(BaseKafkaIntegrationTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.topic = "test_topic"

        self.serializer = KafkaProtobufSerializer(
            msg_type=events.SmsReceived,
            registry_client=self.kafka_schema_registry
        )
        self.deserializer = KafkaProtobufDeserializer(msg_type=events.SmsReceived)

        self.kafka_producer = KafkaProtoProducer(params=self.producer_config, serializer=self.serializer)

        self.consumer_config = KafkaConsumerConfig(bootstrap_servers=self.kafka_bootstrap_server, topic=self.topic,
                                                   group_id="test-sms-received-group")
        self.kafka_consumer = KafkaProtoConsumer(params=self.consumer_config, deserializer=self.deserializer)

        self.sms_received_producer = SmsReceivedProducer(topic=self.topic, kafka_producer=self.kafka_producer)

    @unittest.skip("Kafka Schema registry is failing to connect to Kafka broker. This needs to be resolved or mocked")
    def test_produces_a_message_to_kafka(self):
        """Should successfully publish a message to a topic on Kafka"""
        sender_phone = "+254700000000"
        sender = PhoneNumber(value=sender_phone)
        recipient_phone = "+254700000000"
        recipient = PhoneNumber(value=recipient_phone)
        message_text = fake.text()
        message = Message(value=message_text)

        mock_sms = Sms(
            sender=sender,
            recipient=recipient,
            message=message,
            status=SmsDeliveryStatus.PENDING
        )

        self.sms_received_producer.publish_message(mock_sms)

        actual_message = self.kafka_consumer.consume()
        self.assertIsNotNone(actual_message)


if __name__ == '__main__':
    unittest.main()
