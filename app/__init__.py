"""
Application Entry point
"""
import logging
import uvicorn.logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.opentelemetry import SentryPropagator, SentrySpanProcessor
from opentelemetry import metrics, trace
from opentelemetry.propagate import set_global_textmap
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import make_asgi_app
import app.api.sms.routes
from app.api.sms.routes import router as sms_router
from app.api.monitoring.routes import router as monitoring_router
from app.config.di.container import ApplicationContainer
from app.infra.middleware.header_middleware import HeaderMiddleware
from app.infra.middleware.logger_middleware import LoggerRequestMiddleware
from app.infra.handlers.exception_handlers import attach_exception_handlers
from .settings import get_config

logging.root.setLevel(logging.INFO)
console_formatter = uvicorn.logging.ColourizedFormatter(
    "{levelprefix:<8} {name}: {message}", style="{", use_colors=True
)
root = logging.getLogger()
for handler in root.handlers:
    handler.setFormatter(console_formatter)

_settings = get_config()

logging.info(f"Sentry Enabled: {_settings.sentry.sentry_enabled}")
if _settings.sentry.sentry_enabled:

    def _is_sampling_enabled_for_path(path: str) -> bool:
        # We want sampling to be enabled for non-web transactions
        if not path:
            return True

        # We want to disable sampling on the following paths
        excluded_paths = [
            "/",
            "/healthCheck",
            "/health",
            "/metrics",
            "/ping",
        ]

        if path in excluded_paths:
            return False

        return True

    def _traces_sampler(sampling_context):
        path = sampling_context.get("asgi_scope", {}).get("path")

        if not _is_sampling_enabled_for_path(path):
            return 0.0
        else:
            return _settings.sentry_sample_rate

    logging.info(f"Sentry Sample Rate: {_settings.sentry.sentry_traces_sample_rate}")
    sentry_sdk.init(
        dsn=_settings.sentry.sentry_dsn,
        traces_sampler=_traces_sampler,
        # set the instrumenter to use OpenTelemetry instead of Sentry
        instrumenter="otel",
        release=_settings.git_commit_sha,
        environment=_settings.environment,
        profiles_sample_rate=_settings.sentry.sentry_profile_rate,
    )

    if _settings.git_branch:
        sentry_sdk.set_tag("git_branch", _settings.git_branch)

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
    allow_origins=_settings.cors_allow_origins,
    allow_origin_regex=_settings.cors_allow_origin_regex,
    allow_credentials=_settings.cors_allow_credentials,
    allow_headers=list(_settings.cors_allow_headers),
    allow_methods=list(_settings.cors_allow_methods),
)

# Configure Traces
tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)
tracer_provider.add_span_processor(SentrySpanProcessor())
set_global_textmap(SentryPropagator())

# Configure Metrics
reader = PrometheusMetricReader()
resource = Resource(attributes={SERVICE_NAME: _settings.server_name})
meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(meter_provider)

# instrument app
# https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html
FastAPIInstrumentor.instrument_app(app)

# Prometheus
prometheus_app = make_asgi_app()
app.mount("/metrics", prometheus_app)

attach_exception_handlers(app=app)
