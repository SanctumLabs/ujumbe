from typing import Union
from datetime import datetime
from dataclasses import dataclass
from app.core.domain.entities.value_object import ValueObject

DATE_PATTERN = "%d, %B %Y %H:%M:%S +0000"


@dataclass
class SmsDate(ValueObject):
    date_created: Union[datetime, str]
    date_sent: Union[datetime, str]
    date_updated: Union[datetime, str]

    def __post_init__(self):
        created_date = datetime.strptime(self.date_created, DATE_PATTERN) if isinstance(self.date_created,
                                                                                        str) else self.date_created
        sent_date = datetime.strptime(self.date_sent, DATE_PATTERN) if isinstance(self.date_sent,
                                                                                  str) else self.date_sent
        updated_date = datetime.strptime(self.date_updated, DATE_PATTERN) if isinstance(self.date_updated,
                                                                                        str) else self.date_updated

        if created_date > sent_date:
            raise ValueError(f"Created date: {self.date_created} cannot be after Sent Date: {self.date_sent}")

        if created_date > updated_date:
            raise ValueError(f"Created date: {self.date_created} cannot be after Date Updated: {self.date_updated}")
