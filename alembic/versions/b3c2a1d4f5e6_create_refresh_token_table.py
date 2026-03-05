"""Create refresh_tokens table

Revision ID: b3c2a1d4f5e6
Revises: 18b339dffa5d
Create Date: 2026-02-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = 'b3c2a1d4f5e6'
down_revision: Union[str, Sequence[str], None] = '18b339dffa5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'refresh_tokens',
        sa.Column('id', mysql.VARCHAR(length=36), nullable=False),
        sa.Column('created_at', mysql.DATETIME(), server_default=sa.text('(now())'), nullable=False),
        sa.Column('updated_at', mysql.DATETIME(), server_default=sa.text('(now())'), nullable=False),
        sa.Column('user_id', mysql.VARCHAR(length=36), nullable=False),
        sa.Column('jti', mysql.VARCHAR(length=36), nullable=False),
        sa.Column('token_hash', mysql.VARCHAR(length=128), nullable=False),
        sa.Column('device_id', mysql.VARCHAR(length=255), nullable=True),
        sa.Column('ip', mysql.VARCHAR(length=45), nullable=True),
        sa.Column('user_agent', mysql.VARCHAR(length=512), nullable=True),
        sa.Column('expires_at', mysql.DATETIME(), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('rotated_from', mysql.VARCHAR(length=36), nullable=True),
        sa.Column('rotated_at', mysql.DATETIME(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['rotated_from'], ['refresh_tokens.id'], ),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_0900_ai_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_refresh_tokens_jti'), 'refresh_tokens', ['jti'], unique=True)
    op.create_index(op.f('ix_refresh_tokens_token_hash'), 'refresh_tokens', ['token_hash'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_refresh_tokens_token_hash'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_jti'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
