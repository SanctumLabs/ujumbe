from . import sms_api
from flask import jsonify, request
from app.logger import log as logger
from .schemas import SmsMessageSchema
from app.exceptions import SmsGatewayError
from app.tasks.sms_sending_task import sms_sending_task
from marshmallow.exceptions import ValidationError

sms_message_schema = SmsMessageSchema()


@logger.catch
@sms_api.route("/", methods=["POST"])
def send_sms():
    """
    Send sms API function. This is a POST REST endpoint that accepts requests that meet the criteria defined by the
    schema validation before sending a plain text sms
    :return: JSON response to client
    :rtype: dict
    """
    payload = request.get_json()

    if not payload:
        return jsonify(dict(message="No data provided")), 400

    try:
        # validate JSON body
        data = sms_message_schema.load(payload)

        try:
            sms_sending_task.apply_async(
                kwargs=dict(
                    to=data.get("to"),
                    message=data.get("message"),
                ))            

            return jsonify(dict(
                message="Sms sent out successfully"
            )), 200
        except SmsGatewayError as e:
            logger.error(f"Failed to send sms to {payload.get('to')} with error {e}")
            return jsonify(dict(
                success=False,
                message="Failed to send sms"
            )), 500
    except ValidationError as ve:
        logger.error(f"Failed to load schema with error {ve}")
        return jsonify(dict(errors=[ve.messages])), 422
