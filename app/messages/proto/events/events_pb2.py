# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: events/events.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import descriptor_pb2 as google_dot_protobuf_dot_descriptor__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13\x65vents/events.proto\x12\x11ujumbe.sms.events\x1a google/protobuf/descriptor.proto:7\n\x06\x64omain\x12\x1c.google.protobuf.FileOptions\x18\x85\x8f\xcb\x05 \x01(\tR\x06\x64omain:;\n\x08grouping\x12\x1c.google.protobuf.FileOptions\x18\x86\x8f\xcb\x05 \x01(\tR\x08grouping:A\n\nevent_type\x12\x1f.google.protobuf.MessageOptions\x18\x87\x8f\xcb\x05 \x01(\tR\teventType:6\n\x04tags\x12\x1f.google.protobuf.MessageOptions\x18\x88\x8f\xcb\x05 \x03(\tR\x04tagsB\x8a\x01\n\x15\x63om.ujumbe.sms.eventsB\x0b\x45ventsProtoP\x01\xa2\x02\x03USE\xaa\x02\x11Ujumbe.Sms.Events\xca\x02\x11Ujumbe\\Sms\\Events\xe2\x02\x1dUjumbe\\Sms\\Events\\GPBMetadata\xea\x02\x13Ujumbe::Sms::Eventsb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'events.events_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
  google_dot_protobuf_dot_descriptor__pb2.FileOptions.RegisterExtension(domain)
  google_dot_protobuf_dot_descriptor__pb2.FileOptions.RegisterExtension(grouping)
  google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(event_type)
  google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(tags)

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\025com.ujumbe.sms.eventsB\013EventsProtoP\001\242\002\003USE\252\002\021Ujumbe.Sms.Events\312\002\021Ujumbe\\Sms\\Events\342\002\035Ujumbe\\Sms\\Events\\GPBMetadata\352\002\023Ujumbe::Sms::Events'
# @@protoc_insertion_point(module_scope)
