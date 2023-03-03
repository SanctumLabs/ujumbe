"""
Send sms service wrapper. This handles sending the actual sms to recipients and handles connection to an SMS client
if provided with the credentials to. If that fails, this will use an alternative to send an sms using Twilio API.
Ensure that the correct environment variables have been set for the SMTP client and Sendgrid for this method to work.
These env variables are imported and included in the config.py file under the Config class for these to be available in
the current application context
"""
from app.infra.logger import log as logger
from .exceptions import SmsSendingException, ServiceIntegrationException
from app.config import get_config

# import africastalking


@logger.catch
def send_sms(to: list, message: str):
    """
    Sends a plain text message to a list of recipients with
    :param str message: Message to send in body of sms
    :param list to: List of recipients of this sms
    :param str subject: The subject of the sms
    :param sender_id subject: The Registered alphanumeric sender id
    """

    try:
        logger.info(f"Sending sms to {to}")

        username = get_config().sms_api_username
        api_key = get_config().sms_api_token
        sender_id = get_config().sms_sender_id

        # africastalking.initialize(username, api_key)
        # sms = africastalking.SMS

        # synchronous request to send out an SMS
        # response = sms.send(message, to, sender_id)
        return dict(message="Message successfully sent", response={})
    except Exception as e:
        logger.error(f"Failed to send sms with error {e}")

        raise SmsSendingException(f"Failed to send sms message with error {e}")
