import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.infra.logger import log


class LoggerRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        log.info(f"Request: {request.url} took {process_time}")
        return response
