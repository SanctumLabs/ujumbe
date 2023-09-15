"""
SMS Callback Database repository that handles CRUD operations on an SMS Callback entity
"""
from typing import Iterator, Optional

from app.domain.entities.sms_callback import SmsCallback
from app.domain.repositories.sms_repository import SmsRepository
from app.domain.services.exceptions import (
    SmsResponseNotFoundError,
    SmsCallbackNotFoundError,
)
from app.infra.database.database_client import DatabaseClient
from app.infra.logger import log as logger
from app.database.models.sms_response_model import SmsResponse as SmsResponseModel
from app.database.models.sms_callback_model import SmsCallback as SmsCallbackModel
from .mapper import (
    map_sms_callback_entity_to_model,
    map_sms_callback_model_to_entity,
)


class SmsCallbackDatabaseRepository(SmsRepository):
    """
    SMS Callback Database Repository handles CRUD operations on the SmsCallbackModel
    """

    def __init__(self, db_client: DatabaseClient):
        self.db_client = db_client
        self.session_factory = self.db_client.session

    def add(self, entity: SmsCallback) -> SmsCallback:
        try:
            with self.session_factory() as session:
                # check if we already have this sms callback in the database
                existing_sms_callback = (
                    session.query(SmsCallbackModel)
                    .filter(SmsCallbackModel.message_sid == entity.message_sid)
                    .first()
                )

                if existing_sms_callback is not None:
                    # We only update the status(es), we don't want to update other metadata as at this point we already
                    # have an existing sms callback that was initially saved, however, the metadata is now different,
                    # i.e. the statuses have been updated. Therefore, we only need to update the statuses of this
                    # callback
                    existing_sms_callback.message_status = entity.message_status
                    existing_sms_callback.sms_status = entity.sms_status

                    session.add(existing_sms_callback)
                    session.commit()
                    return entity

                # if none exists, then this is a new sms callback to persist, we find the initial response of the
                # sms in order to find the sms we want to attach this callback to. This is because the sms database
                # model does not have metadata that can be tied to an sms callback yet, but the sms response does
                sms_response = (
                    session.query(SmsResponseModel)
                    .filter(SmsResponseModel.sid == entity.sms_sid)
                    .first()
                )
                if not sms_response:
                    raise SmsResponseNotFoundError(entity.sms_sid)

                sms = sms_response.sms

                sms_callback = map_sms_callback_entity_to_model(entity)
                sms_callback.sms_id = sms.id

                session.add(sms_callback)
                session.commit()

                return entity
        except Exception as exc:
            logger.error(
                f"{self.name}> Failed to persist sms callback {entity}. Error: {exc}",
                exc,
            )
            raise exc

    def get_by_id(self, sid: str) -> SmsCallback:
        with self.session_factory() as session:
            sms_callback_model: SmsCallbackModel = (
                session.query(SmsCallbackModel)
                .filter(SmsCallbackModel.identifier == sid)
                .first()
            )
            if not sms_callback_model:
                raise SmsCallbackNotFoundError(sid)

            return map_sms_callback_model_to_entity(sms_callback_model)

    def get_all(self) -> Iterator[SmsCallback]:
        with self.session_factory() as session:
            sms_callback_models = session.query(SmsCallbackModel).all()
            return list(map(map_sms_callback_model_to_entity, sms_callback_models))

    def update(self, entity: SmsCallback):
        with self.session_factory() as session:
            sms_callback_model: Optional[SmsCallbackModel] = (
                session.query(SmsCallbackModel)
                .filter(SmsCallbackModel.identifier == entity.id.value)
                .first()
            )

            if not sms_callback_model:
                raise SmsCallbackNotFoundError(entity.id.value)

            # We only update the status(es), we don't want to update other metadata as at this point we assume
            # that the SMS Callback was received from an earlier request and persisted and now we keep track of the
            # statuses as they come in
            sms_callback_model.message_status = entity.message_status
            sms_callback_model.sms_status = entity.sms_status

            session.add(sms_callback_model)
            session.commit()

    def remove(self, entity: SmsCallback):
        with self.session_factory() as session:
            sms_callback_model = (
                session.query(SmsCallbackModel)
                .filter(SmsCallbackModel.identifier == entity.id.value)
                .first()
            )
            if not sms_callback_model:
                raise SmsCallbackNotFoundError(entity.id.value)

            session.delete(sms_callback_model)
            session.commit()
