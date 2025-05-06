# Example Work Flow 
## Watchlist User Makes a Comment Example Flow
Bob just finished watching *Good Will Hunting* for a second time and had some thoughts about the movie. He wants to leave a comment on his friend Joe's watchlist.

- Bob calls `GET /watchlist/876543` to see Joe’s recently watched list.
- He sees *Good Will Hunting* under `movie_id tt1417298`.
- He then calls `GET /watchlist/876543/tt1417298` to view the movie entry.
- Bob submits a comment with:
  ```json
  {
    "comment": "I really connected with the character Will in the movie."
  }
  ```
- Request: `POST /watchlist/876543/tt1417298/1391810/comment`
- Server response:
  ```json
  { "message": "Comment added." }
  ```
## Testing results
- Bob calls (Joe's id is 3):
  curl -X 'GET' \
  'https://slomotion.onrender.com/watchlist/3' \
  -H 'accept: application/json' \
  -H 'access_token: SLOmotion44'
- what's returned is
  [
  {
    "watchlist_id": 3,
    "movie_id": 3,
    "name": "Minecraft"
  },
  {
    "watchlist_id": 3,
    "movie_id": 1,
    "name": "Good Will Hunting"
  }
]

## Get Movie Rating by User

### `GET /watchlist/{user_id}/{movie_id}`
Bob wants to check the rating he gave to *Good Will Hunting*.

- Bob knows:
  - `user_id = 1`
  - `movie_id = 1`

- He sends a request to:
```bash
GET /watchlist/1/1
```

- The server returns his review, rating, and status.
  ```json
  {
  "user_id": 1,
  "movie_id": 1,
  "notes": "Amazing cinematography.",
  "rating": 5,
  "status": "watched"
  }
  ```

- If the input is invalid or missing, the server responds with:
  ```json
  {
    "detail": "Movie rating not found for this user."
  }
  ```
  

