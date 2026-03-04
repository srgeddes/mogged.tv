"""fix_stream_enum_values

Revision ID: 37851551c6b9
Revises: 694f1f004c09
Create Date: 2026-02-28 16:40:44.240302

Fixes stream_status enum: lowercase values -> uppercase to match
SQLAlchemy StrEnum. stream_access_level is already uppercase.
"""
from typing import Sequence, Union

from alembic import op


revision: str = '37851551c6b9'
down_revision: Union[str, Sequence[str], None] = '694f1f004c09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix stream_status enum values from lowercase to uppercase."""

    # --- stream_status (lowercase -> uppercase) ---
    op.execute("ALTER TABLE streams ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TYPE stream_status RENAME TO stream_status_old")
    op.execute("CREATE TYPE stream_status AS ENUM ('SCHEDULED', 'LIVE', 'ENDED')")
    op.execute(
        "ALTER TABLE streams ALTER COLUMN status "
        "TYPE stream_status USING upper(status::text)::stream_status"
    )
    op.execute("ALTER TABLE streams ALTER COLUMN status SET DEFAULT 'SCHEDULED'::stream_status")
    op.execute("DROP TYPE stream_status_old")


def downgrade() -> None:
    """Revert stream_status enum back to lowercase values."""

    # --- stream_status (uppercase -> lowercase) ---
    op.execute("ALTER TABLE streams ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TYPE stream_status RENAME TO stream_status_old")
    op.execute("CREATE TYPE stream_status AS ENUM ('scheduled', 'live', 'ended')")
    op.execute(
        "ALTER TABLE streams ALTER COLUMN status "
        "TYPE stream_status USING lower(status::text)::stream_status"
    )
    op.execute("ALTER TABLE streams ALTER COLUMN status SET DEFAULT 'scheduled'::stream_status")
    op.execute("DROP TYPE stream_status_old")
