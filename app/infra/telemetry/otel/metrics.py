from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry import metrics
from app.settings import get_config
from app.infra.logger import log as logger

_settings = get_config()


def initialize_metrics():
    """configures metrics in the application"""
    logger.info("Setting up metrics")
    reader = PrometheusMetricReader()
    resource = Resource(attributes={SERVICE_NAME: _settings.server_name})
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)
