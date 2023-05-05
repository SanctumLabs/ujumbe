"""initial

Revision ID: 0ad6b839a7f9
Revises: ac52bb38b7cf
Create Date: 2023-05-05 17:19:36.419982

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0ad6b839a7f9"
down_revision = "ac52bb38b7cf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "sms",
        sa.Column("sender", sa.String(), nullable=False),
        sa.Column("recipient", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column(
            "delivery_status",
            sa.Enum(
                "ACCEPTED",
                "SCHEDULED",
                "CANCELED",
                "QUEUED",
                "SENDING",
                "SENT",
                "FAILED",
                "DELIVERED",
                "UNDELIVERED",
                "RECEIVING",
                "READ",
                "PENDING",
                "UNKNOWN",
                name="smsdeliverystatus",
            ),
            nullable=True,
        ),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("identifier", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_by", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("identifier"),
        sa.UniqueConstraint(
            "sender",
            "recipient",
            "message",
            name="sms_sender_recipient_message_constraint",
        ),
    )
    op.create_index(op.f("ix_sms_created_at"), "sms", ["created_at"], unique=False)
    op.create_table(
        "sms_responses",
        sa.Column(
            "account_sid",
            sa.String(),
            nullable=False,
            comment="SID of the account that sent the message",
        ),
        sa.Column(
            "sid",
            sa.String(),
            nullable=False,
            comment="Unique string that was created to identifier the message",
        ),
        sa.Column(
            "date_created",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Date and time in GMT that resource was created",
        ),
        sa.Column(
            "date_sent",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Date and time in GMT that resource was sent",
        ),
        sa.Column(
            "date_updated",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Date and time in GMT that resource was last updated",
        ),
        sa.Column(
            "sms_direction",
            sa.Enum(
                "OUTBOUND",
                "INBOUND",
                "OUTBOUND_API",
                "OUTBOUND_REPLY",
                "UNKNOWN",
                name="smstype",
            ),
            nullable=True,
            comment="Direction of the message",
        ),
        sa.Column(
            "num_media",
            sa.Integer(),
            nullable=False,
            comment="Number of media files associated with the message",
        ),
        sa.Column(
            "num_segments",
            sa.Integer(),
            nullable=False,
            comment="Number of segments to make up a complete message",
        ),
        sa.Column(
            "price",
            sa.Float(),
            nullable=True,
            comment="Amount billed for each message, priced per segment",
        ),
        sa.Column(
            "currency",
            sa.String(),
            nullable=True,
            comment="Currency in which price is measured in ISO 4127 format",
        ),
        sa.Column(
            "subresource_uris",
            sa.JSON(),
            nullable=True,
            comment="A list of related resources identified by their URIs relative to https://api.twilio.com",
        ),
        sa.Column(
            "uri",
            sa.String(),
            nullable=False,
            comment="URI of resource, relative to https://api.twilio.com",
        ),
        sa.Column(
            "messaging_service_sid",
            sa.String(),
            nullable=True,
            comment="SID of the messaging service used. Null if not used",
        ),
        sa.Column(
            "error_code",
            sa.String(),
            nullable=True,
            comment="Code returned if message status is failed or undelivered",
        ),
        sa.Column(
            "error_message",
            sa.String(),
            nullable=True,
            comment="Description of error code if available",
        ),
        sa.Column(
            "delivery_status",
            sa.Enum(
                "ACCEPTED",
                "SCHEDULED",
                "CANCELED",
                "QUEUED",
                "SENDING",
                "SENT",
                "FAILED",
                "DELIVERED",
                "UNDELIVERED",
                "RECEIVING",
                "READ",
                "PENDING",
                "UNKNOWN",
                name="smsdeliverystatus",
            ),
            nullable=True,
            comment="Status of the message",
        ),
        sa.Column("sms_id", sa.Integer(), nullable=False, comment="SMS ID"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("identifier", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_by", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["sms_id"],
            ["sms.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("identifier"),
        sa.UniqueConstraint("sid"),
    )
    op.create_index(
        op.f("ix_sms_responses_created_at"),
        "sms_responses",
        ["created_at"],
        unique=False,
    )
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker()
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute("SELECT audit.audit_table('sms')")
    session.execute("SELECT audit.audit_table('sms_responses')")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_sms_responses_created_at"), table_name="sms_responses")
    op.drop_table("sms_responses")
    op.drop_index(op.f("ix_sms_created_at"), table_name="sms")
    op.drop_table("sms")
    # ### end Alembic commands ###
