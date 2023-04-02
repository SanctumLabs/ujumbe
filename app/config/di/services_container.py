from dependency_injector import containers, providers
from app.services.sms_producer import SmsProducer
from app.services.sms_service import UjumbeSmsService
from app.settings import KafkaSettings


class ServicesContainer(containers.DeclarativeContainer):
    """
    Dependency Injector Container for wrapper for 3rd Party services or external services

    see https://github.com/ets-labs/python-dependency-injector for more details
    """

    gateways = providers.DependenciesContainer()
    config = providers.Configuration(pydantic_settings=[KafkaSettings()])

    submit_sms_producer = providers.Factory(
        SmsProducer,
        kafka_producer=gateways.kafka_producer_client,
        topic=config.submit_sms_topic
    )

    send_sms_producer = providers.Factory(
        SmsProducer,
        kafka_producer=gateways.kafka_producer_client,
        topic=config.send_sms_topic
    )

    sms_service = providers.Factory(
        UjumbeSmsService,
        sms_client=gateways.sms_client
    )
