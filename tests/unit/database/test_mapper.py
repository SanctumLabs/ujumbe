import pytest

from app.database.mapper import map_sms_entity_to_model, map_sms_model_to_entity
from app.database.models.sms_model import Sms as SmsModel
from app.domain.entities.message import Message
from app.domain.entities.phone_number import PhoneNumber
from app.domain.entities.sms import Sms
from app.domain.entities.sms_status import SmsDeliveryStatus


@pytest.mark.unit
def test_maps_senderless_sms_entity_to_persistence_model():
    sms = Sms(
        recipient=PhoneNumber(value="+254700000000"),
        message=Message(value="Hello without an explicit sender"),
    )

    model = map_sms_entity_to_model(sms)

    assert model.sender is None


@pytest.mark.unit
def test_maps_senderless_sms_model_to_domain_entity():
    model = SmsModel(
        identifier=Sms.next_id().value,
        sender=None,
        recipient="+254700000000",
        message="Hello without an explicit sender",
        status=SmsDeliveryStatus.PENDING,
    )

    sms = map_sms_model_to_entity(model)

    assert sms.sender is None
