from collections import namedtuple

SmsResponseDto = namedtuple("SmsResponseDto", [
    "account_sid",
    "api_version",
    "body",
    "date_created",
    "date_sent",
    "date_updated",
    "direction",
    "error_code",
    "error_message",
    "from_",
    "messaging_service_sid",
    "num_media",
    "num_segments",
    "price",
    "price_unit",
    "sid",
    "status",
    "to",
    "uri",
    "subresource_uris",
])
