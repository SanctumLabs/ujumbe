"""
Configurations for flask application. These are global variables that the app will use in its entire
lifetime
"""
import os
from abc import ABCMeta
from click import echo, style

basedir = os.path.abspath(os.path.dirname(__file__))
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

if os.path.exists(".env"):
    echo(style(text="Importing environment variables", fg="green", bold=True))
    for line in open(".env"):
        var = line.strip().split("=")
        if len(var) == 2:
            os.environ[var[0]] = var[1]


class Config(object):
    """
    Default configuration for application
    This is abstract and thus will not be used when configuring the application.
    the instance variables and class variables will be inherited by subclass
    configurations and either they will be used as is of there will be overrides
    :cvar CSRF_SESSION_KEY Use a secure, unique and absolutely secret key for signing
     the data.
     this example
    """

    __abstract__ = True
    __metaclass__ = ABCMeta
    SSL_DISABLE = False

    # configure flask secret key
    SECRET_KEY = os.environ.get("SECRET_KEY") or "sms-gateway"

    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT") or "sms-gateway"

    ROOT_DIR = APP_ROOT
    WTF_CSRF_ENABLED = True
    CSRF_ENABLED = True
    CSRF_SESSION_KEY = os.environ.get("CSRF_SESSION_KEY")

    SMS_TOKEN = os.environ.get("SMS_TOKEN", "")
    SMS_API_URL = os.environ.get("SMS_API_URL", "")
    RESULT_BACKEND = os.environ.get("RESULT_BACKEND", "rpc://")

    @staticmethod
    def init_app(app):
        """Initializes the current application"""
        pass


class DevelopmentConfig(Config):
    """Configuration for development environment"""

    FLASK_DEBUG = True
    DEBUG = True


class StagingConfig(Config):
    """Configuration for staging environment"""

    FLASK_DEBUG = False


class TestingConfig(Config):
    """
    Testing configurations
    """

    FLASK_DEBUG = True
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    DEFAULT_SENDER = "test@example.com"
    SMS_TOKEN = "sms-token"
    SMS_API_URL = "https://api.sms.test.com"


class ProductionConfig(Config):
    """
    Production configuration
    """
    FLASK_DEBUG = False
    FLASK_ENV = "production"

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


config = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig,
    staging=StagingConfig,
    default=DevelopmentConfig,
)
