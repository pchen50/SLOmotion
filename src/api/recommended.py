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
    pass
    # if user doesn't exist raise an error
    # if user doesn't have anything on watchlist return first five movies
    # otherwise go off of top genre and return 5 movies from that genre