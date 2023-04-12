import unittest
import pytest
from tests import BaseTestCase


@pytest.mark.unit
class MonitoringRoutesTestCases(BaseTestCase):

    @pytest.mark.anyio
    async def test_monitoring_route(self):
        async with self.async_client as ac:
            response = await ac.get("/healthz")
        self.assert_status(200, response.status_code)
        self.assertEqual({"message": "Healthy!"}, response.json())


if __name__ == "__main__":
    unittest.main()
