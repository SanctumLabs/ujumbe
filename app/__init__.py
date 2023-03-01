from fastapi import FastAPI
from .config import config
from .logger import log as app_logger
from kombu import Queue
from app.api.routers.sms import router as sms_router
from app.infra.middleware.header_middleware import HeaderMiddleware
from app.infra.middleware.logger_middleware import LoggerRequestMiddleware
from .constants import SMS_DEFAULT_EXCHANGE, SMS_DEFAULT_QUEUE_NAME, SMS_DEFAULT_ROUTING_KEY, SMS_EXCHANGE, \
    SMS_QUEUE_NAME, SMS_ROUTING_KEY


app = FastAPI(title="Ujumbe")

app.add_middleware(HeaderMiddleware)
app.add_middleware(LoggerRequestMiddleware)

app.include_router(prefix="/api", router=sms_router)

def create_app(config_name):
    """
    Creates a new flask app instance with the given configuration
    :param config_name: configuration to use when creating the application
    :return: a new WSGI Flask app
    :rtype: Flask
    """

    error_handlers(app)
    register_app_blueprints(app)

    # Task Queues
    task_queues = (
        Queue(name=SMS_DEFAULT_QUEUE_NAME, routing_key=SMS_DEFAULT_ROUTING_KEY, exchange=SMS_DEFAULT_EXCHANGE),
        Queue(name=SMS_QUEUE_NAME, routing_key=SMS_ROUTING_KEY, exchange=SMS_EXCHANGE)
    )

    # Task Routes
    task_routes = {
        "sms_sending_task": dict(
            queue=SMS_QUEUE_NAME
        )
    }

    # Set task routes and queues
    app.config.update(dict(
        task_default_queue=SMS_DEFAULT_QUEUE_NAME,
        task_default_exchange=SMS_DEFAULT_EXCHANGE,
        task_default_routing_key=SMS_DEFAULT_ROUTING_KEY,
        task_queues=task_queues,
        task_routes=task_routes
    ))
    

    # this will reduce the load time for templates and increase the application performance
    app.jinja_env.cache = {}

    @app.route("/health")
    def health():
        return jsonify({"message": "I am healthy :D"}), 200

    return app


def error_handlers(app):
    """
    Error handlers function that will initialize error handling templates for the entire application
    :param app: the flask app
    """

    @app.errorhandler(404)
    def not_found(error):
        """
        This will handle errors that involve 404 messages
        :return: a template instructing user they have sent a request that does not exist on
         the server
        """
        app_logger.error(f"An error occurred during a request. Error => {error}")
        return jsonify(dict(message="Failed to find resource")), 404

    @app.errorhandler(500)
    def server_error(e):
        # Log the error and stacktrace.
        app_logger.error(f"An error occurred during a request. Error => {e}")
        return jsonify(dict(message=f"Request failed with error {e}")), 500

    @app.errorhandler(403)
    def error_403(error):
        app_logger.error(f"An error occurred during a request. Error => {error}")
        return jsonify(dict(message=f"Request failed with error {error}")), 403

    @app.errorhandler(400)
    def bad_request(error):
        app_logger.error(f"An error occurred during a request. Error => {error}")
        return jsonify(dict(message=f"Request failed with error {error}")), 400


def register_app_blueprints(app_):
    """
    Registers the application blueprints
    :param app_: the current flask app
    """
    from app.api import sms

    app_.register_blueprint(sms)
