"""Add username column to users table

Revision ID: 1e2ce8491981
Revises: 4b6364a5d8df
Create Date: 2025-05-30 19:27:01.662625

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1e2ce8491981"
down_revision: Union[str, None] = "4b6364a5d8df"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("users", sa.Column("username", sa.Text(), nullable=False))
    op.create_unique_constraint("uq_users_username", "users", ["username"])


def downgrade():
    op.drop_constraint("uq_users_username", "users", type_="unique")
    op.drop_column("users", "username")
