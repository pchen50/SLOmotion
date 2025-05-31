from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[Depends(auth.get_api_key)],
)


class Customer(BaseModel):
    customer_name: str
    username: str  # new field to distinguish users by unique id


class UserCreateResponse(BaseModel):
    user_id: int


class UserInfo(BaseModel):
    # response model for /login/{user_id}
    user_id: int
    name: str
    username: str


@router.post("/", response_model=UserCreateResponse)
def create_user(new_cart: Customer):
    try:
        with db.engine.begin() as connection:
            # insert user with username and name
            result = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO users (name, username)
                    VALUES (:customer_name, :username)
                    RETURNING id
                    """
                ),
                {
                    "customer_name": new_cart.customer_name,
                    "username": new_cart.username,
                },
            )
            user_id = result.scalar_one()

            if user_id is None:
                raise HTTPException(status_code=500, detail="Failed to create user")

            return UserCreateResponse(user_id=int(user_id))

    # handle cases where username already exists
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already taken.")
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


# new endpoint to look up user id by username
@router.get("/lookup/{username}", response_model=UserCreateResponse)
def get_user_by_username(username: str):
    with db.engine.connect() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM users
                WHERE username = :username
                """
            ),
            {"username": username},
        ).one_or_none()

        if result is None:
            raise HTTPException(status_code=404, detail="Username not found")

        return UserCreateResponse(user_id=result.id)


# new end point for login to return name nad username from user id
@router.get("/login/{user_id}", response_model=UserInfo)
def login_user(user_id: int):
    with db.engine.connect() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT id AS user_id, name, username
                FROM users
                WHERE id = :user_id
                """
            ),
            {"user_id": user_id},
        ).one_or_none()

        if result is None:
            raise HTTPException(status_code=404, detail="User not found")

        return UserInfo(**result._mapping)
