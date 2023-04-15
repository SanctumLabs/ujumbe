from fastapi import FastAPI
import app.api.sms.routes
from app.api.sms.routes import router as sms_router
from app.api.monitoring.routes import router as monitoring_router
from app.config.di.container import ApplicationContainer
from app.infra.middleware.header_middleware import HeaderMiddleware
from app.infra.middleware.logger_middleware import LoggerRequestMiddleware
from app.infra.handlers.exception_handlers import attach_exception_handlers
from .settings import config

container = ApplicationContainer()
container.wire(modules=[app.api.sms.routes])

app = FastAPI(
    title=config.server_name,
    description=config.description,
    version="1.0.0",
    docs_url=None if config.docs_disabled else "/docs",
    redoc_url=None if config.docs_disabled else "/redoc",
)

app.container = container
app.add_middleware(HeaderMiddleware)
app.add_middleware(LoggerRequestMiddleware)
attach_exception_handlers(app=app)

app.include_router(prefix="/api", router=sms_router)
app.include_router(router=monitoring_router)
