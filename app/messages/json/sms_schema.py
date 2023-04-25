sms_json_schema = """
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Sms",
  "description": "An SMS Message",
  "type": "object",
  "properties": {
    "id": {
      "description": "SMS ID",
      "type": "string"
    },
    "recipient": {
      "description": "Recipient of SMS",
      "type": "string"
    },
    "sender": {
      "description": "Sender of SMS",
      "type": "string"
    },
    "message": {
      "description": "SMS Message",
      "type": "string"
    },
    "status": {
      "description": "SMS Delivery status",
      "type": "string"
    },
    "response": {
      "description": "SMS Response",
      "type": "object"
    }
  },
  "required": [ "id", "recipient", "message", "status" ]
}
"""
