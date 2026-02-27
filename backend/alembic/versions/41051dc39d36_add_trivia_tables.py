"""add trivia tables

Revision ID: 41051dc39d36
Revises: 7e6330ab1ac8
Create Date: 2026-02-27 07:37:30.531990

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41051dc39d36'
down_revision: Union[str, Sequence[str], None] = '7e6330ab1ac8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('trivia_categories',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('slug', sa.String(length=100), nullable=False),
    sa.Column('is_brain_rot', sa.Boolean(), nullable=False),
    sa.Column('icon', sa.String(length=50), nullable=False),
    sa.Column('question_count', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trivia_categories_slug'), 'trivia_categories', ['slug'], unique=True)
    op.create_table('trivia_questions',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('category_id', sa.Uuid(), nullable=False),
    sa.Column('question_text', sa.Text(), nullable=False),
    sa.Column('correct_answer', sa.String(length=500), nullable=False),
    sa.Column('incorrect_answers', sa.Text(), nullable=False),
    sa.Column('difficulty', sa.Enum('EASY', 'MEDIUM', 'HARD', name='difficulty'), nullable=False),
    sa.Column('source', sa.Enum('OPENTDB', 'CUSTOM', name='question_source'), nullable=False),
    sa.Column('external_id', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['trivia_categories.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('external_id')
    )
    op.create_index('ix_trivia_questions_category_id', 'trivia_questions', ['category_id'], unique=False)
    op.create_index('ix_trivia_questions_difficulty', 'trivia_questions', ['difficulty'], unique=False)
    op.create_index('ix_trivia_questions_is_active', 'trivia_questions', ['is_active'], unique=False)
    op.create_table('user_trivia_attempts',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('question_id', sa.Uuid(), nullable=False),
    sa.Column('selected_answer', sa.String(length=500), nullable=False),
    sa.Column('is_correct', sa.Boolean(), nullable=False),
    sa.Column('aura_earned', sa.Integer(), nullable=False),
    sa.Column('answered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['question_id'], ['trivia_questions.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'question_id', name='uq_user_trivia_attempt')
    )
    op.create_index('ix_user_trivia_attempts_answered_at', 'user_trivia_attempts', ['answered_at'], unique=False)
    op.create_index('ix_user_trivia_attempts_user_id', 'user_trivia_attempts', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_user_trivia_attempts_user_id', table_name='user_trivia_attempts')
    op.drop_index('ix_user_trivia_attempts_answered_at', table_name='user_trivia_attempts')
    op.drop_table('user_trivia_attempts')
    op.drop_index('ix_trivia_questions_is_active', table_name='trivia_questions')
    op.drop_index('ix_trivia_questions_difficulty', table_name='trivia_questions')
    op.drop_index('ix_trivia_questions_category_id', table_name='trivia_questions')
    op.drop_table('trivia_questions')
    op.drop_index(op.f('ix_trivia_categories_slug'), table_name='trivia_categories')
    op.drop_table('trivia_categories')
