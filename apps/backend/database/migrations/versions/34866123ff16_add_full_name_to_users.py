"""add full_name to users

Revision ID: 34866123ff16
Revises: 9a1b2c3d4e5f
Create Date: 2026-09-13 19:32:58.223111

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34866123ff16'
down_revision: Union[str, Sequence[str], None] = '9a1b2c3d4e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('full_name', sa.String(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('users', 'full_name')
