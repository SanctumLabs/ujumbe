from dependency_injector import containers, providers
from app.services.sms_submitted_producer import SmsSubmittedProducer
from app.services.sms_submitted_consumer import SmsSubmittedConsumer
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

    sms_submitted_consumer = providers.Factory(
        SmsSubmittedConsumer,
        kafka_consumer=kafka_container.sms_submitted_protobuf_consumer
    )

    submit_sms_producer = providers.Factory(
        SmsSubmittedProducer,
        kafka_producer=kafka_container.sms_submitted_protobuf_producer,
        topic=kafka_config.sms_received_topic(),
    )

    send_sms_producer = providers.Factory(
        SmsSubmittedProducer,
        kafka_producer=kafka_container.sms_submitted_protobuf_producer,
        topic=kafka_config.send_sms_topic(),
    )

    sms_service = providers.Factory(UjumbeSmsService, sms_client=gateways.sms_client)
