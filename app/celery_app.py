from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

broker = os.environ.get("BROKER_URL", "amqp://")
result_backend = os.environ.get("RESULT_BACKEND", "rpc://")

celery_app = Celery("SmsGateway", broker=broker, backend=result_backend, include=["app.tasks"])
