from dataclasses import dataclass
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from typing import List
import sqlalchemy
from src.api import auth
from src import database as db
from sqlalchemy import exc

router = APIRouter(
    prefix="/watchlist",
    tags=["watchlist"],
    dependencies=[Depends(auth.get_api_key)],
)


class WatchlistMovie(BaseModel):
    watchlist_id: int
    movie_id: int
    name: str


class MovieRating(BaseModel):
    movie_id: int
    user_id: int
    notes: str
    rating: int
    status: str


@router.get("/{user_id}", response_model=List[WatchlistMovie])
def get_rated_movies(
    user_id: int,
) -> List[WatchlistMovie]:  # return list of rated movies
    # get their watchlist id from watchlists?
    with db.engine.begin() as connection:
        row = connection.execute(
            sqlalchemy.text(
                """ 
                        SELECT id, public
                        FROM watchlists
                        WHERE user_id = :user_id
                    """
            ),
            [{"user_id": user_id}],
        ).one()
        if row.public == False:
            return []
        watchlist_id = row.id
        # Then from that get all the movie_rating ids associated with watchlist id
        result = connection.execute(
            sqlalchemy.text(
                """
                    SELECT watchlist_id, movies.id as movie_id, movies.name as name
                    FROM watchlist_movie
                    JOIN movie_ratings on watchlist_movie.movie_rating_id = movie_ratings.id
                    JOIN movies on movie_ratings.movie_id = movies.id
                    WHERE watchlist_id = :watchlist_id
                """
            ),
            [{"watchlist_id": watchlist_id}],
        ).tuples()
        # for all movie rating ids return the movie_rating, movie_ids, and their names
        watchlist_movies = []
        for movie in result:
            watchlist_movies.append(
                WatchlistMovie(
                    watchlist_id=movie.watchlist_id,
                    movie_id=movie.movie_id,
                    name=movie.name,
                )
            )
        return watchlist_movies


@router.get("/{user_id}/{movie_id}", response_model=MovieRating)
def get_movie_rating(
    user_id: int, movie_id: int
) -> MovieRating:  # return a movie rating
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT movie_id, user_id, notes, rating, status
                FROM movie_ratings
                WHERE user_id = :user_id AND movie_id = :movie_id
                """
            ),
            {"user_id": user_id, "movie_id": movie_id},
        ).one_or_none()
        # if no result was found, raise a 404 HTTPException
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie rating not found for this user.",
            )
        # if result is found, return it as a MovieRating response model
        return MovieRating(
            movie_id=result.movie_id,
            user_id=result.user_id,
            notes=result.notes,
            rating=result.rating,
            status=result.status,
        )


@router.post(
    "/watchlist/{user_id}/{movie_id}/{user2_id}/comment",
    status_code=status.HTTP_204_NO_CONTENT,
)
def post_comment_on_movie_rating(user_id: int, movie_id: int, user2_id: int):
    pass
    # update into comments table
