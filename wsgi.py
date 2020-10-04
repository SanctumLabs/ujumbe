
from werkzeug.middleware.proxy_fix import ProxyFix
from app import create_app
import os

# create the application with given configuration from environment
app = create_app(os.getenv("FLASK_ENV") or "default")

# We may run into some issues with Flask not properly handling the proxied requests.
# It has to do with those headers we set in the Nginx configuration.
# We can use the Werkzeug ProxyFix to ... fix the proxy.
app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == "__main__":
    app.run()