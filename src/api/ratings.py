from fastapi import APIRouter, Depends, status, HTTPException
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
    movie_id: int
    status: str
    rating: int
    notes: str

@router.get("/{movie_id}", response_model=List[Rating])
def get_movie_ratings(movie_id: int) -> List[Rating]:
    pass