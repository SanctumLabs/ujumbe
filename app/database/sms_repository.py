"""
SMS Database repository that handles CRUD operations on an SMS entity
"""
from typing import Iterator, Optional

from app.domain.entities.sms import Sms
from app.domain.repositories.sms_repository import SmsRepository
from app.domain.services.exceptions import SmsNotFoundError
from app.infra.database.database_client import DatabaseClient
from app.infra.logger import log as logger
from app.database.models.sms_model import Sms as SmsModel
from .mapper import map_sms_entity_to_model, map_sms_model_to_entity


class SmsDatabaseRepository(SmsRepository):
    """
    Handles CRUD operations on SmsModel
    """

    def __init__(self, db_client: DatabaseClient):
        self.db_client = db_client
        self.session_factory = self.db_client.session

    def add(self, entity: Sms) -> Sms:
        try:
            with self.session_factory() as session:
                sms = map_sms_entity_to_model(entity)
                session.add(sms)
                session.commit()
                session.refresh(sms)
                return map_sms_model_to_entity(sms)
        except Exception as exc:
            logger.error(f"{self.name}> Failed to persist sms {entity}. {exc}")
            raise exc

    def get_by_id(self, sid: str) -> Sms:
        with self.session_factory() as session:
            sms_model: SmsModel = (
                session.query(SmsModel).filter(SmsModel.identifier == sid).first()
            )
            if not sms_model:
                raise SmsNotFoundError(sid)

            return map_sms_model_to_entity(sms_model)

    def get_all(self) -> Iterator[Sms]:
        with self.session_factory() as session:
            sms_models = session.query(SmsModel).all()
            smses = map(map_sms_model_to_entity, sms_models)
            return list(smses)

    def update(self, sms: Sms):
        with self.session_factory() as session:
            sms_model: Optional[SmsModel] = (
                session.query(SmsModel)
                .filter(SmsModel.identifier == sms.id.value)
                .first()
            )
            if not sms_model:
                raise SmsNotFoundError(sms.id.value)

            # We only update the status of the SMS, as at this point
            sms_model.status = sms.status

            session.add(sms_model)
            session.commit()

    def remove(self, entity: Sms):
        with self.session_factory() as session:
            sms_model = (
                session.query(SmsModel)
                .filter(SmsModel.identifier == entity.id.value)
                .first()
            )
            if not sms_model:
                raise SmsNotFoundError(entity.id.value)
            session.delete(sms_model)
            session.commit()
