#!/usr/bin/env python3

import os
from flask_script import Manager, Shell, Server
from app import create_app
from app.logger import log as app_logger
from werkzeug.middleware.proxy_fix import ProxyFix

# create the application with given configuration from environment
app = create_app(os.getenv("FLASK_ENV") or "default")

# We may run into some issues with Flask not properly handling the proxied requests.
# It has to do with those headers we set in the Nginx configuration.
# We can use the Werkzeug ProxyFix to ... fix the proxy.
app.wsgi_app = ProxyFix(app.wsgi_app)

port = os.getenv("PORT") or 5000

manager = Manager(app)
server = Server(host="0.0.0.0", port=port)


def make_shell_context():
    """
    Makes a shell context
    :return dictionary object
    :rtype: dict
    """
    return dict(app=app)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("runserver", server)


@manager.command
def profile(length=25, profile_dir=None):
    """
    This module provides a simple WSGI profiler middleware for finding
    bottlenecks in web application. It uses the profile or cProfile
    module to do the profiling and writes the stats to the stream provided
    see: http://werkzeug.pocoo.org/docs/0.9/contrib/profiler/
    """
    from werkzeug.middleware.profiler import ProfilerMiddleware

    app.config["PROFILE"] = True
    app.wsgi_app = ProfilerMiddleware(
        app.wsgi_app, restrictions=[length], profile_dir=profile_dir
    )
    app.run()


@manager.command
def list_routes():
    """
    Lists routes available in the application
    Run with python manage.py list_routes
    """
    from flask import url_for
    import urllib

    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ",".join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.parse.unquote(
            "{:50s} {:20s} {}".format(rule.endpoint, methods, url)
        )
        output.append(line)

    for line in sorted(output):
        app_logger.info(line)

if __name__ == "__main__":
    config = os.getenv("FLASK_ENV") or "default"
    app_logger.info(f"Running application in {config} environment on port {port}")
    manager.run()