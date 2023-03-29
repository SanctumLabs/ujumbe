from dependency_injector import containers, providers
from app.services.submit_sms_producer import SubmitSmsProducer
from app.settings import KafkaSettings


class ServicesContainer(containers.DeclarativeContainer):
    """
    Dependency Injector Container

    see https://github.com/ets-labs/python-dependency-injector for more details
    """

    gateways = providers.DependenciesContainer()
    config = providers.Configuration(pydantic_settings=[KafkaSettings()])

    submit_sms_producer = providers.Factory(
        SubmitSmsProducer,
        kafka_producer=gateways.kafka_producer_client,
        topic=config.submit_sms_topic
    )
