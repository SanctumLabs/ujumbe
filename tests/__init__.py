import unittest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from app import app
from app.settings import AppSettings, get_settings, SentrySettings

base_url = "http://ujumbe-test-server"


class BaseTestCase(unittest.TestCase):
    """
    Base test case for application
    """

    def setUp(self):
        app.dependency_overrides[get_settings] = self._get_settings_override()
        self.app = app
        self.test_client = TestClient(app=app, base_url=base_url)
        self.async_client = AsyncClient(app=app, base_url=base_url)

    def tearDown(self):
        pass

    @staticmethod
    def _get_settings_override():
        sentry = SentrySettings(sentry_debug_enabled = False, sentry_enabled = False, sentry_dsn = "")
        return AppSettings(environment="test", sentry=sentry)

    def assert_status(self, status_code: int, actual: int):
        self.assertEqual(status_code, actual)
