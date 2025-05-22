"""add name and profile columns

Revision ID: db298f5d67c1
Revises: 17bf17ac0960
Create Date: 2025-05-22 07:08:49.346944
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db298f5d67c1'
down_revision: Union[str, None] = '17bf17ac0960'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define enum type separately
user_profile_enum = sa.Enum('normal_user', 'admin_user', name='userprofile')


def upgrade() -> None:
    """Upgrade schema."""
    # Create the enum type
    user_profile_enum.create(op.get_bind(), checkfirst=True)

    # Add new columns
    op.add_column('users', sa.Column('name', sa.String(), nullable=False))
    op.add_column('users', sa.Column('profile', user_profile_enum, nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    # Drop columns
    op.drop_column('users', 'profile')
    op.drop_column('users', 'name')

    # Drop enum type
    user_profile_enum.drop(op.get_bind(), checkfirst=True)
