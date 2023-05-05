"""
Contains wrapper for the database client that handles connection to an underlying database
"""
from typing import Callable
from dataclasses import dataclass
from contextlib import contextmanager, AbstractContextManager
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import Session, sessionmaker, scoped_session
from app.database.models import Base


@dataclass
class DatabaseClientParams:
    host: str
    port: int
    database: str
    username: str
    password: str
    logging_enabled: bool
    dialect: str = "postgresql"
    driver: str = "psycopg2"
    autocommit: bool = False
    autoflush: bool = False

    @property
    def drivername(self) -> str:
        return f"{self.dialect}+{self.driver}"


class DatabaseClient:
    """
    DatabaseClient is a client that knows how to connect to a database. This coule be a wrapper around any type of ORM
    or a custom client
    """

    def __init__(self, params: DatabaseClientParams):
        url = URL.create(
            drivername=params.drivername,
            host=params.host,
            port=params.port,
            username=params.username,
            password=params.password,
            database=params.database,
        )

        self.engine = create_engine(url=url, echo=params.logging_enabled)
        self.session_factory = scoped_session(
            sessionmaker(
                autocommit=params.autocommit,
                autoflush=params.autoflush,
                bind=self.engine,
            )
        )

    def create_database(self) -> None:
        Base.metadata.create_all(self.engine)

    def drop_database(self) -> None:
        Base.metadata.drop_all(self.engine)

    @contextmanager
    def session(self) -> Callable[..., AbstractContextManager[Session]]:
        session: Session = self.session_factory()

        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
