import unittest
from flask_testing import TestCase
from app import create_app


class ContextTestCase(TestCase):
    render_templates = False

    def create_app(self):
        app = create_app("testing")
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        return app

    def _pre_setup(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()

    def __call__(self, result=None):
        try:
            self._pre_setup()
            super(ContextTestCase, self).__call__(result)
        finally:
            self._post_teardown()

    def _post_teardown(self):
        if getattr(self, '_ctx', None) and self._ctx is not None:
            self._ctx.pop()
            del self._ctx


class BaseTestCase(ContextTestCase):
    """
    Base test case for application
    """

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()


if __name__ == "__main__":
    unittest.main()