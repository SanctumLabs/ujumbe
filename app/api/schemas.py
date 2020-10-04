"""
Schemas used to validate API requests sent to the application. These validate based on whether a field is required
or has a valid sms format. Uses Marshmallow to handle the schema validation. Refer to this documentation for more on
validation. https://marshmallow.readthedocs.io/en/3.0/
"""
from marshmallow import Schema, fields
from marshmallow.validate import Length


class SmsMessageSchema(Schema):
    """
    Sms message schema, used to validate the sms message
    :cvar from_: Message from which the sms is being sent from
    :cvar to: List of valid phone numbers to send sms message
    :cvar message: Message to use for the sms message. This will appear in the content of the body
    """
    from_ = fields.String(required=False)
    to = fields.List(fields.String(), required=True, validate=Length(min=1))
    message = fields.String(required=True, validate=Length(min=1))
