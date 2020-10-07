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
import africastalking


@logger.catch
def send_sms(to: list, message: str):
    """
    Sends a plain text message to a list of recipients with 
    :param str message: Message to send in body of sms
    :param list to: List of recipients of this sms
    :param str subject: The subject of the sms
    """

    try:
        logger.info(f"Sending sms to {to}")

        username = current_app.config.get("SMS_API_USERNAME")
        api_key = current_app.config.get("SMS_API_TOKEN")

        africastalking.initialize(username, api_key)
        sms = africastalking.SMS

        # synchronous request to send out an SMS
        response = sms.send(message, to)
        return dict(message="Message successfully sent", response=response)
    except Exception as e:
        logger.error(f"Failed to send sms with error {e}")

        raise SmsSendingException(f"Failed to send sms message with error {e}")
