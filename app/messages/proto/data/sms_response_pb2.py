# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: data/sms_response.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2
from data import sms_status_pb2 as data_dot_sms__status__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17\x64\x61ta/sms_response.proto\x12\x13ujumbe.sms.messages\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x19google/protobuf/any.proto\x1a\x15\x64\x61ta/sms_status.proto\"\x96\x06\n\x0bSmsResponse\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x1f\n\x0b\x61\x63\x63ount_sid\x18\x02 \x01(\tR\naccountSid\x12\x10\n\x03sid\x18\x03 \x01(\tR\x03sid\x12\x37\n\x08sms_date\x18\x04 \x01(\x0b\x32\x1c.ujumbe.sms.messages.SmsDateR\x07smsDate\x12\x37\n\x08sms_type\x18\x05 \x01(\x0e\x32\x1c.ujumbe.sms.messages.SmsTypeR\x07smsType\x12\x1b\n\tnum_media\x18\x06 \x01(\x03R\x08numMedia\x12!\n\x0cnum_segments\x18\x07 \x01(\x03R\x0bnumSegments\x12\x33\n\x05price\x18\x08 \x01(\x0b\x32\x1d.ujumbe.sms.messages.SmsPriceR\x05price\x12\x36\n\x06status\x18\t \x01(\x0e\x32\x1e.ujumbe.sms.messages.SmsStatusR\x06status\x12`\n\x10subresource_uris\x18\n \x03(\x0b\x32\x35.ujumbe.sms.messages.SmsResponse.SubresourceUrisEntryR\x0fsubresourceUris\x12\x10\n\x03uri\x18\x0b \x01(\tR\x03uri\x12\x15\n\x06sms_id\x18\x0c \x01(\tR\x05smsId\x12\x37\n\x15messaging_service_sid\x18\r \x01(\tH\x00R\x13messagingServiceSid\x88\x01\x01\x12\"\n\nerror_code\x18\x0e \x01(\tH\x01R\terrorCode\x88\x01\x01\x12(\n\rerror_message\x18\x0f \x01(\tH\x02R\x0c\x65rrorMessage\x88\x01\x01\x1aX\n\x14SubresourceUrisEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12*\n\x05value\x18\x02 \x01(\x0b\x32\x14.google.protobuf.AnyR\x05value:\x02\x38\x01\x42\x18\n\x16_messaging_service_sidB\r\n\x0b_error_codeB\x10\n\x0e_error_message\"\xc0\x01\n\x07SmsDate\x12=\n\x0c\x64\x61te_created\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.TimestampR\x0b\x64\x61teCreated\x12\x37\n\tdate_sent\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.TimestampR\x08\x64\x61teSent\x12=\n\x0c\x64\x61te_updated\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.TimestampR\x0b\x64\x61teUpdated\"]\n\x08SmsPrice\x12\x19\n\x05price\x18\x01 \x01(\x02H\x00R\x05price\x88\x01\x01\x12\x1f\n\x08\x63urrency\x18\x02 \x01(\tH\x01R\x08\x63urrency\x88\x01\x01\x42\x08\n\x06_priceB\x0b\n\t_currency*W\n\x07SmsType\x12\x0c\n\x08OUTBOUND\x10\x00\x12\x0b\n\x07INBOUND\x10\x01\x12\x10\n\x0cOUTBOUND_API\x10\x02\x12\x12\n\x0eOUTBOUND_REPLY\x10\x03\x12\x0b\n\x07UNKNOWN\x10\x04\x42\x99\x01\n\x17\x63om.ujumbe.sms.messagesB\x10SmsResponseProtoP\x01\xa2\x02\x03USM\xaa\x02\x13Ujumbe.Sms.Messages\xca\x02\x13Ujumbe\\Sms\\Messages\xe2\x02\x1fUjumbe\\Sms\\Messages\\GPBMetadata\xea\x02\x15Ujumbe::Sms::Messagesb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'data.sms_response_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\027com.ujumbe.sms.messagesB\020SmsResponseProtoP\001\242\002\003USM\252\002\023Ujumbe.Sms.Messages\312\002\023Ujumbe\\Sms\\Messages\342\002\037Ujumbe\\Sms\\Messages\\GPBMetadata\352\002\025Ujumbe::Sms::Messages'
  _SMSRESPONSE_SUBRESOURCEURISENTRY._options = None
  _SMSRESPONSE_SUBRESOURCEURISENTRY._serialized_options = b'8\001'
  _SMSTYPE._serialized_start=1214
  _SMSTYPE._serialized_end=1301
  _SMSRESPONSE._serialized_start=132
  _SMSRESPONSE._serialized_end=922
  _SMSRESPONSE_SUBRESOURCEURISENTRY._serialized_start=775
  _SMSRESPONSE_SUBRESOURCEURISENTRY._serialized_end=863
  _SMSDATE._serialized_start=925
  _SMSDATE._serialized_end=1117
  _SMSPRICE._serialized_start=1119
  _SMSPRICE._serialized_end=1212
# @@protoc_insertion_point(module_scope)
