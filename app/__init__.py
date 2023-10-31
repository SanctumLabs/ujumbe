"""
Application Entry point
"""
import logging
import uvicorn.logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from app.api.sms.routes import router as sms_router
from app.api.monitoring.routes import router as monitoring_router
from app.config.di.container import ApplicationContainer
from app.infra.middleware.header_middleware import HeaderMiddleware
from app.infra.middleware.logger_middleware import LoggerRequestMiddleware
from app.infra.handlers.exception_handlers import attach_exception_handlers
from app.infra.telemetry.sentry import initialize_sentry
from app.infra.telemetry.otel.metrics import initialize_metrics
from app.infra.telemetry.otel.traces import initialize_traces
from app.infra.telemetry.prometheus import setup_prometheus_client
import app.api.sms.routes
from .settings import get_settings

logging.root.setLevel(logging.INFO)
console_formatter = uvicorn.logging.ColourizedFormatter(
    "{levelprefix:<8} {name}: {message}", style="{", use_colors=True
)
root = logging.getLogger()
for handler in root.handlers:
    handler.setFormatter(console_formatter)

_settings = get_settings()

# initialize sentry
initialize_sentry()

container = ApplicationContainer()
container.wire(modules=[app.api.sms.routes])

app = FastAPI(
    title=_settings.server_name,
    description=_settings.description,
    version="1.0.0",
    docs_url=None if _settings.docs_disabled else "/docs",
    redoc_url=None if _settings.docs_disabled else "/redoc",
)

app.container = container
app.include_router(prefix="/api", router=sms_router)
app.include_router(router=monitoring_router)

app.add_middleware(HeaderMiddleware)
app.add_middleware(LoggerRequestMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors.cors_allow_origins,
    allow_origin_regex=_settings.cors.cors_allow_origin_regex,
    allow_credentials=_settings.cors.cors_allow_credentials,
    allow_headers=list(_settings.cors.cors_allow_headers),
    allow_methods=list(_settings.cors.cors_allow_methods),
)

# Configure Traces
initialize_traces()

# Configure Metrics
initialize_metrics()

# instrument app
# https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html
FastAPIInstrumentor.instrument_app(app)

# Prometheus
prometheus_app = setup_prometheus_client()
app.mount("/metrics", prometheus_app)

attach_exception_handlers(app=app)
