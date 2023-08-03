from tests import BaseTestCase


class BaseTestSmsApi(BaseTestCase):
    """
    Base class for testing Sms API
    """

    def setUp(self):
        super().setUp()
        self.base_url = "/api/v1/sms"

    def tearDown(self):
        pass
