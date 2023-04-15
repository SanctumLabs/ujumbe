from typing import Optional
import pytz

from faker import Faker

from app.domain.entities.sms_status import SmsDeliveryStatus
from app.domain.entities.sms_type import SmsType
from app.domain.entities.sms_response import SmsResponse
from app.domain.entities.sms_date import SmsDate
from app.domain.entities.sms_price import SmsPrice

fake = Faker()


def create_mock_sms_response(sms_identifier: Optional[str] = fake.uuid4()) -> SmsResponse:
    date_created = fake.past_datetime(tzinfo=pytz.UTC)
    date_sent = fake.future_datetime(tzinfo=pytz.UTC)
    date_updated = fake.future_datetime(tzinfo=pytz.UTC)
    account_sid = fake.uuid4()
    sid = fake.uuid4()
    direction = SmsType.OUTBOUND
    num_media = 0
    num_segments = 0
    price = 1.2
    currency = "USD"
    status = SmsDeliveryStatus.PENDING
    subresource_uris = {}
    uri = "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXX/Messages/SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.json"
    messaging_service_sid = fake.uuid4()
    error_code = None
    error_message = None

    sms_date = SmsDate(
        date_sent=date_sent,
        date_updated=date_updated,
        date_created=date_created
    )

    sms_price = SmsPrice(
        price=price,
        currency=currency
    )

    sms_type = SmsType(direction)

    sms_response = SmsResponse(
        sms_id=sms_identifier,
        account_sid=account_sid,
        sid=sid,
        sms_date=sms_date,
        sms_type=sms_type,
        num_media=num_media,
        num_segments=num_segments,
        price=sms_price,
        status=status,
        subresource_uris=subresource_uris,
        uri=uri,
        messaging_service_sid=messaging_service_sid,
        error_code=error_code,
        error_message=error_message
    )

    return sms_response
