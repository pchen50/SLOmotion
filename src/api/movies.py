from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from typing import List
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/movies",
    tags=["movies"],
    dependencies=[Depends(auth.get_api_key)],
)


class Rating(BaseModel):
    user_id: int
    rating: int | None


class MovieId(BaseModel):
    movie_id: int


@router.get("/{movie_name}", response_model=MovieId)
def get_movie_id(movie_name: str, year: int = None):
    metadata_obj = sqlalchemy.MetaData()
    movies = sqlalchemy.Table("movies", metadata_obj, autoload_with=db.engine)
    stmt = sqlalchemy.select(movies.c.id).select_from(movies)
    if year:
        stmt = stmt.where(
            (movies.c.name.ilike(f"{movie_name}")), (movies.c.year == year)
        )
    else:
        stmt = stmt.where((movies.c.name.ilike(f"{movie_name}")))
    with db.engine.connect() as connection:
        results = connection.execute(stmt).fetchall()

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found in database. Please check the spelling and try again.",
            )
        
        if len(results) > 1:
            # if there are multiple matches for a movie, ask for the year
            if year is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Multiple movies found with this name. Please specify the year by adding ?year=YYYY to the URL (e.g. /movies/The%20Godfather?year=1972)",
                )
            # somethings wrong if multiple matches for movie and year
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Multiple movies found with this name and year. This should not happen - please contact support.",
                )

        return MovieId(movie_id=results[0].id)


@router.get("/ratings/{movie_id}", response_model=List[Rating])
def get_movie_ratings(movie_id: int) -> List[Rating]:
    with db.engine.connect() as conn:
        results = (
            conn.execute(
                sqlalchemy.text(
                    """
            SELECT user_id, rating
            FROM movie_ratings
            WHERE movie_id = :movie_id
            """
                ),
                {"movie_id": movie_id},
            )
            .mappings()
            .all()
        )

        ratings = []
        for row in results:
            ratings.append(Rating(user_id=row.user_id, rating=row.rating))

        return ratings
