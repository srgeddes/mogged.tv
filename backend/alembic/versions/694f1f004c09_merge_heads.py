"""merge_heads

Revision ID: 694f1f004c09
Revises: 3bb3d24aeac5, a1b2c3d4e5f6
Create Date: 2026-02-28 16:01:12.387760

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '694f1f004c09'
down_revision: Union[str, Sequence[str], None] = ('3bb3d24aeac5', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
