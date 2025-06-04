from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal
import sqlalchemy
from src.api import auth
from src import database as db
from sqlalchemy.exc import IntegrityError
from pydantic import Field


router = APIRouter(
    prefix="/watchlist",
    tags=["watchlist"],
    dependencies=[Depends(auth.get_api_key)],
)


class WatchlistMovie(BaseModel):
    user_id: int
    movie_id: int
    name: str
    status: str


class MovieRating(BaseModel):
    movie_id: int
    user_id: int
    notes: str
    rating: float | None = None
    status: Literal["watched", "want to watch", "watching"]


class WatchedMovie(BaseModel):
    movie_id: int
    name: str
    status: str
    rating: float
    genre: str


class AddToWatchlist(BaseModel):
    # ge = greater than or equal to
    # le = less than or equal to
    rating: float | None = Field(
        default=None, ge=1, le=10, description="Rating must be between 1 and 10."
    )
    notes: str | None = None
    status: Literal["watched", "want to watch", "watching"]


class RecentNotes(BaseModel):
    movie1: str | None = None
    movie2: str | None = "n/a"
    movie3: str | None = "n/a"


class WatchlistStats(BaseModel):
    user_id: int
    watchedMovieCount: int
    wantToWatchMovieCount: int
    watchingMovieCount: int
    totalGenres: dict[str, str]
    recentNotes: RecentNotes
    averageRating: float


class MovieRatingUpdate(BaseModel):
    notes: str | None = Field(None, example=None)
    rating: float | None = None
    status: Literal["watched", "want to watch", "watching"] | None = None


class Comment(BaseModel):
    commenter_user_id: int
    commenter_username: str
    comment_text: str


@router.get("/{user_id}/stats", response_model=WatchlistStats)
def get_user_stats(user_id: int):
    print(user_id)       # should this be removed?      
    with db.engine.begin() as connection:
        movies = connection.execute(
            sqlalchemy.text(
                """ 
                    SELECT movie_id, user_id, notes, rating, status, name, genre
                    FROM movie_ratings
                    JOIN movies on movies.id = movie_ratings.movie_id
                    WHERE user_id = :user_id
                    ORDER BY movie_ratings.id DESC
                """
            ),
            [{"user_id": user_id}],
        ).tuples()
        watchedCount = 0
        wantToWatch = 0
        watching = 0
        genres = {}
        all_ratings = []
        notes = {}
        for movie in movies:
            if movie.status == "want to watch":
                wantToWatch += 1
            elif movie.status == "watching":
                watching += 1
            elif movie.status == "watched":
                watchedCount += 1
                all_ratings.append(movie.rating)
                if watchedCount <= 3 and movie.notes:
                    notes[f"movie{watchedCount}"] = movie.name + ": " + movie.notes
            if movie.genre in genres:
                genres[movie.genre] += ", " + movie.name
            else:
                genres[movie.genre] = movie.name

        if watchedCount + wantToWatch + watching == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No watchlist movies found for the user",
            )
        movieNotes = RecentNotes()
        for i, notes in notes.items():
            setattr(movieNotes, i, notes)
        return WatchlistStats(
            user_id=user_id,
            watchedMovieCount=watchedCount,
            wantToWatchMovieCount=wantToWatch,
            recentNotes=movieNotes,
            watchingMovieCount=watching,
            totalGenres=genres,
            averageRating=round(sum(all_ratings) / watchedCount, 2),
        )


@router.get("/{user_id}/watched", response_model=List[WatchedMovie])
def get_watched(user_id: int) -> List[WatchedMovie]:
    print(user_id)       # should this be removed?
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                    SELECT movie_id, movies.name as name, movie_ratings.status as status, movie_ratings.rating as rating, movies.genre as genre
                    FROM movie_ratings
                    JOIN movies on movie_ratings.movie_id = movies.id
                    WHERE user_id = :user_id and status = 'watched'
                """
            ),
            [{"user_id": user_id}],
        ).tuples()
        # for all movie rating ids return the movie_rating, movie_ids, and their names
        watched_movies = []
        for movie in result:
            print(movie)            # should this be removed?
            watched_movies.append(
                WatchedMovie(
                    movie_id=movie.movie_id,
                    name=movie.name,
                    status=movie.status,
                    rating=movie.rating,
                    genre=movie.genre,
                )
            )
        return watched_movies


@router.get("/{user_id}", response_model=List[WatchlistMovie])
def get_watchlist_movies(
    user_id: int,
) -> List[WatchlistMovie]:  # return list of movies on user's watchlist
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                    SELECT movies.id as movie_id, movies.name as name, status
                    FROM movie_ratings
                    JOIN movies on movie_ratings.movie_id = movies.id
                    WHERE user_id = :user_id
                """
            ),
            [{"user_id": user_id}],
        ).tuples()
        # for all movie rating ids return the movie_rating, movie_ids, and their names
        watchlist_movies = []
        for movie in result:
            watchlist_movies.append(
                WatchlistMovie(
                    user_id=user_id,
                    movie_id=movie.movie_id,
                    name=movie.name,
                    status=movie.status,
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


class CommentInput(BaseModel):
    comment_text: str


@router.post(
    "/{user_id}/{movie_id}/{user2_id}/comment", status_code=status.HTTP_204_NO_CONTENT
)
def post_comment_on_movie_rating(
    user_id: int, movie_id: int, user2_id: int, comment: CommentInput
):
    with db.engine.begin() as connection:
        rating = connection.execute(
            sqlalchemy.text(
                """
            SELECT 1
            FROM movie_ratings
            WHERE user_id = :user_id AND movie_id = :movie_id
            """
            ),
            {"user_id": user_id, "movie_id": movie_id},
        ).one_or_none()

        if rating is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie or user does not exist.",
            )

        # insert comment
        try:
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO comments (commenter_user_id, user_id, movie_id, comment_text)
                    VALUES (:commenter_user_id, :user_id, :movie_id, :comment_text)
                    """
                ),
                {
                    "commenter_user_id": user2_id,
                    "user_id": user_id,
                    "movie_id": movie_id,
                    "comment_text": comment.comment_text,
                },
            )
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A comment from this user already exists on this rating.",
            )

    return {"message": "Comment added."}


@router.patch("/{user_id}/{movie_id}", status_code=status.HTTP_200_OK)
def update_watchlist_movie_entry(
    user_id: int, movie_id: int, update: MovieRatingUpdate
):
    # Updates a user's description/rating for a movie in their watchlist
    # add null in request body to not update a field

    fields = []
    values = {"user_id": user_id, "movie_id": movie_id}

    if update.notes is not None:
        fields.append("notes = :notes")
        values["notes"] = update.notes
    if update.rating is not None:
        values["rating"] = update.rating
        fields.append("rating = :rating")
    if update.status is not None:
        values["status"] = update.status
        fields.append("status = :status")

    if not fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update provided.",
        )

    with db.engine.begin() as connection:
        # check if user exists first
        user_exists = connection.execute(
            sqlalchemy.text("SELECT id FROM users WHERE id = :user_id"),
            {"user_id": user_id},
        ).one_or_none()

        if user_exists is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this ID does not exist.",
            )

        # proceed with the update
        result = connection.execute(
            sqlalchemy.text(
                f"""
                UPDATE movie_ratings
                SET {", ".join(fields)}
                WHERE user_id = :user_id AND movie_id = :movie_id
                RETURNING id
                """
            ),
            values,
        )

        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie rating not found for this user and movie.",
            )

    return {"message": "Successfully updated!"}


@router.post("/{user_id}/{movie_id}", status_code=status.HTTP_201_CREATED)
def post_movie_onto_watchlist(user_id: int, movie_id: int, movie: AddToWatchlist):
    # posts in movie ratings but in movie ratings it won't have rating or notes?

    # check if movie already exists in watchlist
    with db.engine.begin() as connection:
        exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT id 
                FROM movie_ratings
                WHERE user_id = :user_id AND movie_id = :movie_id
                """
            ),
            {"user_id": user_id, "movie_id": movie_id},
        ).one_or_none()

        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Movie already exists in watchlist.",
            )

        # if it doesn't exist, insert into movie ratings table
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO movie_ratings (user_id, movie_id, notes, rating, status)
                VALUES (:user_id, :movie_id, :notes, :rating, :status)
                RETURNING id
                """
            ),
            {
                "user_id": user_id,
                "movie_id": movie_id,
                "notes": movie.notes or "N/A",
                "rating": movie.rating if movie.rating is not None else None,
                "status": movie.status,
            },
        )

    return {"message": "Successfully added movie to watchlist."}


@router.delete("/{user_id}/{movie_id}", status_code=status.HTTP_200_OK)
def delete_users_movie_entry(user_id: int, movie_id: int):
    # delete from movie ratings, and any comments on it

    # gets movie rating id from movie ratings table
    with db.engine.begin() as connection:
        rating = connection.execute(
            sqlalchemy.text(
                """
                SELECT id 
                FROM movie_ratings
                WHERE user_id = :user_id AND movie_id = :movie_id
                """
            ),
            {"user_id": user_id, "movie_id": movie_id},
        ).one_or_none()

        if rating is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie rating not found for this user and movie.",
            )

        movie_rating_id = rating.id

        # delete comments linked to the movie rating
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM comments
                WHERE user_id = :user_id AND movie_id = :movie_id
                """
            ),
            {"user_id": user_id, "movie_id": movie_id},
        )

        # delete from movie ratings table
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM movie_ratings
                WHERE id = :movie_rating_id
                """
            ),
            {"movie_rating_id": movie_rating_id},
        )

    return {"message": "Successfully removed movie."}


@router.get("/{user_id}/{movie_id}/comments", response_model=List[Comment])
def get_comments(user_id: int, movie_id: int):
    # get the commenters user id, their username, and the comment text
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT c.commenter_user_id, u.username AS commenter_username, c.comment_text
                FROM comments c
                JOIN users u ON c.commenter_user_id = u.id
                WHERE c.user_id = :user_id AND c.movie_id = :movie_id
                ORDER BY c.id DESC
                """
            ),
            {"user_id": user_id, "movie_id": movie_id},
        ).fetchall()

        # return the list of comments as comment models
        # each user can only leave one comment on a movie so there are no repeats
        return [
            Comment(
                commenter_user_id=row.commenter_user_id,
                commenter_username=row.commenter_username,
                comment_text=row.comment_text,
            )
            for row in result
        ]
