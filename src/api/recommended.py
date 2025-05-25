from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from typing import List
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/recommended_movies",
    tags=["recommended"],
    dependencies=[Depends(auth.get_api_key)],
)


class Movie(BaseModel):
    movie_id: int
    name: str
    genre: str


@router.get("/{user_id}", response_model=List[Movie])
def get_recommended_movies(user_id: int) -> List[Movie]:
    with db.engine.connect() as conn:
        # Check if user exists
        result = conn.execute(
            sqlalchemy.text("SELECT id FROM users WHERE id = :user_id"),
            {"user_id": user_id},
        ).fetchone()

        if result is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Get user's most common genre from watchlist
        watchlist = conn.execute(
            sqlalchemy.text(
                """
                SELECT m.genre
                FROM watchlists w
                JOIN watchlist_movie wm ON w.id = wm.watchlist_id
                JOIN movie_ratings mr ON wm.movie_rating_id = mr.id
                JOIN movies m ON mr.movie_id = m.id
                WHERE w.user_id = :user_id
                GROUP BY m.genre
                ORDER BY COUNT(*) DESC
                LIMIT 1
                """
            ),
            {"user_id": user_id},
        ).fetchone()

        if watchlist is None:
            # No watchlist: return first 5 movies
            movies = (
                conn.execute(
                    sqlalchemy.text(
                        "SELECT id AS movie_id, name, genre FROM movies LIMIT 5"
                    )
                )
                .mappings()
                .all()
            )
        else:
            # Get most common genre
            top_genre = watchlist.genre

            # Return 5 movies from top genre that are not in the user's watchlist
            movies = (
                conn.execute(
                    sqlalchemy.text(
                        """
                    SELECT m.id AS movie_id, m.name, m.genre
                    FROM movies m
                    WHERE m.genre = :genre 
                     AND m.id NOT IN ( 
                        SELECT mr.movie_id
                        FROM movie_ratings mr
                        WHERE mr.user_id = :user_id)
                    ORDER BY RANDOM()
                    LIMIT 5
                    """
                    ),
                    {"genre": top_genre, "user_id": user_id},
                )
                .mappings()
                .all()
            )

        return [Movie(**row) for row in movies]
