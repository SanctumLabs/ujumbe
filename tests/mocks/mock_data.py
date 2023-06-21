from typing import Optional
import pytz

from faker import Faker

from app.domain.entities.sms_status import SmsDeliveryStatus
from app.domain.entities.sms_type import SmsType
from app.domain.entities.sms_response import SmsResponse
from app.domain.entities.sms_callback import SmsCallback
from app.domain.entities.phone_number import PhoneNumber
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


def create_mock_sms_callback(account_sid: str = fake.uuid4(),
                             sender_phone_number: str = "+254744444444",
                             sms_sid: str = fake.uuid4(),
                             sms_status: SmsDeliveryStatus = SmsDeliveryStatus.SENT,
                             message_sid: str = fake.uuid4(),
                             message_status: SmsDeliveryStatus = SmsDeliveryStatus.SENT) -> SmsCallback:
    sender = PhoneNumber(sender_phone_number)

    return SmsCallback(
        account_sid=account_sid,
        sender=sender,
        message_sid=message_sid,
        message_status=message_status,
        sms_sid=sms_sid,
        sms_status=sms_status
    )
