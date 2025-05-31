"""populate alice, bob, joe, eve with movies and ratings

Revision ID: 61a4b98e64f7
Revises: 34a53ab6d376
Create Date: 2025-05-10 18:08:41.726936
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "61a4b98e64f7"
down_revision: Union[str, None] = "34a53ab6d376"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema by populating users, movies, watchlists, and ratings."""
    connect = op.get_bind()

    # Step 1: Insert movies into the movies table
    movies = {
        "A Minecraft Movie": "Adventure",
        "Barbie": "Comedy",
        "Good Will Hunting": "Drama",
        "Gladiator": "Action",
    }

    movie_ids = {}
    for name, genre in movies.items():
        movie_ids[name] = (
            connect.execute(
                sa.text(
                    "INSERT INTO movies (name, genre) VALUES (:name, :genre) RETURNING id"
                ),
                {"name": name, "genre": genre},
            )
            .one()
            .id
        )

    # Step 2: Create users and associated watchlists
    users = ["Alice", "Bob", "Joe", "Eve"]
    user_ids = {}
    watchlist_ids = {}
    for user in users:
        user_ids[user] = (
            connect.execute(
                sa.text("INSERT INTO users (name) VALUES (:name) RETURNING id"),
                {"name": user},
            )
            .one()
            .id
        )
        watchlist_ids[user] = (
            connect.execute(
                sa.text(
                    "INSERT INTO watchlists (user_id, public) VALUES (:user_id, true) RETURNING id"
                ),
                {"user_id": user_ids[user]},
            )
            .one()
            .id
        )

    # Step 3: Joe's ratings and watchlist additions
    joe_id = user_ids["Joe"]
    joe_watchlist = watchlist_ids["Joe"]
    joe_minecraft = (
        connect.execute(
            sa.text("""
            INSERT INTO movie_ratings (movie_id, user_id, notes, rating, status)
            VALUES (:movie_id, :user_id, '', NULL, 'want to watch') RETURNING id
        """),
            {"movie_id": movie_ids["A Minecraft Movie"], "user_id": joe_id},
        )
        .one()
        .id
    )
    joe_gwh = (
        connect.execute(
            sa.text("""
            INSERT INTO movie_ratings (movie_id, user_id, notes, rating, status)
            VALUES (:movie_id, :user_id, 'amazing cinematography', 5, 'watched') RETURNING id
        """),
            {"movie_id": movie_ids["Good Will Hunting"], "user_id": joe_id},
        )
        .one()
        .id
    )

    # Add Joe's ratings to his watchlist
    connect.execute(
        sa.text(
            "INSERT INTO watchlist_movie (watchlist_id, movie_rating_id) VALUES (:wl, :mr)"
        ),
        [
            {"wl": joe_watchlist, "mr": joe_minecraft},
            {"wl": joe_watchlist, "mr": joe_gwh},
        ],
    )

    # Step 4: Bob's ratings and watchlist additions
    bob_id = user_ids["Bob"]
    bob_watchlist = watchlist_ids["Bob"]
    bob_glad = (
        connect.execute(
            sa.text("""
            INSERT INTO movie_ratings (movie_id, user_id, notes, rating, status)
            VALUES (:movie_id, :user_id, 'nice', 6, 'watched') RETURNING id
        """),
            {"movie_id": movie_ids["Gladiator"], "user_id": bob_id},
        )
        .one()
        .id
    )
    bob_gwh = (
        connect.execute(
            sa.text("""
            INSERT INTO movie_ratings (movie_id, user_id, notes, rating, status)
            VALUES (:movie_id, :user_id, 'really good', 7, 'watched') RETURNING id
        """),
            {"movie_id": movie_ids["Good Will Hunting"], "user_id": bob_id},
        )
        .one()
        .id
    )

    # Add Bob's ratings to his watchlist
    connect.execute(
        sa.text(
            "INSERT INTO watchlist_movie (watchlist_id, movie_rating_id) VALUES (:wl, :mr)"
        ),
        [{"wl": bob_watchlist, "mr": bob_glad}, {"wl": bob_watchlist, "mr": bob_gwh}],
    )

    # Step 5: Alice's rating and watchlist addition
    alice_id = user_ids["Alice"]
    alice_watchlist = watchlist_ids["Alice"]
    alice_barbie = (
        connect.execute(
            sa.text("""
            INSERT INTO movie_ratings (movie_id, user_id, notes, rating, status)
            VALUES (:movie_id, :user_id, '', NULL, 'want to watch') RETURNING id
        """),
            {"movie_id": movie_ids["Barbie"], "user_id": alice_id},
        )
        .one()
        .id
    )

    # Add Alice's rating to her watchlist
    connect.execute(
        sa.text(
            "INSERT INTO watchlist_movie (watchlist_id, movie_rating_id) VALUES (:wl, :mr)"
        ),
        {"wl": alice_watchlist, "mr": alice_barbie},
    )

    # Step 6: Eve's ratings and watchlist additions
    eve_id = user_ids["Eve"]
    eve_watchlist = watchlist_ids["Eve"]
    eve_glad = (
        connect.execute(
            sa.text("""
            INSERT INTO movie_ratings (movie_id, user_id, notes, rating, status)
            VALUES (:movie_id, :user_id, 'nice', 6, 'watched') RETURNING id
        """),
            {"movie_id": movie_ids["Gladiator"], "user_id": eve_id},
        )
        .one()
        .id
    )
    eve_gwh = (
        connect.execute(
            sa.text("""
            INSERT INTO movie_ratings (movie_id, user_id, notes, rating, status)
            VALUES (:movie_id, :user_id, 'enjoyed', 7, 'watched') RETURNING id
        """),
            {"movie_id": movie_ids["Good Will Hunting"], "user_id": eve_id},
        )
        .one()
        .id
    )
    eve_barbie = (
        connect.execute(
            sa.text("""
            INSERT INTO movie_ratings (movie_id, user_id, notes, rating, status)
            VALUES (:movie_id, :user_id, 'inspiring', 7, 'watched') RETURNING id
        """),
            {"movie_id": movie_ids["Barbie"], "user_id": eve_id},
        )
        .one()
        .id
    )

    # Add Eve's ratings to her watchlist
    connect.execute(
        sa.text(
            "INSERT INTO watchlist_movie (watchlist_id, movie_rating_id) VALUES (:wl, :mr)"
        ),
        [
            {"wl": eve_watchlist, "mr": eve_glad},
            {"wl": eve_watchlist, "mr": eve_gwh},
            {"wl": eve_watchlist, "mr": eve_barbie},
        ],
    )


def downgrade() -> None:
    """Downgrade schema by removing inserted users, movies, and related entries."""
    connect = op.get_bind()

    # Remove all data related to this migration
    connect.execute(sa.text("DELETE FROM watchlist_movie"))
    connect.execute(sa.text("DELETE FROM movie_ratings"))
    connect.execute(sa.text("DELETE FROM watchlists"))
    connect.execute(
        sa.text("DELETE FROM users WHERE name IN ('Alice', 'Bob', 'Joe', 'Eve')")
    )
    connect.execute(
        sa.text(
            "DELETE FROM movies WHERE name IN ('A Minecraft Movie', 'Barbie', 'Good Will Hunting', 'Gladiator')"
        )
    )
