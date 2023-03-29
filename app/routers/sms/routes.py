from fastapi import APIRouter
from starlette import status
from app.infra.logger import log as logger
from .dto import SmsRequestDto
from ..dto import BadRequest, ApiResponse
from app.core.domain.exceptions import AppException
from app.domain.sms.submit_sms import SubmitSmsService
from app.config.di.dependency import dependency
from app.domain.entities.sms import Sms
from app.config.di.container import ApplicationContainer
from dependency_injector.wiring import inject

router = APIRouter(prefix="/v1/sms", tags=["SMS"])


@logger.catch
@router.post(
    path="/",
    summary="Sends SMS",
    description="Sends an SMS request",
    response_model=ApiResponse,
)
@inject
async def send_sms(payload: SmsRequestDto, submit_sms: SubmitSmsService = dependency(ApplicationContainer.domain.submit_sms)):
    """
    Send sms API function. This is a POST REST endpoint that accepts requests that meet the criteria defined by the
    schema validation before sending a plain text sms
    :return: JSON response to client
    """
    if not payload:
        return BadRequest(message="No data provided")

    try:
        data = dict(sender=payload.sender, recipient=payload.recipient, message=payload.message)

        sms = Sms.from_dict(data)

        submit_sms.execute(sms)

        return ApiResponse(
            status=status.HTTP_200_OK, message="Sms sent out successfully"
        )
    except AppException as e:
        logger.error(f"Failed to send sms to {payload} with error {e}")
        return ApiResponse(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Failed to send email"
        )
