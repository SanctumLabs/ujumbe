import unittest
from unittest.mock import patch
from tests import BaseTestCase
from app.exceptions import SmsGatewayError
import os

base_url = "/api/v1/sms/"

os.environ.update(BROKER_URL="memory://", RESULT_BACKEND="rpc")

class TestSmsApi(BaseTestCase):
    """
    Test Sms API
    """

    def test_throws_405_with_invalid_get_request(self):
        """Test sms api throws 405 with invalid http get request"""
        with self.client:
            response = self.client.get(base_url)

            self.assert405(response)

    def test_throws_405_with_invalid_patch_request(self):
        """Test sms api throws 405 with invalid http patch request"""
        with self.client:
            response = self.client.patch(base_url)
            self.assert405(response)

    def test_throws_405_with_invalid_put_request(self):
        """Test sms api throws 405 with invalid http put request"""
        with self.client:
            response = self.client.put(base_url)

            self.assert405(response)

    def test_throws_400_with_missing_json_body(self):
        """Test sms api throws 400 with missing JSON body"""
        with self.client:
            response = self.client.post(base_url)

            response_data = response.json

            self.assert400(response)
            self.assertEqual("No data provided", response_data.get("message"))

    def test_throws_422_with_missing_required_fields_in_body(self):
        """Test sms api throws 422 with missing 'message' in JSON body"""
        with self.client:
            response = self.client.post(
                base_url,
                json=dict(
                    to=["johndoe@example.com"],
                    subject="Rocket Schematics!",
                )
            )

            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

    def test_throws_422_with_missing_to_required_field_in_body(self):
        """Test sms api throws 422 with missing to in JSON body"""
        with self.client:
            response = self.client.post(
                base_url,
                json=dict(
                    message="Let us do this!",
                    subject="Rocket Schematics!",
                )
            )

            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

    def test_throws_422_with_missing_subject_in_body(self):
        """Test sms api throws 422 with missing 'subject' in JSON body"""
        with self.client:
            response = self.client.post(
                base_url,
                json=dict(
                    to=["johndoe@example.com"],
                    message="Let's build this!!"
                )
            )

            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

    def test_throws_422_with_invalid_sms_in_to_in_body(self):
        """Test sms api throws 422 with an invalid sms in 'to' in JSON body"""
        with self.client:
            response = self.client.post(
                base_url,
                json=dict(
                    to=["johndoe@gmail"],
                    subject="Rocket Schematics!",
                    message="Let's build this!!"
                )
            )

            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

    def test_throws_422_with_invalid_length_of_subject_in_body(self):
        """Test sms api throws 422 with an invalid length of subject in JSON body"""
        with self.client:
            response = self.client.post(
                base_url,
                json=dict(
                    to=["johndoe@gmail"],
                    subject="",
                    message="Let's build this!!"
                )
            )

            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

    def test_throws_422_with_invalid_length_of_message_in_body(self):
        """Test sms api throws 422 with an invalid length of message in JSON body"""
        with self.client:
            response = self.client.post(
                base_url,
                json=dict(
                    to=["johndoe@example.com"],
                    subject="Rocket Schematics",
                    message=""
                )
            )
            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

    def test_throws_422_with_invalid_length_from_in_body_if_provided(self):
        """Test sms api throws 422 with an invalid from in JSON body if it is provided"""
        with self.client:
            response = self.client.post(
                base_url,
                json={
                    "from_": {
                        "sms": "ninja",
                    },
                    "to": ["johndoe@example.com"],
                    "cc": ["janedoe@example.com"],
                    "subject": "Rocket Schematics",
                    "message": "Let us build a rocket to the Moon"
                }
            )
            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

    def test_throws_422_with_invalid_length_of_cc_in_body(self):
        """Test sms api throws 422 with an invalid cc length in JSON body and invalid sms in cc"""
        with self.client:
            response = self.client.post(
                base_url,
                json=dict(
                    to=["johndoe@example.com"],
                    cc=[],
                    subject="Rocket Schematics",
                    message="Let us build a rocket to the Moon"
                )
            )
            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

            response = self.client.post(
                base_url,
                json=dict(
                    to=["johndoe@example.com"],
                    cc=["janedoe@gmail"],
                    subject="Rocket Schematics",
                    message="Let us build a rocket to the Moon"
                )
            )
            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

    def test_throws_422_with_invalid_length_of_bcc_in_body(self):
        """Test sms api throws 422 with an invalid bcc length in JSON body and invalid sms in bcc"""
        with self.client:
            response = self.client.post(
                base_url,
                json=dict(
                    to=["johndoe@example.com"],
                    cc=["janedoe@example.com"],
                    bcc=[],
                    subject="Rocket Schematics",
                    message="Let us build a rocket to the Moon"
                )
            )
            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

            response = self.client.post(
                base_url,
                json=dict(
                    to=["johndoe@example.com"],
                    cc=["janedoe@example.com"],
                    bcc=["hiddenhooman@gmail"],
                    subject="Rocket Schematics",
                    message="Let us build a rocket to the Moon"
                )
            )
            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

    def test_throws_422_with_invalid_length_of_to_in_body(self):
        """Test sms api throws 422 with an invalid to length in JSON body"""
        with self.client:
            response = self.client.post(
                base_url,
                json=dict(
                    to=[],
                    cc=["janedoe@example.com"],
                    bcc=["hiddenhooman@example.com"],
                    subject="Rocket Schematics",
                    message="Let us build a rocket to the Moon"
                )
            )
            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

    def test_throws_422_with_invalid_length_of_attachments_in_body(self):
        """Test sms api throws 422 with an invalid attachments length in JSON body and missing fields in
        attachments """
        with self.client:
            response = self.client.post(
                base_url,
                json=dict(
                    to=["johndoe@example.com"],
                    cc=["janedoe@example.com"],
                    bcc=["hiddenhooman@example.com"],
                    subject="Rocket Schematics",
                    message="Let us build a rocket to the Moon",
                    attachments=[]
                )
            )

            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

            response = self.client.post(
                base_url,
                json=dict(
                    to=["johndoe@example.com"],
                    cc=["janedoe@example.com"],
                    bcc=["hiddenhooman@example.com"],
                    subject="Rocket Schematics",
                    message="Let us build a rocket to the Moon",
                    attachments=[
                        dict(
                            content="random_string"
                        )
                    ]
                )
            )

            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

            response = self.client.post(
                base_url,
                json=dict(
                    to=["johndoe@example.com"],
                    cc=["janedoe@example.com"],
                    bcc=["hiddenhooman@example.com"],
                    subject="Rocket Schematics",
                    message="Let us build a rocket to the Moon",
                    attachments=[
                        dict(
                            filename="rocket_schematics.pdf"
                        )
                    ]
                )
            )

            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

            response = self.client.post(
                base_url,
                json=dict(
                    to=["johndoe@example.com"],
                    cc=["janedoe@example.com"],
                    bcc=["hiddenhooman@example.com"],
                    subject="Rocket Schematics",
                    message="Let us build a rocket to the Moon",
                    attachments=[
                        dict(
                            content="random_string",
                            filename="rocket_schematics.pdf"
                        ),
                        dict(
                            filename="rocket_parts.pdf"
                        )
                    ]
                )
            )

            response_json = response.json

            self.assert_status(response, status_code=422)
            self.assertIsNotNone(response_json.get("errors"))

    @patch("app.tasks.mail_sending_task.mail_sending_task.apply_async", return_value=dict(success=True))
    def test_returns_200_with_valid_json_body(self, mock_sending_task):
        """Test sms api returns 200 with an valid JSON body calling send plain sms use case"""
        with self.client:
            response = self.client.post(
                base_url,
                json={
                    "from_": {
                        "sms": "ninja@example.com"
                    },
                    "to": ["johndoe@example.com"],
                    "cc": ["janedoe@example.com"],
                    "bcc": ["hiddenhooman@example.com"],
                    "subject": "Rocket Schematics",
                    "message": "Let us build a rocket to the Moon",
                    "attachments": [
                        dict(
                            content="random_string",
                            filename="rocket_schematics.pdf"
                        ),
                    ]
                }
            )

            response_json = response.json

            self.assert_status(response=response, status_code=200)
            self.assertEqual("Sms sent out successfully", response_json.get("message"))

    @patch("app.tasks.mail_sending_task.mail_sending_task.apply_async", side_effect=SmsGatewayError("Boom!"))
    def test_returns_500_with_valid_json_body_but_task_fails(self, mock_sending_task):
        """Test sms api returns 500 with an valid JSON body calling send plain sms use case but exception is
        thrown """
        with self.client:
            response = self.client.post(
                base_url,
                json={
                    "from_": {
                        "sms": "ninja@example.com",
                        "name": "Ninja"
                    },
                    "to": ["johndoe@example.com"],
                    "cc": ["janedoe@example.com"],
                    "bcc": ["hiddenhooman@example.com"],
                    "subject": "Rocket Schematics",
                    "message": "Let us build a rocket to the Moon",
                    "attachments": [
                        dict(
                            content="random_string",
                            filename="rocket_schematics.pdf"
                        ),
                    ]
                }
            )

            response_json = response.json

            self.assert_status(response=response, status_code=500)
            self.assertEqual("Failed to send sms", response_json.get("message"))


if __name__ == '__main__':
    unittest.main()
