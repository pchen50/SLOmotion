## 2. Watchlist User Looks for a Movie to Watch Example Flow
Alice finishes watching *Barbie* and updates its status in her watchlist. She then checks Bob's watchlist and finally gets new recommendations for herself.

- Alice calls `PATCH /watchlist/456219/tt1517268`
  ```json
  {
    "user_id": "456219",
    "movie_id": "tt1517268",
    "status": "watched",
    "rating": 8
  }
  ```
- Server response:
  ```json
  { "message": "Successfully updated!" }
  ```
- Alice calls `GET /watchlist/876543/watched`
  ```json
  {
    "user_id": "876543",
    "status": "watched"
  }
  ```
- Server response:
 ```json
 [
   {
      "movie_id": "tt1517268",
      "title": "Gladiator",
      "status": "watched",
      "rating": "9.8",
      "genre": "action"
    },
    {
      "movie_id": "tt1417298",
      "title": "Good Will Hunting",
      "status": "watched",
      "rating": "9.7",
      "genre": "drama"
    }
 ]
``` 
- She then calls `GET /recommended_movies/456219` to receive personalized recommendations.

## Testing results for flow 2

To check Bob's watchlist she calls `GET /watchlist/5/watched` since Bob's user_id is 5.

curl -X 'GET' \
  'https://slomotion.onrender.com/watchlist/5/watched' \
  -H 'accept: application/json' \
  -H 'access_token: SLOmotion44'

Server response:
  ```json
  [
    {
      "movie_id": 6,
      "name": "The Dark Knight",
      "genre": "Action"
    },
    {
      "movie_id": 10,
      "name": "The Lord of the Rings: The Return of the King",
      "genre": "Action"
    },
    {
      "movie_id": 12,
      "name": "The Lord of the Rings: The Fellowship of the Ring",
      "genre": "Action"
    },
    {
      "movie_id": 16,
      "name": "The Lord of the Rings: The Two Towers",
      "genre": "Action"
    },
    {
      "movie_id": 17,
      "name": "Inception",
      "genre": "Action"
    }
  ]
  ```

## 3. Watchlist User Adds and Removes Movies Example Flow
Eve gets a recommendation to watch *A Minecraft Movie*, but later changes her mind.

- Eve calls `GET /ratings/tt3566834` and sees strong user ratings.
- She adds the movie using `POST /watchlist/376541/tt3566834`
  ```json
  {
    "user_id": "376541",
    "movie_id": "tt3566834",
    "status": "want to watch"
  }
  ```
- After watching, Eve decides to remove it using:
  `DELETE /watchlist/376541/tt3566834`
- Server responds:
  ```json
  { "Message": "Successfully removed movie." }
  ```

## Testing results for flow 3


## 4. Get User's Recommendations
Joe finishes watching Good Will Hunting and wants to find more movies he'll enjoy based on his watchlist history.

- Joe calls `GET /recommended_movies/6` (User ID 6 belongs to Joe)
- Server response
  ```json
    [
      {
        "movie_id": 13,
        "name": "The Good, the Bad and the Ugly",
        "genre": "Adventure"
      },
      {
        "movie_id": 28,
        "name": "Interstellar",
        "genre": "Adventure"
      },
      {
        "movie_id": 33,
        "name": "Back to the Future",
        "genre": "Adventure"
      },
      {
        "movie_id": 74,
        "name": "Inglourious Basterds",
        "genre": "Adventure"
      },
      {
        "movie_id": 94,
        "name": "2001: A Space Odyssey",
        "genre": "Adventure"
      }
    ]
  
  ```
- The server returns 5 movies from the genre Adventure, which is tied for the most common in Joe’s watchlist. Since Adventure appears first when counts are tied (alphabetical or order by default), those recommendations are selected.

