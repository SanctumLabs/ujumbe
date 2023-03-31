from dependency_injector import containers, providers
from app.database.sms_repository import SmsDatabaseRepository


class DatabaseContainer(containers.DeclarativeContainer):
    """
    Dependency Injector Container for Database repositories

    see https://github.com/ets-labs/python-dependency-injector for more details
    """

    gateways = providers.DependenciesContainer()

    sms_repository = providers.Factory(
        SmsDatabaseRepository,
        db_client=gateways.databse_client
    )
