"""
Base model Mixin classes used by all database models in the system
"""
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, func, String, Integer
from sqlalchemy.ext.declarative import declared_attr
from nanoid import generate
from . import Base
import inflection

# A date time that indicates a record has not been deleted
NOT_DELETED = datetime(1970, 1, 1, 0, 0, 1, 0, timezone.utc)


class IdentifierPrimaryKeyMixin:
    """
    Contains fields specific to uniquely identifying a database record
    """

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    identifier = Column(String, unique=True, default=generate, nullable=False)


class TimestampColumnsMixin:
    """
    Contains timestamp fields for a record
    """

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SoftDeleteMixin:
    """
    Soft deletion by storing a timestamp of when this was deleted. `NOT_DELETED`
    is used instead of null so that you can safely have a composite key with this
    column. e.g. (email, deleted) will be a valid unique key. If this was null then
    PostgreSQL would never enforce the constraint
    """

    deleted_at = Column(DateTime(timezone=True), default=NOT_DELETED)


class AuditedMixin:
    """
    Audit mixin contains fields that will contain audit information
    """

    updated_by = Column(String, default="system")


class TableNameMixin:
    """
    Contains table attributes and fields for a record in the database
    """

    @declared_attr
    def __tablename__(cls):
        """
        Table names are snake_case_plural - e.g. user_roles
        Returns: table name
        """
        return inflection.pluralize(inflection.underscore(cls.__name__))


class BaseModel(
    Base,
    IdentifierPrimaryKeyMixin,
    TimestampColumnsMixin,
    SoftDeleteMixin,
    AuditedMixin,
    TableNameMixin,
):
    """
    Base model for all models in the database. Database models inherit from this class
    """

    __abstract__ = True

    @classmethod
    @property
    def pk(cls):
        """
        property used to get the primary key of a model
        Returns: ID attribute of model
        """
        if hasattr(cls, "id"):
            return cls.id
        elif hasattr(cls, "identifier"):
            return cls.identifier
        elif hasattr(cls, "uuid"):
            return cls.uuid
        else:
            raise Exception("Class does not have pk (primary key) defined")
