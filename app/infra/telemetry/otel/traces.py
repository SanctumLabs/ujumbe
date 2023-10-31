from opentelemetry import trace
from opentelemetry.propagate import set_global_textmap
from opentelemetry.sdk.trace import TracerProvider
from sentry_sdk.integrations.opentelemetry import SentryPropagator, SentrySpanProcessor
from app.settings import get_settings
from app.infra.logger import log as logger

_settings = get_settings()


def initialize_traces():
    """Initializes traces in the application"""
    logger.info("Setting up traces")
    tracer_provider = TracerProvider()
    trace.set_tracer_provider(tracer_provider)
    tracer_provider.add_span_processor(SentrySpanProcessor())
    set_global_textmap(SentryPropagator())
