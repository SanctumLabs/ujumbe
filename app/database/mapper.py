from app.core.domain.entities.unique_id import UniqueId
from app.domain.entities.sms import Sms
from app.domain.entities.sms_response import SmsResponse
from app.domain.entities.sms_date import SmsDate
from app.domain.entities.sms_price import SmsPrice
from app.domain.entities.sms_type import SmsType
from app.domain.entities.message import Message
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.sms_status import SmsDeliveryStatus
from app.database.models.sms_model import Sms as SmsModel
from app.database.models.sms_response_model import SmsResponse as SmsResponseModel


def map_sms_model_to_entity(model: SmsModel) -> Sms:
    """"""
    sms_id = UniqueId(value=model.identifier)
    sender_phone_number = model.sender
    sender = PhoneNumber(value=sender_phone_number)

    recipient_phone_number = model.recipient
    recipient = PhoneNumber(value=recipient_phone_number)

    message_text = model.message
    message = Message(value=message_text)

    status = model.status
    delivery_status = SmsDeliveryStatus(value=status)

    response = model.response
    sms_response = map_sms_response_model_to_entity(response) if response else None

    return Sms(
        id=sms_id,
        sender=sender,
        recipient=recipient,
        message=message,
        status=delivery_status,
        response=sms_response,
    )


def map_sms_entity_to_model(entity: Sms) -> SmsModel:
    return SmsModel(
        identifier=entity.id.value,
        sender=entity.sender.value,
        recipient=entity.recipient.value,
        message=entity.message.value,
        status=entity.status,
        response=map_sms_response_entity_to_model(entity.response)
        if entity.response
        else None,
    )


def map_sms_response_model_to_entity(model: SmsResponseModel) -> SmsResponse:
    sms_date = SmsDate(
        date_sent=model.date_sent,
        date_updated=model.date_updated,
        date_created=model.date_created,
    )

    sms_price = SmsPrice(price=model.price, currency=model.currency)

    sms_type = SmsType(model.direction)
    status = SmsDeliveryStatus(model.status)

    return SmsResponse(
        id=UniqueId(model.identifier),
        account_sid=model.account_sid,
        sid=model.sid,
        sms_date=sms_date,
        sms_type=sms_type,
        num_media=model.num_media,
        num_segments=model.num_segments,
        price=sms_price,
        status=status,
        subresource_uris=model.subresource_uris,
        uri=model.uri,
        messaging_service_sid=model.messaging_service_sid,
        error_code=model.error_code,
        error_message=model.error_message,
        sms_id=model.sms.identifier,
    )


def map_sms_response_entity_to_model(entity: SmsResponse) -> SmsResponseModel:
    return SmsResponseModel(
        identifier=entity.id.value,
        account_sid=entity.account_sid,
        sid=entity.sid,
        date_sent=entity.sms_date.date_sent,
        date_updated=entity.sms_date.date_updated,
        date_created=entity.sms_date.date_created,
        direction=entity.sms_type,
        num_media=entity.num_media,
        num_segments=entity.num_segments,
        price=entity.price.price,
        currency=entity.price.currency,
        status=entity.status,
        subresource_uris=entity.subresource_uris,
        uri=entity.uri,
        messaging_service_sid=entity.messaging_service_sid,
        error_code=entity.error_code,
        error_message=entity.error_message,
    )
