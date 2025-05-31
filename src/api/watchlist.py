from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from typing import List, Literal
import sqlalchemy
from src.api import auth
from src import database as db

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
    rating: int | None = None
    status: Literal["watched", "want to watch", "watching"]


class WatchedMovie(BaseModel):
    movie_id: int
    title: str
    status: str
    rating: int
    genre: str


class AddToWatchlist(BaseModel):
    rating: int | None = None
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


@router.get("/{user_id}/stats", response_model=WatchlistStats)
def get_user_stats(user_id: int):
    print(user_id)
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
    print(user_id)
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
            print(movie)
            watched_movies.append(
                WatchedMovie(
                    movie_id=movie.movie_id,
                    title=movie.name,
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

    return {"message": "Comment added."}


@router.patch("/{user_id}/{movie_id}", status_code=status.HTTP_200_OK)
def update_watchlist_movie_entry(user_id: int, movie_id: int, update: MovieRating):
    # Updates a user's description/rating for a movie in their watchlist

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                UPDATE movie_ratings
                SET notes = :notes, rating = :rating, status = :status
                WHERE user_id = :user_id AND movie_id = :movie_id"""
            ),
            {
                "user_id": user_id,
                "movie_id": movie_id,
                "notes": update.notes,
                "rating": update.rating,
                "status": update.status,
            },
        )

        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie rating not found for this user.",
            )

    return {"message": "Successfully updated!"}


@router.post("/{user_id}/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
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
        result = connection.execute(
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
