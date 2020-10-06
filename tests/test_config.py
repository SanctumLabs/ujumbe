import unittest
from flask import current_app
from tests import BaseTestCase


class TestConfigurationsCases(BaseTestCase):
    """
    Test for configuration of the application. These Tests ensure that the testing configurations run
    as the should under TESTING config
    """

    def test_app_is_testing(self):
        """Test application can be configured for testing"""
        self.assertTrue(current_app.config["TESTING"])

    def test_app_is_debuggable(self):
        """Test application can be in debug mode"""
        self.assertTrue(current_app.config.get("DEBUG") is True)

    def test_app_has_wsrf_enabled(self):
        """Test application has WSRF disabled in testing mode"""
        self.assertTrue(current_app.config.get("WTF_CSRF_ENABLED") is False)

    def test_app_exists(self):
        """Test that the application exists"""
        self.assertFalse(current_app is None)

    def test_app_preserves_context(self):
        """Test the application preserves context on exception"""
        self.assertTrue(current_app.config.get("PRESERVE_CONTEXT_ON_EXCEPTION") is False)

    def test_app_has_set_sms_token_and_url_to_test_values(self):
        """Test the application has set the SMS_TOKEN and SMS_API_URL to test values"""
        token = current_app.config.get("SMS_TOKEN")
        base_url = current_app.config.get("SMS_API_URL")
        self.assertEqual(token, "sms-token")
        self.assertEqual(base_url, "https://api.sms.test.com")


if __name__ == '__main__':
    unittest.main()
