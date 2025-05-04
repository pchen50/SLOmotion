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
    prefix="/user",
    tags=["user"],
    dependencies=[Depends(auth.get_api_key)],
)

class Customer(BaseModel):
    customer_name: str

class UserCreateResponse(BaseModel):
    user_id: int

@router.post("/", response_model=UserCreateResponse)
def create_user(new_cart: Customer):
    pass # probably just insert into users and return an id
    # maybe also insert into watchlist? to create a user's watchlist and just default set status to public