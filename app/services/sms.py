"""
Send sms service wrapper. This handles sending the actual sms to recipients and handles connection to an SMS client
if provided with the credentials to. If that fails, this will use an alternative to send an sms using Twilio API.
Ensure that the correct environment variables have been set for the SMTP client and Sendgrid for this method to work.
These env variables are imported and included in the config.py file under the Config class for these to be available in
the current application context
"""
from app.logger import log as logger
from flask import current_app
from .exceptions import SmsSendingException, ServiceIntegrationException
import requests


@logger.catch
def send_sms(to: list, message: str, from_: dict = None):
    """
    Sends a plain text message to a list of recipients with 
    :param dict from_: sender of sms (Optional), will default to value set in DEFAULT_SENDER config
    :param str message: Message to send in body of sms
    :param list to: List of recipients of this sms
    :param str subject: The subject of the sms
    """

    try:
        logger.info(f"Sending sms to {to}")

        # Set the message sender it it exists else default it
        sender = from_ if from_ else current_app.config.get("DEFAULT_SENDER")

        msg = Message(
            sender=sender,
            subject=subject,
            recipients=to,
            cc=cc,
            bcc=bcc)

        if "<html" in message:
            msg.html = message
        else:
            msg.body = message

        mail.send(msg)
        return dict(success=True, message="Message successfully sent")
    except Exception as e:
        # this should only happen if there is a fallback and we fail to send sms with the default setting
        # if in that event, then the application should try sending an sms using Sendgrid

        logger.error(f"Failed to send sms with error {e}")
        logger.warning(f"Using alternative to send sms")

        # get the token and base url
        token = current_app.config.get("SMS_TOKEN")
        base_url = current_app.config.get("SMS_API_URL")

        recipients_to = [{"email": email} for email in to]

        # this will be used to construct the recipients of the sms
        recipients = dict(to=recipients_to)

        sender = {"email": from_.get("email") if from_ else current_app.config.get("DEFAULT_SENDER"),
                  "name": from_.get("name") if from_ else current_app.config.get("DEFAULT_SENDER")}

        request_body = {
            "personalizations": [
                recipients
            ],
            "from": sender,
            "content": [
                {
                    "type": "text/html",
                    "value": message
                }
            ]
        }

        try:

            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(url=base_url, json=request_body, headers=headers)

            if not response.ok:
                raise ServiceIntegrationException(f"Sending sms failed with status code: {response.status_code}")
            else:
                return dict(
                    success=True,
                    message="Message successfully sent",
                )

        except Exception as e:
            logger.error(f"Failed to send message with alternative with error {e}")
            raise SmsSendingException(f"Failed to send sms message with error {e}")
