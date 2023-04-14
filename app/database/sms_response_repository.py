"""
SMS Response Database repository that handles CRUD operations on an SMS Response entity
"""
from typing import Iterator, Optional

from app.domain.entities.sms import Sms
from app.domain.entities.sms_response import SmsResponse
from app.domain.sms.sms_repository import SmsRepository
from app.domain.sms.exceptions import SmsNotFoundError
from app.infra.database.database_client import DatabaseClient
from app.infra.logger import log as logger
from app.database.models.sms_model import Sms as SmsModel
from .mapper import map_sms_model_to_entity, map_sms_response_entity_to_model, map_sms_response_model_to_entity


class SmsResponseDatabaseRepository(SmsRepository):

    def __init__(self, db_client: DatabaseClient):
        self.db_client = db_client
        self.session_factory = self.db_client.session

    def add(self, entity: SmsResponse) -> SmsResponse:
        try:
            with self.session_factory() as session:
                sms = session.query(SmsModel).filter(SmsModel.identifier == entity.sms_id).first()
                if not sms:
                    raise SmsNotFoundError(entity.sms_id)

                sms_response = map_sms_response_entity_to_model(entity)
                sms_response.sms_id = sms.id

                session.add(sms_response)
                session.commit()

                return entity
        except Exception as e:
            logger.error(f"Failed to persist sms response {entity}", e)
            raise e

    def get_by_id(self, sid: str) -> Sms:
        with self.session_factory() as session:
            sms_model: SmsModel = session.query(SmsModel).filter(SmsModel.identifier == sid).first()
            if not sms_model:
                raise SmsNotFoundError(sid)

            return map_sms_model_to_entity(sms_model)

    def get_all(self) -> Iterator[Sms]:
        with self.session_factory() as session:
            sms_models = session.query(SmsModel).all()
            return list(map(map_sms_model_to_entity, sms_models))

    def update(self, sms: Sms):
        with self.session_factory() as session:
            sms_model: Optional[SmsModel] = session.query(SmsModel).filter(SmsModel.identifier == sms.id.value).first()
            if not sms_model:
                raise SmsNotFoundError(sms.id.value)

            # We only update the status of the SMS, we don't want to update the sender, recipient & message as at this
            # point we assume that the SMS has already been sent out & these values are now immutable
            sms_model.status = sms.status

            session.add(sms_model)
            session.commit()

    def remove(self, entity: Sms):
        with self.session_factory() as session:
            sms_model = session.query(SmsModel).filter(SmsModel.identifier == entity.id.value).first()
            if not sms_model:
                raise SmsNotFoundError(entity.id.value)
            session.delete(sms_model)
            session.commit()
