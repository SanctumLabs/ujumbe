"""
SMS Database repository that handles CRUD operations on an SMS entity
"""
from typing import Iterator

from app.domain.entities.sms import Sms
from app.domain.sms.sms_repositoty import SmsRepository
from app.domain.sms.exceptions import SmsNotFoundError
from app.infra.database.database_client import DatabaseClient
from .models import Sms as SmsModel
from .mapper import sms_entity_to_model, sms_model_to_entity


class SmsDatabaseRepository(SmsRepository):

    def __init__(self, db_client: DatabaseClient):
        self.db_client = db_client
        self.session_factory = self.db_client.session

    def add(self, entity: Sms):
        with self.session_factory() as session:
            sms = sms_entity_to_model(entity)
            session.add(sms)
            session.commit()
            session.refresh(sms)

    def get_by_id(self, sid: str) -> Sms:
        with self.session_factory() as session:
            sms_model: SmsModel = session.query(SmsModel).filter(SmsModel.id == sid).first()
            if not sms_model:
                raise SmsNotFoundError(sid)

            return sms_model_to_entity(sms_model)

    def get_all(self) -> Iterator[Sms]:
        with self.session_factory() as session:
            sms_models = session.query(SmsModel).all()
            return map(sms_model_to_entity, sms_models)

    def update(self, sms: Sms):
        pass

    def remove(self, entity: Sms):
        with self.session_factory() as session:
            sms_model = session.query(SmsModel).filter(SmsModel.id == entity.id.value).first()
            if not sms_model:
                raise SmsNotFoundError(entity.id.value)
            session.delete(sms_model)
            session.commit()
