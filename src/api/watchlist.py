from dataclasses import dataclass
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import List
import random
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
def create_user(user_id: int) -> List[WatchlistMovie]: # return list of rated movies
    pass 
    # get their watchlist id from watchlists?
    # Then from that get all the movie_rating ids associated with watchlist id
    # for all movie rating ids return the movie_rating, movie_ids, and their names

@router.get("/{user_id}/{movie_id}", response_model=MovieRating)
def get_movie_rating(user_id: int, movie_id:int) -> MovieRating: # return a movie rating
    pass 
    # from user_id and movie_id return the movie rating

@router.post("/watchlist/{user_id}/{movie_id}/{user2_id}/comment", status_code=status.HTTP_204_NO_CONTENT)
def post_comment_on_movie_rating(user_id: int, movie_id:int, user2_id:int): 
    pass 
    # update into comments table