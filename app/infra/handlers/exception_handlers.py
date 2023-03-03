"""
Application exception handlers
"""
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from app.routers.dto import ApiError


def _rewrite_error(err):
    field = err["loc"][-1]
    message = err["msg"].capitalize()
    typ = err["type"]

    if typ == "value_error.missing":
        message = "This field is required"

    return field, message


def attach_exception_handlers(app: FastAPI):
    """
    Attaches exception handlers to application
    """

    @app.exception_handler(ApiError)
    # pylint: disable=unused-argument
    async def api_exception_handler(request: Request, error: ApiError):
        return JSONResponse(
            status_code=error.status,
            content={
                "status": error.status,
                "message": error.message,
                "data": getattr(error, "data", {}),
            },
        )

    @app.exception_handler(HTTPException)
    # pylint: disable=unused-argument
    async def http_exception_handler(request: Request, error: HTTPException):
        try:
            message = error.detail
        # pylint: disable=broad-except
        except Exception as err:
            message = err or "Internal server error"

        return JSONResponse(
            status_code=error.status_code,
            content={"status": error.status_code, "message": message},
        )

    @app.exception_handler(Exception)
    # pylint: disable=unused-argument
    async def exception_handler(request: Request, error: Exception):
        return JSONResponse(
            status_code=500, content={"status": 500, "message": "Internal server error"}
        )

    @app.exception_handler(RequestValidationError)
    # pylint: disable=unused-argument
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        error_list = [_rewrite_error(e) for e in exc.errors()]
        errors = {}
        for error in error_list:
            errors.setdefault(error[0], []).append(error[1])

        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "message": "Something went wrong, please check the error messages below",
                "data": {"errors": errors},
            },
        )
