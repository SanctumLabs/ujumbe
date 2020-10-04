from __future__ import absolute_import, unicode_literals
import os
from app import celery_app, create_app

app = create_app(os.getenv('FLASK_ENV') or 'default')
app.app_context().push()
