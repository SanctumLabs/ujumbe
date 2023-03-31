"""
SMS Database repository that handles CRUD operations on an SMS entity
"""
from app.domain.entities.sms import Sms
from app.domain.sms.sms_repositoty import SmsRepository
from app.infra.database.database_client import DatabaseClient


class SmsDatabaseRepository(SmsRepository):
    def __init__(self, db_client: DatabaseClient):
        self.db_client = db_client

    def update(self, sms: Sms):
        pass

    def add(self, entity: Sms):
        pass

    def remove(self, entity: Sms):
        pass

    def get_by_id(self, id: str) -> Sms:
        pass
