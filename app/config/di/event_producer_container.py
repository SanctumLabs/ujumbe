from dependency_injector import containers, providers
from app.adapters.broker.producers.sms_received_producer import SmsReceivedProducer
from app.adapters.broker.producers.sms_submitted_producer import SmsSubmittedProducer
from app.adapters.broker.producers.sms_sent_producer import SmsSentProducer
from app.adapters.broker.producers.sms_callback_received_producer import SmsCallbackReceivedProducer

from app.settings import get_kafka_settings

_kafka_settings = get_kafka_settings()


class EventProducerContainer(containers.DeclarativeContainer):
    """
    Dependency Injector Container for wrapper for Event producers

    see https://github.com/ets-labs/python-dependency-injector for more details
    """

    infra = providers.DependenciesContainer()

    sms_received_producer = providers.Factory(
        SmsReceivedProducer,
        event_stream=infra.kafka_adapter_client,
        topic=_kafka_settings.sms_received_topic,
    )

    sms_callback_received_producer = providers.Factory(
        SmsCallbackReceivedProducer,
        async_event_stream=infra.kafka_adapter_client,
        topic=_kafka_settings.sms_callback_received_topic,
    )

    sms_submitted_producer = providers.Factory(
        SmsSubmittedProducer,
        async_event_stream=infra.kafka_adapter_client,
        topic=_kafka_settings.sms_submitted_topic,
    )

    sms_sent_producer = providers.Factory(
        SmsSentProducer,
        async_event_stream=infra.kafka_adapter_client,
        topic=_kafka_settings.sms_sent_topic,
    )
