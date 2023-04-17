"""
Celery Application
"""
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

SMS_DEFAULT_QUEUE_NAME = "sms-default-queue"
SMS_DEFAULT_ROUTING_KEY = "sms-default-route-key"
SMS_DEFAULT_EXCHANGE = "sms-default-exchange"

SMS_QUEUE_NAME = "sms-queue"
SMS_ROUTING_KEY = "sms-route-key"
SMS_EXCHANGE = "sms-exchange"

SMS_ERROR_QUEUE_NAME = "sms-error-queue"
SMS_ERROR_ROUTING_KEY = "sms-error-route-key"
SMS_ERROR_EXCHANGE = "sms-error-exchange"

broker = os.environ.get("BROKER_URL", "amqp://")
result_backend = os.environ.get("RESULT_BACKEND", "rpc://")

celery_app = Celery(
    "SmsGateway", broker=broker, backend=result_backend, include=["app.tasks"]
)
