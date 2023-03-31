# import africastalking

class SmsClient:
    def __init__(self, sms_client):
        self.sms_client = sms_client

    def send(self, sms):
        """
        Sends a plain text message to a list of recipients with
        :param str message: Message to send in body of sms
        :param list to: List of recipients of this sms
        :param str subject: The subject of the sms
        :param sender_id subject: The Registered alphanumeric sender id
        """

        try:
            # logger.info(f"Sending sms to {to}")

            # username = get_config().sms_api_username
            # api_key = get_config().sms_api_token
            # sender_id = get_config().sms_sender_id

            # africastalking.initialize(username, api_key)
            # sms = africastalking.SMS

            # synchronous request to send out an SMS
            # response = sms.send(message, to, sender_id)
            return dict(message="Message successfully sent", response={})
        except Exception as e:
            # logger.error(f"Failed to send sms with error {e}")

            # raise SmsSendingException(f"Failed to send sms message with error {e}")
            raise e
