from dependency_injector import containers, providers
from app.services.sms_producer import SmsProducer
from app.services.sms_service import UjumbeSmsService
from app.settings import KafkaSettings
from app.infra.broker.kafka.consumers.consumer import KafkaConsumer, KafkaConsumerParams


class ServicesContainer(containers.DeclarativeContainer):
    """
    Dependency Injector Container for wrapper for 3rd Party services or external services

    see https://github.com/ets-labs/python-dependency-injector for more details
    """

    gateways = providers.DependenciesContainer()
    kafka_container = providers.DependenciesContainer()

    kafka_config = providers.Configuration(pydantic_settings=[KafkaSettings()])
    kafka_config.from_pydantic(KafkaSettings())

    sms_received_kafka_consumer_client = providers.Factory(
        KafkaConsumer,
        params=KafkaConsumerParams(
            bootstrap_servers=kafka_config.kafka_bootstrap_servers(),
            topic=kafka_config.sms_received_topic(),
            group_id=kafka_config.sms_received_group_id()
        )
    )

    submit_sms_producer = providers.Factory(
        SmsProducer,
        kafka_producer=kafka_container.kafka_producer_client,
        topic=kafka_config.sms_received_topic,
    )

    send_sms_producer = providers.Factory(
        SmsProducer,
        kafka_producer=kafka_container.kafka_sms_submitted_proto_producer_client,
        topic=kafka_config.send_sms_topic,
    )

    sms_service = providers.Factory(UjumbeSmsService, sms_client=gateways.sms_client)
