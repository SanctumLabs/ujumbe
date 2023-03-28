from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.settings import config


class HeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        Is handled after each request and can be used to add headers to the response or handle further processing
        :param request: Request object that is received from client
        :param call_next: receives request as parameters and passes it to the next execution
        """
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["server"] = config.server_name
        return response
