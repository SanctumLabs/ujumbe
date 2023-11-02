from fastapi import APIRouter
from starlette import status
from dependency_injector.wiring import inject
from opentelemetry import trace
from app.infra.logger import log as logger
from app.core.domain.exceptions import AppException
from app.domain.services.sms.submit_sms import SubmitSmsService
from app.domain.services.sms.submit_sms_callback import SubmitSmsCallbackService
from app.config.di.dependency import dependency
from app.domain.entities.sms import Sms
from app.domain.entities.sms_callback import SmsCallback
from app.config.di.container import ApplicationContainer
from .dto import SmsRequestDto, SmsCallbackRequestDto
from ..dto import BadRequest, ApiResponse

router = APIRouter(prefix="/v1/sms", tags=["SMS"])
tracer_name = "sms"
tracer = trace.get_tracer(tracer_name)


@router.post(
    path="/",
    summary="Sends SMS API that handles sending SMS messages to recipients",
    description="Sends an SMS request",
    response_model=ApiResponse,
)
@inject
async def send_sms_api(
    payload: SmsRequestDto,
    submit_sms: SubmitSmsService = dependency(ApplicationContainer.domain.submit_sms),
):
    """Send SMS API. This is a POST REST endpoint that accepts requests that meet the criteria defined by the schema
    validation before sending a plain text sms

    Args:
        payload(SmsRequestDto): SMS Request payload
        submit_sms(SubmitSmsService): Handles sms request payload and submits it for processing
    Returns:
        ApiResponse: returns a JSON response to a client.
    """
    with tracer.start_span(f"{tracer_name}.send"):
        if not payload:
            return BadRequest(message="No data provided")

        try:
            data = dict(
                sender=payload.sender,
                recipient=payload.recipient,
                message=payload.message,
            )

            sms = Sms.from_dict(data)

            with tracer.start_span(f"{tracer_name}.submit_sms"):
                await submit_sms.execute(sms)

            return ApiResponse(
                status=status.HTTP_200_OK, message="Sms sent out successfully"
            )
        except Exception as e:
            logger.error(f"Failed to send sms to {payload} with error {e}")
            if e is AppException:
                return ApiResponse(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="Failed to send SMS",
                )
            else:
                return ApiResponse(status=status.HTTP_400_BAD_REQUEST, message=f"{e}")


@router.post(
    path="/callback",
    summary="SMS Callback to track delivery of sent SMS. 3rd part clients communicate the deliver of an SMS with this "
    "webhook",
    description="Receives callback from 3rd Party services to track the delivery status of messages",
    response_model=ApiResponse,
)
@inject
async def sms_callback_api(
    payload: SmsCallbackRequestDto,
    submit_sms_callback: SubmitSmsCallbackService = dependency(
        ApplicationContainer.domain.submit_sms_callback
    ),
):
    """SMS callback API. This is a POST REST endpoint that accepts sms callback requests that is used to track the
    status of an initially delivered SMS message.
    Args:
        payload(SmsCallbackRequestDto): Callback Request DTO as provided by a client
        submit_sms_callback(SubmitSmsCallbackService): service that handles processing of SMS Callback requests
    Returns:
        ApiResponse: JSON response to a client
    """
    with tracer.start_span(f"{tracer_name}.callback"):
        if not payload:
            return BadRequest(message="No data provided")

        try:
            callback = SmsCallback.from_dict(payload.dict())

            await submit_sms_callback.execute(callback)

            return ApiResponse(
                status=status.HTTP_202_ACCEPTED,
                message="Sms status received successfully",
            )
        except Exception as e:
            logger.error(f"Failed to handle sms callback {payload} with error {e}")
            if e is AppException:
                return ApiResponse(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="Failed to handle SMS Callback",
                )
            else:
                return ApiResponse(status=status.HTTP_400_BAD_REQUEST, message=f"{e}")
