"""schema changes

Revision ID: 9c05649dfc2f
Revises: 61a4b98e64f7
Create Date: 2025-05-28 13:28:41.021014

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c05649dfc2f'
down_revision: Union[str, None] = '61a4b98e64f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table("watchlist_movie")
    op.drop_table("watchlists")
    connect = op.get_bind()
    connect.execute(
        sa.text(
            """
            TRUNCATE comments, movie_ratings, movies, users RESTART IDENTITY CASCADE
            """
        )
    )
    op.add_column(
        "users",
        sa.Column("username", sa.String(100), nullable=False)
    )
    op.create_unique_constraint("username_uq", "users", ["username"])
    op.create_foreign_key("commenter_foreign", "comments","users", ["commenter_user_id"],["id"])
    op.create_unique_constraint("comments_uq", "comments", ["commenter_user_id", "user_id", "movie_id"])
    op.alter_column("comments", "commenter_user_id", nullable=False)
    op.alter_column("comments", "user_id", nullable=False)
    op.alter_column("comments", "movie_id", nullable=False)
    op.alter_column("comments", "comment_text", nullable=False)
    op.add_column(
        "movies",
        sa.Column("year", sa.Integer, nullable=False)
    )
    op.alter_column("movie_ratings","movie_id", nullable=False)
    op.alter_column("movie_ratings","user_id", nullable=False)
    op.alter_column("movie_ratings","rating", type_=sa.Float)
    op.create_check_constraint(
        "rating_between_0_10",
        "movie_ratings",
        "rating >= 0 AND rating <= 10"
    )
    op.create_unique_constraint("movie_rating_uq", "movie_ratings", ["movie_id","user_id"])

    



def downgrade() -> None:
    """Downgrade schema."""
    pass
