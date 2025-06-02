from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/ratings",
    tags=["ratings"],
    dependencies=[Depends(auth.get_api_key)],
)

class Rating(BaseModel):
    user_id: int
    rating: int | None = None    # <-- union type with default None

@router.get("/{movie_id}", response_model=List[Rating])
def get_movie_ratings(movie_id: int) -> List[Rating]:
    with db.engine.connect() as conn:
        results = conn.execute(sqlalchemy.text(
            """
            SELECT user_id, rating
            FROM movie_ratings
            WHERE movie_id = :movie_id
            """
        ), {"movie_id": movie_id}).mappings().all()

        return [
            Rating(
                user_id=row.user_id,
                rating=row.rating  # if row.rating is NULL, this is None
            )
            for row in results
        ]
