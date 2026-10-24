"""allow SMS without a sender

Revision ID: cbf76f4c2bde
Revises: 0ad6b839a7f9
Create Date: 2026-10-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cbf76f4c2bde"
down_revision = "0ad6b839a7f9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "sms",
        "sender",
        existing_type=sa.String(),
        nullable=True,
    )


def downgrade() -> None:
    raise NotImplementedError(
        "Cannot restore a non-null sender constraint while senderless SMS records exist."
    )
