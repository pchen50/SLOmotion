"""readding extra movies and initial users

Revision ID: 4b6364a5d8df
Revises: 7c8dc4beba56
Create Date: 2025-05-28 21:05:12.761049

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from src import database as db


# revision identifiers, used by Alembic.
revision: str = "4b6364a5d8df"
down_revision: Union[str, None] = "7c8dc4beba56"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    connect = op.get_bind()
    mineMovie = (
        connect.execute(
            sa.text(
                "INSERT into movies (name,genre, year) VALUES ('A Minecraft Movie', 'Adventure', 2025) RETURNING id"
            )
        )
        .one()
        .id
    )
    barbieMovie = (
        connect.execute(
            sa.text(
                "INSERT into movies (name,genre, year) VALUES ('Barbie', 'Comedy', 2023) RETURNING id"
            )
        )
        .one()
        .id
    )

    aliceId = (
        connect.execute(
            sa.text(
                "INSERT into users (name, username) VALUES ('Alice', 'aliceMovies') RETURNING id"
            )
        )
        .one()
        .id
    )

    bobId = (
        connect.execute(
            sa.text(
                "INSERT into users (name, username) VALUES ('Bob', 'bobRatings') RETURNING id"
            )
        )
        .one()
        .id
    )

    joeId = (
        connect.execute(
            sa.text(
                "INSERT into users (name, username) VALUES ('Joe', 'watchWithJoe') RETURNING id"
            )
        )
        .one()
        .id
    )

    eveId = (
        connect.execute(
            sa.text(
                "INSERT into users (name, username) VALUES ('Eve','filmCriticEve') RETURNING id"
            )
        )
        .one()
        .id
    )

    with db.engine.begin() as connection:
        gwhId = (
            connection.execute(
                sa.text(
                    """
                SELECT id 
                FROM movies
                WHERE name = 'Good Will Hunting'
                """
                )
            )
            .one()
            .id
        )

        gladiatorId = (
            connection.execute(
                sa.text(
                    """
                SELECT id 
                FROM movies
                WHERE name = 'Gladiator'
                """
                )
            )
            .one()
            .id
        )

        connect.execute(
            sa.text(
                "INSERT into movie_ratings (movie_id,user_id,notes,rating,status) VALUES (:movie_id, :user_id, '', :rating, 'want to watch')"
            ),
            [{"movie_id": mineMovie, "user_id": joeId, "rating": None}],
        )

        connect.execute(
            sa.text(
                "INSERT into movie_ratings (movie_id,user_id,notes,rating,status) VALUES (:movie_id, :user_id, 'amazing cinematography', 5, 'watched')"
            ),
            [{"movie_id": gwhId, "user_id": joeId}],
        )

        connect.execute(
            sa.text(
                "INSERT into movie_ratings (movie_id,user_id,notes,rating,status) VALUES (:movie_id, :user_id, 'nice', 6, 'watched')"
            ),
            [{"movie_id": gladiatorId, "user_id": bobId}],
        )

        connect.execute(
            sa.text(
                "INSERT into movie_ratings (movie_id,user_id,notes,rating,status) VALUES (:movie_id, :user_id, 'really good', 7, 'watched')"
            ),
            [{"movie_id": gwhId, "user_id": bobId}],
        )

        connect.execute(
            sa.text(
                "INSERT into movie_ratings (movie_id,user_id,notes,rating,status) VALUES (:movie_id, :user_id, '', :rating, 'want to watch')"
            ),
            [{"movie_id": barbieMovie, "user_id": aliceId, "rating": None}],
        )

        connect.execute(
            sa.text(
                "INSERT into movie_ratings (movie_id,user_id,notes,rating,status) VALUES (:movie_id, :user_id, 'nice', 6, 'watched')"
            ),
            [{"movie_id": gladiatorId, "user_id": eveId}],
        )

        connect.execute(
            sa.text(
                "INSERT into movie_ratings (movie_id,user_id,notes,rating,status) VALUES (:movie_id, :user_id, 'enjoyed', 7, 'watched')"
            ),
            [{"movie_id": gwhId, "user_id": eveId}],
        )

        connect.execute(
            sa.text(
                "INSERT into movie_ratings (movie_id,user_id,notes,rating,status) VALUES (:movie_id, :user_id, 'inspiring', 7, 'watched')"
            ),
            [{"movie_id": barbieMovie, "user_id": eveId}],
        )


def downgrade() -> None:
    """Downgrade schema."""
    pass
