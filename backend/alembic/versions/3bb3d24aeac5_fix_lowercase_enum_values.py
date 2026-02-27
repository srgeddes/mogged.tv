"""fix_lowercase_enum_values

Revision ID: 3bb3d24aeac5
Revises: 5d157b105db3
Create Date: 2026-02-27 07:50:41.468789

The initial migration created message_type, participant_role, and
transaction_type enums with lowercase values, but SQLAlchemy StrEnum
sends uppercase names. This migration recreates each enum with uppercase
values and adds the missing TRIVIA_REWARD value to transaction_type.
"""
from typing import Sequence, Union

from alembic import op


revision: str = '3bb3d24aeac5'
down_revision: Union[str, Sequence[str], None] = '5d157b105db3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix lowercase enum values to uppercase for SQLAlchemy StrEnum compat."""

    # --- message_type ---
    op.execute("ALTER TABLE chat_messages ALTER COLUMN message_type DROP DEFAULT")
    op.execute("ALTER TYPE message_type RENAME TO message_type_old")
    op.execute("CREATE TYPE message_type AS ENUM ('TEXT', 'EMOTE', 'SYSTEM', 'AURA_GIFT')")
    op.execute(
        "ALTER TABLE chat_messages ALTER COLUMN message_type "
        "TYPE message_type USING upper(message_type::text)::message_type"
    )
    op.execute("ALTER TABLE chat_messages ALTER COLUMN message_type SET DEFAULT 'TEXT'::message_type")
    op.execute("DROP TYPE message_type_old")

    # --- participant_role ---
    op.execute("ALTER TYPE participant_role RENAME TO participant_role_old")
    op.execute("CREATE TYPE participant_role AS ENUM ('HOST', 'MODERATOR', 'VIEWER')")
    op.execute(
        "ALTER TABLE stream_participants ALTER COLUMN role "
        "TYPE participant_role USING upper(role::text)::participant_role"
    )
    op.execute("DROP TYPE participant_role_old")

    # --- transaction_type (also adds TRIVIA_REWARD) ---
    op.execute("ALTER TYPE transaction_type RENAME TO transaction_type_old")
    op.execute(
        "CREATE TYPE transaction_type AS ENUM "
        "('STREAM_REWARD', 'GIFT', 'BONUS', 'REFUND', 'TRIVIA_REWARD')"
    )
    op.execute(
        "ALTER TABLE aura_transactions ALTER COLUMN transaction_type "
        "TYPE transaction_type USING upper(transaction_type::text)::transaction_type"
    )
    op.execute("DROP TYPE transaction_type_old")


def downgrade() -> None:
    """Revert enums back to lowercase values."""

    # --- transaction_type ---
    op.execute("ALTER TYPE transaction_type RENAME TO transaction_type_old")
    op.execute(
        "CREATE TYPE transaction_type AS ENUM "
        "('stream_reward', 'gift', 'bonus', 'refund')"
    )
    op.execute(
        "ALTER TABLE aura_transactions ALTER COLUMN transaction_type "
        "TYPE transaction_type USING lower(transaction_type::text)::transaction_type"
    )
    op.execute("DROP TYPE transaction_type_old")

    # --- participant_role ---
    op.execute("ALTER TYPE participant_role RENAME TO participant_role_old")
    op.execute("CREATE TYPE participant_role AS ENUM ('host', 'moderator', 'viewer')")
    op.execute(
        "ALTER TABLE stream_participants ALTER COLUMN role "
        "TYPE participant_role USING lower(role::text)::participant_role"
    )
    op.execute("DROP TYPE participant_role_old")

    # --- message_type ---
    op.execute("ALTER TABLE chat_messages ALTER COLUMN message_type DROP DEFAULT")
    op.execute("ALTER TYPE message_type RENAME TO message_type_old")
    op.execute("CREATE TYPE message_type AS ENUM ('text', 'emote', 'system', 'aura_gift')")
    op.execute(
        "ALTER TABLE chat_messages ALTER COLUMN message_type "
        "TYPE message_type USING lower(message_type::text)::message_type"
    )
    op.execute("ALTER TABLE chat_messages ALTER COLUMN message_type SET DEFAULT 'text'::message_type")
    op.execute("DROP TYPE message_type_old")
