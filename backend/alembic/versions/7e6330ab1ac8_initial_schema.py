"""initial schema

Revision ID: 7e6330ab1ac8
Revises:
Create Date: 2026-02-26 22:17:14.673834

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "7e6330ab1ac8"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- enums (used by column definitions below) ---
    stream_status = sa.Enum("scheduled", "live", "ended", name="stream_status")
    participant_role = sa.Enum("host", "moderator", "viewer", name="participant_role")
    message_type = sa.Enum("text", "emote", "system", "aura_gift", name="message_type")
    transaction_type = sa.Enum("stream_reward", "gift", "bonus", "refund", name="transaction_type")

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("aura_balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_is_active", "users", ["is_active"])

    # --- streams ---
    op.create_table(
        "streams",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("host_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", stream_status, nullable=False, server_default="scheduled"),
        sa.Column("room_name", sa.String(100), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_recording", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("recording_url", sa.String(500), nullable=True),
        sa.Column("thumbnail_url", sa.String(500), nullable=True),
        sa.Column("aura_pool", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_viewers", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["host_id"], ["users.id"]),
        sa.UniqueConstraint("room_name"),
    )
    op.create_index("ix_streams_host_id", "streams", ["host_id"])
    op.create_index("ix_streams_status", "streams", ["status"])
    op.create_index("ix_streams_room_name", "streams", ["room_name"], unique=True)
    op.create_index("ix_streams_started_at", "streams", ["started_at"])

    # --- stream_invite_links ---
    op.create_table(
        "stream_invite_links",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("stream_id", sa.Uuid(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("token", sa.String(64), nullable=False),
        sa.Column("max_uses", sa.Integer(), nullable=True),
        sa.Column("use_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["stream_id"], ["streams.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.UniqueConstraint("token"),
    )
    op.create_index("ix_stream_invite_links_stream_id", "stream_invite_links", ["stream_id"])
    op.create_index("ix_stream_invite_links_token", "stream_invite_links", ["token"], unique=True)

    # --- stream_participants ---
    op.create_table(
        "stream_participants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("stream_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", participant_role, nullable=False),
        sa.Column("invite_link_id", sa.Uuid(), nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("left_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("aura_received", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_banned", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["stream_id"], ["streams.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["invite_link_id"], ["stream_invite_links.id"]),
    )
    op.create_index("ix_stream_participants_stream_id", "stream_participants", ["stream_id"])
    op.create_index("ix_stream_participants_user_id", "stream_participants", ["user_id"])

    # --- chat_messages ---
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("stream_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("message_type", message_type, nullable=False, server_default="text"),
        sa.Column("reply_to_id", sa.Uuid(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["stream_id"], ["streams.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["reply_to_id"], ["chat_messages.id"]),
    )
    op.create_index("ix_chat_messages_stream_created", "chat_messages", ["stream_id", "created_at"])
    op.create_index("ix_chat_messages_user_id", "chat_messages", ["user_id"])

    # --- emotes ---
    op.create_table(
        "emotes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("image_url", sa.String(500), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("is_global", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_animated", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_emotes_code", "emotes", ["code"], unique=True)
    op.create_index("ix_emotes_created_by", "emotes", ["created_by"])
    op.create_index("ix_emotes_is_global", "emotes", ["is_global"])

    # --- aura_transactions ---
    op.create_table(
        "aura_transactions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("from_user_id", sa.Uuid(), nullable=True),
        sa.Column("to_user_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("transaction_type", transaction_type, nullable=False),
        sa.Column("stream_id", sa.Uuid(), nullable=True),
        sa.Column("note", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["from_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["to_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["stream_id"], ["streams.id"]),
    )
    op.create_index("ix_aura_transactions_from_user_id", "aura_transactions", ["from_user_id"])
    op.create_index("ix_aura_transactions_to_user_id", "aura_transactions", ["to_user_id"])
    op.create_index("ix_aura_transactions_stream_id", "aura_transactions", ["stream_id"])
    op.create_index("ix_aura_transactions_created_at", "aura_transactions", ["created_at"])

    # --- user_stats ---
    op.create_table(
        "user_stats",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("total_streams_hosted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_streams_watched", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_watch_time_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_stream_time_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_aura_earned", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_aura_given", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_messages_sent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_emotes_sent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("longest_stream_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("biggest_aura_drop", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_user_stats_user_id", "user_stats", ["user_id"], unique=True)

    # --- stream_metrics ---
    op.create_table(
        "stream_metrics",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("stream_id", sa.Uuid(), nullable=False),
        sa.Column("peak_viewers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_unique_viewers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("avg_viewers", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("total_messages", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_emotes_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_aura_distributed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duration_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("top_chatter_id", sa.Uuid(), nullable=True),
        sa.Column("most_used_emote_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["stream_id"], ["streams.id"]),
        sa.ForeignKeyConstraint(["top_chatter_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["most_used_emote_id"], ["emotes.id"]),
        sa.UniqueConstraint("stream_id"),
    )
    op.create_index("ix_stream_metrics_stream_id", "stream_metrics", ["stream_id"], unique=True)


def downgrade() -> None:
    op.drop_table("stream_metrics")
    op.drop_table("user_stats")
    op.drop_table("aura_transactions")
    op.drop_table("emotes")
    op.drop_table("chat_messages")
    op.drop_table("stream_participants")
    op.drop_table("stream_invite_links")
    op.drop_table("streams")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS transaction_type")
    op.execute("DROP TYPE IF EXISTS message_type")
    op.execute("DROP TYPE IF EXISTS participant_role")
    op.execute("DROP TYPE IF EXISTS stream_status")
