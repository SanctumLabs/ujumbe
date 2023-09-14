from prometheus_client import make_asgi_app
from app.settings import get_config
from app.infra.logger import log as logger

_settings = get_config()


def setup_prometheus_client():
    """Sets up a prometheus client"""
    logger.info("Setting up prometheus client")
    prometheus_app = make_asgi_app()
    return prometheus_app
