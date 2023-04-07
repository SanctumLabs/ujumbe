import unittest
from app.infra.database.models import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


class BaseModelTestCases(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)
        cls.session = sessionmaker(bind=cls.engine)

    @classmethod
    def tearDownClass(cls) -> None:
        with cls.session() as session:
            session.rollback()
            session.close()
