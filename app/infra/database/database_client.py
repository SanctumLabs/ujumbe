from typing import Callable
from contextlib import contextmanager, AbstractContextManager
from sqlalchemy import create_engine, orm
from sqlalchemy.orm import Session
from .models import Base


class DatabaseClient:
    def __init__(self, db_url: str, logging_enabled: bool):
        self.engine = create_engine(url=db_url, echo=logging_enabled)
        self.session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        )

    def create_database(self) -> None:
        Base.metadata.create_all(self.engine)

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
