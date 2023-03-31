import unittest
import os
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest
from app import app
from app.settings import AppSettings, get_config


class BaseTestCase(unittest.TestCase):
    """
    Base test case for application
    """

    os.environ.update(SENTRY_ENABLED="False", RESULT_BACKEND="rpc")

    def setUp(self):
        self.test_client = TestClient(app=app)
        app.dependency_overrides[get_config] = self._get_settings_override()

    @pytest.fixture(scope="class")
    async def client(self):
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client

    def tearDown(self):
        pass

    @staticmethod
    def _get_settings_override():
        return AppSettings(environment="test", sentry_debug_enabled=False, sentry_enabled=False, sentry_dsn="")

    def assert_status(self, status_code: int, actual: int):
        self.assertEqual(status_code, actual)
