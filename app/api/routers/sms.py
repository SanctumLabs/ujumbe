from fastapi import APIRouter
from .. import sms
from flask import jsonify, request
from app.logger import log as logger
from ..schemas import SmsMessageSchema
from .dto import SmsRequestDto
from ..dto import BadRequest
from app.exceptions import SmsGatewayError
from app.tasks.sms_sending_task import sms_sending_task
from marshmallow.exceptions import ValidationError

router = APIRouter(prefix = "/v1/sms/", tags = ["SMS"])

@logger.catch
@router.post(path="/", summary="Sends SMS", description="Sends an SMS request")
async def send_sms(payload: SmsRequestDto):
    """
    Send sms API function. This is a POST REST endpoint that accepts requests that meet the criteria defined by the
    schema validation before sending a plain text sms
    :return: JSON response to client
    :rtype: dict
    """
    if not payload:
        return BadRequest(message="No data provided")

    try:
        # validate JSON body
        data = sms_message_schema.load(payload)

        sms_sending_task.apply_async(
            kwargs=dict(
                to=data.get("to"),
                message=data.get("message"),
            ))            

        return jsonify(dict(
            message="Sms sent out successfully"
        )), 200
    except ValidationError as ve:
        logger.error(f"Failed to send sms to {payload.get('to')} with error {e}")
        logger.error(f"Failed to load schema with error {ve}")
        return jsonify(dict(errors=[ve.messages])), 422
