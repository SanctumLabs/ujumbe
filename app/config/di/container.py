from dependency_injector import containers, providers
from app.domain.sms.submit_sms import SubmitSmsService
from app.infra.broker.producer import KafkaProducer
from app.services.submit_sms_producer import SubmitSmsProducer
from app.settings import KafkaSettings


class Container(containers.DeclarativeContainer):
    """
    Dependency Injector Container

    see https://github.com/ets-labs/python-dependency-injector for more details
    """

    kafka_settings = providers.Configuration(pydantic_settings=KafkaSettings())
    kafka_producer_client = providers.Singleton(KafkaProducer)

    submit_sms_producer = providers.Factory(
        SubmitSmsProducer,
        kafka_producer=kafka_producer_client,
        topic=kafka_settings.submit_sms_topic
    )

    submit_sms = providers.Factory(
        SubmitSmsService,
        producer=submit_sms_producer
    )
