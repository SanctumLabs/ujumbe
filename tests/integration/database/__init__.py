import unittest
from app.infra.database.database_client import DatabaseClient, DatabaseClientParams
from testcontainers.postgres import PostgresContainer

TEST_DATABASE_VERSION = "postgres:15.2-alpine"
TEST_DATABASE_USERNAME = "ujumbe-user"
TEST_DATABASE_PASSWORD = "ujumbe-password"
TEST_DATABASE_NAME = "ujumbedb"
TEST_DATABASE_PORT = 5432
TEST_DATABASE_DRIVER = "psycopg2"
TEST_DATABASE_DIALECT = "postgresql"


class BaseIntegrationTestCases(unittest.TestCase):
    started_container: PostgresContainer = None
    client: DatabaseClient

    @classmethod
    def setUpClass(cls) -> None:
        postgres_container = PostgresContainer(image=TEST_DATABASE_VERSION, port=TEST_DATABASE_PORT,
                                               user=TEST_DATABASE_USERNAME, password=TEST_DATABASE_PASSWORD,
                                               dbname=TEST_DATABASE_NAME, driver=TEST_DATABASE_DRIVER)

        cls.started_container = postgres_container.start()
        port = int(cls.started_container.get_exposed_port(TEST_DATABASE_PORT))

        params = DatabaseClientParams(
            host=cls.started_container.get_container_host_ip(),
            username=TEST_DATABASE_USERNAME,
            password=TEST_DATABASE_PASSWORD,
            database=TEST_DATABASE_NAME,
            port=port,
            dialect=TEST_DATABASE_DIALECT,
            driver=TEST_DATABASE_DRIVER,
            logging_enabled=True,
        )
        cls.client = DatabaseClient(params=params)
        cls.client.create_database()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.drop_database()
        cls.started_container.stop()
