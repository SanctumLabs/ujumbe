from dependency_injector import containers, providers
from app.adapters.broker.producers.sms_received_producer import SmsReceivedProducer
from app.adapters.broker.consumers.sms_received_consumer import SmsReceivedConsumer
from app.adapters.broker.producers.sms_submitted_producer import SmsSubmittedProducer
from app.adapters.broker.consumers.sms_submitted_consumer import SmsSubmittedConsumer
from app.adapters.broker.producers.sms_callback_received_producer import (
    SmsCallbackReceivedProducer,
)
from app.adapters.broker.consumers.sms_callback_received_consumer import (
    SmsCallbackReceivedConsumer,
)
from app.adapters.broker.producers.sms_sent_producer import SmsSentProducer
from app.adapters.sms_svc.sms_service import UjumbeSmsService


class ServicesContainer(containers.DeclarativeContainer):
    """
    Dependency Injector Container for wrapper for 3rd Party services or external services

    see https://github.com/ets-labs/python-dependency-injector for more details
    """

    infra = providers.DependenciesContainer()
    event_stream = providers.DependenciesContainer()

    kafka_config = providers.Configuration()
    # TODO: load from env
    # kafka_config.from_pydantic(KafkaSettings())

    # Sms Received
    sms_received_consumer = providers.Factory(
        SmsReceivedConsumer,
        kafka_consumer=event_stream.sms_received_protobuf_consumer,
    )

    sms_received_producer = providers.Factory(
        SmsReceivedProducer,
        event_stream=event_stream.kafka_event_stream,
        topic=kafka_config.sms_received_topic(),
    )

    # Sms Callback Received

    # consumer
    sms_callback_received_consumer = providers.Factory(
        SmsCallbackReceivedProducer,
        kafka_consumer=event_stream.sms_callback_received_protobuf_consumer,
    )

    # producer
    sms_callback_received_producer = providers.Factory(
        SmsCallbackReceivedConsumer,
        kafka_producer=event_stream.sms_callback_received_protobuf_producer,
        topic=kafka_config.sms_callback_received_topic(),
    )

    # Sms Submitted
    sms_submitted_consumer = providers.Factory(
        SmsSubmittedConsumer,
        kafka_consumer=event_stream.sms_submitted_protobuf_consumer,
    )

    sms_submitted_producer = providers.Factory(
        SmsSubmittedProducer,
        kafka_producer=event_stream.sms_submitted_protobuf_producer,
        topic=kafka_config.sms_submitted_topic(),
    )

    # Sms Sent producer

    sms_sent_producer = providers.Factory(
        SmsSentProducer,
        kafka_producer=event_stream.sms_sent_protobuf_producer,
        topic=kafka_config.sms_sent_topic(),
    )

    sms_service = providers.Factory(UjumbeSmsService, sms_client=infra.sms_client)
