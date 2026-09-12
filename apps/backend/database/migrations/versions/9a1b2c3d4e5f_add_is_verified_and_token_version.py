"""add is_verified and token_version to users

Revision ID: 9a1b2c3d4e5f
Revises: 85aa191e766e
Create Date: 2026-09-12 03:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '9a1b2c3d4e5f'
down_revision: Union[str, Sequence[str], None] = '85aa191e766e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Add is_verified column
    op.add_column(
        'users',
        sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False)
    )
    # 2. Add token_version column for session revocation
    op.add_column(
        'users',
        sa.Column('token_version', sa.Integer(), server_default='1', nullable=False)
    )
    
    # 3. Create index on is_verified
    op.create_index(op.f('ix_users_is_verified'), 'users', ['is_verified'], unique=False)
    
    # 4. Provider-aware grandfathering (M-03):
    # - Verified Google accounts are marked verified
    # - Verified Phone accounts are marked verified
    # - Pre-migration normal accounts (email is not null, not guest) are grandfathered as verified
    # - Guests remain unverified
    op.execute(
        sa.text("UPDATE users SET is_verified = TRUE WHERE google_id IS NOT NULL")
    )
    op.execute(
        sa.text("UPDATE users SET is_verified = TRUE WHERE phone_number IS NOT NULL")
    )
    op.execute(
        sa.text("UPDATE users SET is_verified = TRUE WHERE email IS NOT NULL AND is_guest = FALSE")
    )
    op.execute(
        sa.text("UPDATE users SET is_verified = FALSE WHERE is_guest = TRUE")
    )
    op.execute(
        sa.text("UPDATE users SET token_version = 1 WHERE token_version IS NULL")
    )

def downgrade() -> None:
    op.drop_index(op.f('ix_users_is_verified'), table_name='users')
    op.drop_column('users', 'token_version')
    op.drop_column('users', 'is_verified')
