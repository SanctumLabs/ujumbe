from app import celery_app
from app.logger import log
from app.services.sms import send_sms
from app.constants import SMS_ERROR_EXCHANGE, SMS_ERROR_ROUTING_KEY
from .exceptions import TaskException
import pika
import os
import json

broker_host = os.environ.get("BROKER_HOST")


@celery_app.task(bind=True, default_retry_delay=30, max_retries=3, name="sms_sending_task")
@log.catch
def sms_sending_task(self, from_, to, message):
    try:
        result = send_sms(
            from_=from_,
            to=to,
            message=message,
        )

        if not result:
            raise TaskException("SMS sending task failed")
        return result
    except Exception as exc:
        log.error(f"Error sending sms with error {exc}. Attempt {self.request.retries}/{self.max_retries} ...")

        if self.request.retries == self.max_retries:
            log.warning(f"Maximum attempts reached, pushing to error queue...")
            push_to_error_queue(from_, to, message)

        raise self.retry(countdown=30 * 2, exc=exc, max_retries=3)


def push_to_error_queue(from_, to, message):
    if broker_host:
        body = dict(
            from_=from_,
            to=to,
            message=message,
        )

        # to bytes
        body_bytes = json.dumps(body).encode('utf-8')

        # to decode
        # json.loads(res_bytes.decode('utf-8'))

        connection = pika.BlockingConnection(pika.ConnectionParameters(host=broker_host))
        channel = connection.channel()
        channel.basic_publish(exchange=SMS_ERROR_EXCHANGE, routing_key=SMS_ERROR_ROUTING_KEY,
                              body=body_bytes)
        connection.close()
