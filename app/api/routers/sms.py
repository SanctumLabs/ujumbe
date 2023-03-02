from fastapi import APIRouter
from starlette import status
from app.infra.logger import log as logger
from .dto import SmsRequestDto
from ..dto import BadRequest, ApiResponse
from app.core.domain.exceptions import AppException
from app.modules.sms.domain.send_sms import send_sms as send_sms_service
from app.modules.sms.entities.sms_request import SmsRequest


router = APIRouter(prefix="/v1/sms", tags=["SMS"])


@logger.catch
@router.post(
    path="/",
    summary="Sends SMS",
    description="Sends an SMS request",
    response_model=ApiResponse
)
async def send_sms(payload: SmsRequestDto):
    """
    Send sms API function. This is a POST REST endpoint that accepts requests that meet the criteria defined by the
    schema validation before sending a plain text sms
    :return: JSON response to client
    """
    if not payload:
        return BadRequest(message="No data provided")

    try:
        data = dict(phone_number=payload.phone_number, message=payload.message)

        sms_request = SmsRequest(**data)

        send_sms_service(sms_request)

        return ApiResponse(
            status=status.HTTP_200_OK, message="Sms sent out successfully"
        )
    except AppException as e:
        logger.error(f"Failed to send sms to {payload} with error {e}")
        return ApiResponse(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Failed to send email"
        )
