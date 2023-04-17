"""
SMS Response Database repository that handles CRUD operations on an SMS Response entity
"""
from typing import Iterator, Optional

from app.domain.entities.sms_response import SmsResponse
from app.domain.sms.sms_repository import SmsRepository
from app.domain.sms.exceptions import SmsNotFoundError
from app.infra.database.database_client import DatabaseClient
from app.infra.logger import log as logger
from app.database.models.sms_model import Sms as SmsModel
from app.database.models.sms_response_model import SmsResponse as SmsResponseModel
from .mapper import (
    map_sms_response_entity_to_model,
    map_sms_response_model_to_entity,
)


class SmsResponseDatabaseRepository(SmsRepository):
    """
    SMS Response Database Repository handles CRUD operations on the SmsResponseModel
    """

    def __init__(self, db_client: DatabaseClient):
        self.db_client = db_client
        self.session_factory = self.db_client.session

    def add(self, entity: SmsResponse) -> SmsResponse:
        try:
            with self.session_factory() as session:
                sms = (
                    session.query(SmsModel)
                    .filter(SmsModel.identifier == entity.sms_id)
                    .first()
                )
                if not sms:
                    raise SmsNotFoundError(entity.sms_id)

                sms_response = map_sms_response_entity_to_model(entity)
                sms_response.sms_id = sms.id

                session.add(sms_response)
                session.commit()

                return entity
        except Exception as exc:
            logger.error(f"Failed to persist sms response {entity}", exc)
            raise exc

    def get_by_id(self, sid: str) -> SmsResponse:
        with self.session_factory() as session:
            sms_response_model: SmsResponseModel = (
                session.query(SmsResponseModel)
                .filter(SmsResponseModel.identifier == sid)
                .first()
            )
            if not sms_response_model:
                raise SmsNotFoundError(sid)

            return map_sms_response_model_to_entity(sms_response_model)

    def get_all(self) -> Iterator[SmsResponse]:
        with self.session_factory() as session:
            sms_models = session.query(SmsResponseModel).all()
            return list(map(map_sms_response_model_to_entity, sms_models))

    def update(self, sms_response: SmsResponse):
        with self.session_factory() as session:
            sms_model: Optional[SmsResponseModel] = (
                session.query(SmsResponseModel)
                .filter(SmsResponseModel.identifier == sms_response.id.value)
                .first()
            )
            if not sms_model:
                raise SmsNotFoundError(sms_response.id.value)

            # We only update the status, we don't want to update other metadata as at this point we assume
            # that the SMS Response was received from an earlier request and persisted
            # & now we need to track the status
            sms_model.status = sms_response.status

            session.add(sms_model)
            session.commit()

    def remove(self, entity: SmsResponse):
        with self.session_factory() as session:
            sms_model = (
                session.query(SmsResponseModel)
                .filter(SmsResponseModel.identifier == entity.id.value)
                .first()
            )
            if not sms_model:
                raise SmsNotFoundError(entity.id.value)
            session.delete(sms_model)
            session.commit()
