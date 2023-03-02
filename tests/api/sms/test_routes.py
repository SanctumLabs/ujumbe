import unittest
from unittest.mock import patch
import pytest
from app.core.domain.exceptions import AppException
from tests import BaseTestCase
import os

base_url = "/api/v1/sms/"
os.environ.update(BROKER_URL="memory://", RESULT_BACKEND="rpc")


class TestSmsApi(BaseTestCase):
    """
    Test Sms API
    """

    @pytest.mark.anyio
    async def test_throws_405_with_invalid_get_request(self):
        """Test sms api throws 405 with invalid http get request"""
        async with self.async_client as ac:
            response = ac.get(base_url)

            self.assert405(response)

    @pytest.mark.anyio
    async def test_throws_405_with_invalid_patch_request(self):
        """Test sms api throws 405 with invalid http patch request"""
        async with self.async_client as ac:
            response = ac.patch(base_url)
            self.assert405(response)

    @pytest.mark.anyio
    async def test_throws_405_with_invalid_put_request(self):
        """Test sms api throws 405 with invalid http put request"""
        async with self.async_client as ac:
            response = ac.put(base_url)

            self.assert405(response)

    @pytest.mark.anyio
    async def test_throws_400_with_missing_json_body(self):
        """Test sms api throws 400 with missing JSON body"""
        async with self.async_client as ac:
            response = ac.post(base_url)

            response_data = response.json

            self.assert400(response)
            self.assertEqual("No data provided", response_data.get("message"))

    @pytest.mark.anyio
    async def test_throws_422_with_missing_required_fields_in_body(self):
        """Test sms api throws 422 with missing 'message' in JSON body"""
        async with self.async_client as ac:
            response = ac.post(
                base_url,
                json=dict(
                    message="Rocket Schematics!",
                )
            )

            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

    @pytest.mark.anyio
    async def test_throws_422_with_missing_message_required_field_in_body(self):
        """Test sms api throws 422 with missing message in JSON body"""
        async with self.async_client as ac:
            response = ac.post(
                base_url,
                json=dict(
                    to=["+254700000000"]
                )
            )

            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

    @pytest.mark.anyio
    async def test_throws_422_with_invalid_phone_number_in_body(self):
        """Test sms api throws 422 with missing 'subject' in JSON body"""
        async with self.async_client as ac:
            response = ac.post(
                base_url,
                json=dict(
                    to=["0777777777"],
                    message="Let's build this!!"
                )
            )

            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

    @pytest.mark.anyio
    async def test_throws_422_with_invalid_length_of_message_in_body(self):
        """Test sms api throws 422 with an invalid length of subject in JSON body"""
        async with self.async_client as ac:
            response = ac.post(
                base_url,
                json=dict(
                    to=["+254700000000"],
                    message=""
                )
            )

            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

    @pytest.mark.anyio
    async def test_throws_422_with_invalid_length_of_to_in_body(self):
        """Test sms api throws 422 with an invalid to length in JSON body"""
        async with self.async_client as ac:
            response = ac.post(
                base_url,
                json=dict(
                    to=[],
                    message="Let us build a rocket to the Moon"
                )
            )
            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

    @pytest.mark.anyio
    @patch("app.tasks.sms_sending_task.sms_sending_task.apply_async", return_value=dict(success=True))
    async def test_returns_200_with_valid_json_body(self, mock_sending_task):
        """Test sms api returns 200 with an valid JSON body calling send plain sms use case"""
        async with self.async_client as ac:
            response = ac.post(
                base_url,
                json=dict(
                    to=["+254700000000"],
                    message="Let us build a rocket to the Moon"
                )
            )

            response_json = response.json

            self.assert_status(response=response, status_code=200)
            self.assertEqual("Sms sent out successfully", response_json.get("message"))

    @pytest.mark.anyio
    @patch("app.tasks.sms_sending_task.sms_sending_task.apply_async", side_effect=AppException("Boom!"))
    async def test_returns_500_with_valid_json_body_but_task_fails(self, mock_sending_task):
        """Test sms api returns 500 with an valid JSON body calling send plain sms use case but exception is
        thrown """
        async with self.async_client as ac:
            response = ac.post(
                base_url,
                json=dict(
                    to=["+254700000000"],
                    message="Let us build a rocket to the Moon"
                )
            )

            response_json = response.json

            self.assert_status(response=response, status_code=500)
            self.assertEqual("Failed to send sms", response_json.get("message"))


if __name__ == '__main__':
    unittest.main()
