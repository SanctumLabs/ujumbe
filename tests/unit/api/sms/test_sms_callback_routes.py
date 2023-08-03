import unittest
from unittest.mock import Mock
import pytest
from faker import Faker
from . import BaseTestSmsApi
from app.domain.sms.submit_sms_callback import SubmitSmsCallbackService

fake = Faker()


@pytest.mark.unit
class TestSmsCallbackApi(BaseTestSmsApi):
    """
    Test Sms API
    """

    def setUp(self):
        super().setUp()
        self.callback_url = f"{self.base_url}/callback"
        self.mock_submit_sms_callback_service = Mock(spec=SubmitSmsCallbackService)

    @pytest.mark.anyio
    def test_throws_405_with_invalid_get_request(self):
        """Test API throws 405 with invalid http get request"""
        with self.test_client as tc:
            response = tc.get(self.callback_url)
            self.assert_status(405, response.status_code)

    @pytest.mark.anyio
    def test_throws_405_with_invalid_patch_request(self):
        """Test API throws 405 with invalid http patch request"""
        with self.test_client as ac:
            response = ac.patch(self.callback_url)
            self.assert_status(status_code=405, actual=response.status_code)

    @pytest.mark.anyio
    def test_throws_405_with_invalid_put_request(self):
        """Test API throws 405 with invalid http put request"""
        with self.test_client as ac:
            response = ac.put(self.callback_url)

            self.assert_status(status_code=405, actual=response.status_code)

    @pytest.mark.anyio
    def test_throws_400_with_missing_json_body(self):
        """Test sms api throws 400 with missing JSON body"""
        with self.test_client as ac:
            response = ac.post(self.callback_url)
            self.assert_status(status_code=400, actual=response.status_code)

    @pytest.mark.anyio
    def test_throws_400_with_missing_account_sid_field_in_body(self):
        """Test API throws 400 with missing 'AccountSid' in JSON body"""
        with self.test_client as ac:
            response = ac.post(
                self.callback_url,
                json=dict(
                    From="+25472000000",
                    MessageSid=fake.uuid4(),
                    MessageStatus="sent",
                    SmsSid=fake.uuid4(),
                    SmsStatus="sent",
                )
            )

            response_json = response.json()
            data = response_json.get("data")

            self.assert_status(status_code=400, actual=response.status_code)
            self.assertIsNotNone(data.get("errors"))

    @pytest.mark.anyio
    def test_throws_400_with_missing_from_field_in_body(self):
        """Test API throws 400 with missing 'From' field in JSON body"""
        with self.test_client as ac:
            response = ac.post(
                self.callback_url,
                json=dict(
                    AccountSid=fake.uuid4(),
                    MessageSid=fake.uuid4(),
                    MessageStatus="sent",
                    SmsSid=fake.uuid4(),
                    SmsStatus="sent",
                )
            )

            response_json = response.json()
            data = response_json.get("data")

            self.assert_status(status_code=400, actual=response.status_code)
            self.assertIsNotNone(data.get("errors"))

    @pytest.mark.anyio
    def test_throws_400_with_missing_from_message_sid_in_body(self):
        """Test API throws 400 with missing 'MessageSid' field in JSON body"""
        with self.test_client as ac:
            response = ac.post(
                self.callback_url,
                json=dict(
                    AccountSid=fake.uuid4(),
                    From="+25472000000",
                    MessageStatus="sent",
                    SmsSid=fake.uuid4(),
                    SmsStatus="sent",
                )
            )

            response_json = response.json()
            data = response_json.get("data")

            self.assert_status(status_code=400, actual=response.status_code)
            self.assertIsNotNone(data.get("errors"))

    @pytest.mark.anyio
    def test_throws_400_with_missing_from_message_status_in_body(self):
        """Test API throws 400 with missing 'MessageStatus' field in JSON body"""
        with self.test_client as ac:
            response = ac.post(
                self.callback_url,
                json=dict(
                    AccountSid=fake.uuid4(),
                    From="+25472000000",
                    MessageSid=fake.uuid4(),
                    SmsSid=fake.uuid4(),
                    SmsStatus="sent",
                )
            )

            response_json = response.json()
            data = response_json.get("data")

            self.assert_status(status_code=400, actual=response.status_code)
            self.assertIsNotNone(data.get("errors"))

    @pytest.mark.anyio
    def test_throws_400_with_missing_from_sms_sid_in_body(self):
        """Test API throws 400 with missing 'SmsSid' field in JSON body"""
        with self.test_client as ac:
            response = ac.post(
                self.callback_url,
                json=dict(
                    AccountSid=fake.uuid4(),
                    From="+25472000000",
                    MessageSid=fake.uuid4(),
                    MessageStatus="sent",
                    SmsStatus="sent",
                )
            )

            response_json = response.json()
            data = response_json.get("data")

            self.assert_status(status_code=400, actual=response.status_code)
            self.assertIsNotNone(data.get("errors"))

    @pytest.mark.anyio
    def test_throws_400_with_missing_from_sms_status_in_body(self):
        """Test API throws 400 with missing 'SmsStatus' field in JSON body"""
        with self.test_client as ac:
            response = ac.post(
                self.callback_url,
                json=dict(
                    AccountSid=fake.uuid4(),
                    From="+25472000000",
                    MessageStatus="sent",
                    MessageSid=fake.uuid4(),
                    SmsSid=fake.uuid4(),
                )
            )

            response_json = response.json()
            data = response_json.get("data")

            self.assert_status(status_code=400, actual=response.status_code)
            self.assertIsNotNone(data.get("errors"))

    @pytest.mark.anyio
    def test_returns_200_with_valid_json_body(self):
        """Test API returns 200 with valid JSON body"""
        self.mock_submit_sms_callback_service.execute.return_value = None

        account_sid = fake.uuid4()
        from_ = "+254720000000"
        message_sid = fake.uuid4()
        message_status = "sent"
        sms_sid = fake.uuid4()
        sms_status = "sent"

        with self.app.container.domain.submit_sms_callback.override(self.mock_submit_sms_callback_service):
            with self.test_client as ac:
                response = ac.post(
                    url=self.callback_url,
                    json=dict(
                        AccountSid=account_sid,
                        From=from_,
                        MessageSid=message_sid,
                        MessageStatus=message_status,
                        SmsSid=sms_sid,
                        SmsStatus=sms_status
                    )
                )

            response_json = response.json()
            message = response_json.get("message")

            self.assert_status(actual=response.status_code, status_code=200)
            self.assertEqual("Sms status received successfully", message)

            self.mock_submit_sms_callback_service.execute.assert_called_once()

    @pytest.mark.anyio
    def test_returns_500_with_valid_json_body_but_submit_callback_service_fails(self):
        """Test API returns 500 with valid JSON body but failure from submit sms callback service"""
        error_message = "Failed to handle sms callback"
        self.mock_submit_sms_callback_service.execute.side_effect = Exception(error_message)

        account_sid = fake.uuid4()
        from_ = "+254720000000"
        message_sid = fake.uuid4()
        message_status = "sent"
        sms_sid = fake.uuid4()
        sms_status = "sent"

        with self.app.container.domain.submit_sms_callback.override(self.mock_submit_sms_callback_service):
            with self.test_client as ac:
                response = ac.post(
                    url=self.callback_url,
                    json=dict(
                        AccountSid=account_sid,
                        From=from_,
                        MessageSid=message_sid,
                        MessageStatus=message_status,
                        SmsSid=sms_sid,
                        SmsStatus=sms_status
                    )
                )

            response_json = response.json()
            message = response_json.get("message")

            self.assertEqual(error_message, message)


if __name__ == '__main__':
    unittest.main()
