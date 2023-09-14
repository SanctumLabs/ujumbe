import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.loguru import LoguruIntegration
from app.settings import get_config
from app.infra.logger import log as logger

_settings = get_config()


def _traces_sampler(sampling_context):
    path = sampling_context.get("asgi_scope", {}).get("path")

    if not _is_sampling_enabled_for_path(path):
        return 0.0
    else:
        return _settings.sentry.sentry_traces_sample_rate


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


def initialize_sentry():
    """Initializes sentry SDK in the application based on the settings provided"""
    logger.debug(f"Sentry Enabled: {_settings.sentry.sentry_enabled}")

    if _settings.sentry.sentry_enabled:
        logger.debug(
            f"Sentry Sample Rate: {_settings.sentry.sentry_traces_sample_rate}"
        )
        sentry_sdk.init(
            dsn=_settings.sentry.sentry_dsn,
            traces_sampler=_traces_sampler,
            # set the instrumenter to use OpenTelemetry instead of Sentry
            instrumenter="otel",
            release=_settings.git_commit_sha,
            environment=_settings.environment,
            profiles_sample_rate=_settings.sentry.sentry_profile_rate,
            sample_rate=_settings.sentry.sentry_sample_rate,
            integrations=[
                StarletteIntegration(transaction_style="url"),
                FastApiIntegration(transaction_style="url"),
                LoguruIntegration(),
            ],
        )

        if _settings.git_branch:
            sentry_sdk.set_tag("git_branch", _settings.git_branch)
