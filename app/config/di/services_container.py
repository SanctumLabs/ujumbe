from dependency_injector import containers, providers
from app.services.sms_received_producer import SmsReceivedProducer
from app.services.sms_received_consumer import SmsReceivedConsumer
from app.services.sms_submitted_producer import SmsSubmittedProducer
from app.services.sms_submitted_consumer import SmsSubmittedConsumer
from app.services.sms_sent_producer import SmsSentProducer
from app.services.sms_service import UjumbeSmsService
from app.settings import KafkaSettings


class ServicesContainer(containers.DeclarativeContainer):
    """
    Dependency Injector Container for wrapper for 3rd Party services or external services

    see https://github.com/ets-labs/python-dependency-injector for more details
    """

    gateways = providers.DependenciesContainer()
    kafka_container = providers.DependenciesContainer()

    kafka_config = providers.Configuration(pydantic_settings=[KafkaSettings()])
    kafka_config.from_pydantic(KafkaSettings())

    # Sms Received
    sms_received_consumer = providers.Factory(
        SmsReceivedConsumer,
        kafka_consumer=kafka_container.sms_received_protobuf_consumer
    )

    sms_received_producer = providers.Factory(
        SmsReceivedProducer,
        kafka_producer=kafka_container.sms_received_protobuf_producer,
        topic=kafka_config.sms_received_topic(),
    )

    # Sms Submitted
    sms_submitted_consumer = providers.Factory(
        SmsSubmittedConsumer,
        kafka_consumer=kafka_container.sms_submitted_protobuf_consumer
    )

    sms_submitted_producer = providers.Factory(
        SmsSubmittedProducer,
        kafka_producer=kafka_container.sms_submitted_protobuf_producer,
        topic=kafka_config.sms_submitted_topic(),
    )

    # Sms Sent producer

    sms_sent_producer = providers.Factory(
        SmsSentProducer,
        kafka_producer=kafka_container.sms_sent_protobuf_producer,
        topic=kafka_config.sms_sent_topic(),
    )

    sms_service = providers.Factory(UjumbeSmsService, sms_client=gateways.sms_client)
