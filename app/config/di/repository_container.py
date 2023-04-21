from dependency_injector import containers, providers
from app.database.sms_repository import SmsDatabaseRepository
from app.database.sms_response_repository import SmsResponseDatabaseRepository


class RepositoryContainer(containers.DeclarativeContainer):
    """
    Dependency Injector Container for Repositories

    see https://github.com/ets-labs/python-dependency-injector for more details
    """

    gateways = providers.DependenciesContainer()

    sms_repository = providers.Factory(
        SmsDatabaseRepository, db_client=gateways.database_client
    )

    sms_response_repository = providers.Factory(
        SmsResponseDatabaseRepository, db_client=gateways.database_client
    )
