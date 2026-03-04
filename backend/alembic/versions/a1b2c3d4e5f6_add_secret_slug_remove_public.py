"""add secret_slug and remove public access level

Revision ID: a1b2c3d4e5f6
Revises: 5d157b105db3
Create Date: 2026-02-28 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "5d157b105db3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add secret_slug column and migrate PUBLIC streams to FRIENDS."""
    op.add_column("streams", sa.Column("secret_slug", sa.String(64), nullable=True))
    op.create_index("ix_streams_secret_slug", "streams", ["secret_slug"])

    # Migrate any existing PUBLIC streams to FRIENDS
    op.execute("UPDATE streams SET access_level = 'FRIENDS' WHERE access_level = 'PUBLIC'")


def downgrade() -> None:
    """Remove secret_slug column."""
    op.drop_index("ix_streams_secret_slug", table_name="streams")
    op.drop_column("streams", "secret_slug")
