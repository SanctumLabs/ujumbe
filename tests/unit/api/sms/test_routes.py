import unittest
from unittest.mock import Mock
import pytest
from tests import BaseTestCase
from app.domain.sms.submit_sms import SubmitSmsService

base_url = "/api/v1/sms/"


@pytest.mark.unit
class TestSmsApi(BaseTestCase):
    """
    Test Sms API
    """

    def setUp(self):
        super().setUp()
        self.mock_submit_service = Mock(spec=SubmitSmsService)

    @pytest.mark.anyio
    def test_throws_405_with_invalid_get_request(self):
        """Test sms api throws 405 with invalid http get request"""
        with self.test_client as tc:
            response = tc.get(base_url)
            self.assert_status(405, response.status_code)

    @pytest.mark.anyio
    def test_throws_405_with_invalid_patch_request(self):
        """Test sms api throws 405 with invalid http patch request"""
        with self.test_client as ac:
            response = ac.patch(base_url)
            self.assert_status(status_code=405, actual=response.status_code)

    @pytest.mark.anyio
    def test_throws_405_with_invalid_put_request(self):
        """Test sms api throws 405 with invalid http put request"""
        with self.test_client as ac:
            response = ac.put(base_url)

            self.assert_status(status_code=405, actual=response.status_code)

    @pytest.mark.anyio
    def test_throws_400_with_missing_json_body(self):
        """Test sms api throws 400 with missing JSON body"""
        with self.test_client as ac:
            response = ac.post(base_url)
            self.assert_status(status_code=400, actual=response.status_code)

    @pytest.mark.anyio
    def test_throws_400_with_missing_recipient_field_in_body(self):
        """Test sms api throws 400 with missing 'recipient' in JSON body"""
        with self.test_client as ac:
            response = ac.post(
                base_url,
                json=dict(
                    message="Rocket Schematics!",
                )
            )

            response_json = response.json()
            data = response_json.get("data")

            self.assert_status(status_code=400, actual=response.status_code)
            self.assertIsNotNone(data.get("errors"))

    @pytest.mark.anyio
    def test_throws_400_with_missing_message_required_field_in_body(self):
        """Test sms api throws 400 with missing message in JSON body"""
        with self.test_client as ac:
            response = ac.post(
                base_url,
                json=dict(
                    recipient="+254700000000"
                )
            )

            response_json = response.json()
            data = response_json.get("data")

            self.assert_status(status_code=400, actual=response.status_code)
            self.assertIsNotNone(data.get("errors"))

    @pytest.mark.anyio
    def test_throws_400_with_invalid_length_of_message_in_body(self):
        """Test sms api throws 400 with an invalid length of message in JSON body"""
        with self.test_client as ac:
            response = ac.post(
                base_url,
                json=dict(
                    recipient="+254700000000",
                    message=""
                )
            )

            json = response.json()
            data = json.get("data")
            errors = data.get("errors")

            self.assert_status(actual=response.status_code, status_code=400)
            self.assertIsNotNone(errors)

    @pytest.mark.anyio
    def test_returns_200_with_valid_json_body(self):
        """Test sms api returns 200 with valid JSON body"""
        self.mock_submit_service.execute.return_value = None

        with self.app.container.domain.submit_sms.override(self.mock_submit_service):
            with self.test_client as ac:
                response = ac.post(
                    base_url,
                    json=dict(
                        recipient="+254700000000",
                        message="Let us build a rocket to the Moon"
                    )
                )

            response_json = response.json()
            message = response_json.get("message")

            self.assert_status(actual=response.status_code, status_code=200)
            self.assertEqual("Sms sent out successfully", message)

    @pytest.mark.anyio
    @unittest.skip("Failure to mock side effect on submit_service.execute. Need to investigate underlying Exception")
    def test_returns_500_with_valid_json_body_but_submit_service_fails(self):
        """Test sms api returns 500 with valid JSON body but failure from submit sms service"""
        self.mock_submit_service.execute.side_effect = Exception("Failed to send out sms")

        with self.app.container.domain.submit_sms.override(self.mock_submit_service):
            with self.test_client as ac:
                response = ac.post(
                    base_url,
                    json=dict(
                        recipient="+254700000000",
                        message="Let us build a rocket to the Moon"
                    )
                )

            response_json = response.json()
            message = response_json.get("message")

            self.assert_status(actual=response.status_code, status_code=500)
            self.assertEqual("Failed to send SMS", message)


if __name__ == '__main__':
    unittest.main()
