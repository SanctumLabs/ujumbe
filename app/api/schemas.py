"""
Schemas used to validate API requests sent to the application. These validate based on whether a field is required
or has a valid sms format. Uses Marshmallow to handle the schema validation. Refer to this documentation for more on
validation. https://marshmallow.readthedocs.io/en/3.0/
"""
from marshmallow import Schema, fields
from marshmallow.validate import Length, Regexp


class SmsMessageSchema(Schema):
    """
    Sms message schema, used to validate the sms message
    :cvar to: List of valid phone numbers to send sms message
    :cvar message: Message to use for the sms message. This will appear in the content of the body
    """

    to = fields.List(fields.String(validate=Regexp(r"^\+\d{1,3}\d{3,}$"), required=True), required=True, validate=Length(min=1))
    message = fields.String(required=True, validate=Length(min=1))
