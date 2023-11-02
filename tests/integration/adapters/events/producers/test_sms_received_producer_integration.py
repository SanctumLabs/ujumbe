import unittest
from typing import cast
import pytest
from faker import Faker
from eventmsg_adaptor.event_streams import AsyncEventStream
from eventmsg_adaptor import factory
from eventmsg_adaptor.config import Config, AdapterConfigs
from eventmsg_adaptor.config.kafka import KafkaConfig, KafkaSchemaRegistryConfig

from app.domain.entities.sms import Sms
from app.adapters.events.producers.sms_received_producer import SmsReceivedProducer
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.message import Message
from app.domain.entities.sms_status import SmsDeliveryStatus

from tests.integration.adapters import BaseKafkaIntegrationTestCase

fake = Faker()


@pytest.mark.integration
class SmsReceivedProducerIntegrationTestCase(BaseKafkaIntegrationTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.topic = "test_topic"

        event_adapter_config = Config(
            service_name="ujumbe-test",
            default_adapter="kafka",
            adapters=AdapterConfigs(
                kafka=KafkaConfig(
                    bootstrap_servers=[self.kafka_bootstrap_server],
                    schema_registry=KafkaSchemaRegistryConfig(
                        schema_registry_url=self.kafka_schema_registry,
                        schema_registry_user_info=_kafka_settings.kafka_schema_registry_user_info
                    )
                )
            )
        )

        self.event_producer_client = cast(AsyncEventStream,
                                          factory(config=event_adapter_config, adapter_name="aiokafka"))

        self.sms_received_producer = SmsReceivedProducer(
            topic=self.topic, event_stream=self.event_producer_client
        )

    @unittest.skip(
        "Kafka Schema registry is failing to connect to Kafka broker. This needs to be resolved or mocked"
    )
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
            status=SmsDeliveryStatus.PENDING,
        )

        self.sms_received_producer.publish_message(mock_sms)

        actual_message = self.kafka_consumer.consume()
        self.assertIsNotNone(actual_message)


if __name__ == "__main__":
    unittest.main()
